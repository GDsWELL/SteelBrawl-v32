namespace Supercell.Laser.Server.Networking
{
    using Supercell.Laser.Server.Networking.Session;
    using System.Collections.Generic;
    using System;
    using System.Net;
    using System.Net.Sockets;
    using System.Threading;
    using System.Diagnostics;

    public static class TCPGateway
    {
        private static List<Connection> ActiveConnections;
        private static Dictionary<string, PacketCounter> PacketCounters;
        private static Dictionary<string, ConnectionAttemptCounter> ConnectionAttempts;

        private static Socket Socket;
        private static Thread Thread;
        private static Timer CleanupTimer;

        private static ManualResetEvent AcceptEvent;
        private static readonly object ConnectionLock = new object();

        public static void Init(string host, int port)
        {
            ActiveConnections = new List<Connection>();
            PacketCounters = new Dictionary<string, PacketCounter>();
            ConnectionAttempts = new Dictionary<string, ConnectionAttemptCounter>();

            Socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            Socket.Bind(new IPEndPoint(IPAddress.Parse(host), port));
            Socket.Listen(99999999);

            AcceptEvent = new ManualResetEvent(false);

            Thread = new Thread(Update);
            Thread.Start();

            CleanupTimer = new Timer(CleanupInactiveConnections, null, 10000, 10000);

            Logger.Print($"TCP сервер запущен на {host}:{port}");
        }

        private static void Update()
        {
            while (true)
            {
                AcceptEvent.Reset();
                Socket.BeginAccept(new AsyncCallback(OnAccept), null);
                AcceptEvent.WaitOne();
            }
        }

        private static void OnAccept(IAsyncResult ar)
        {
            try
            {
                Socket client = Socket.EndAccept(ar);
                string clientIp = ((IPEndPoint)client.RemoteEndPoint).Address.ToString();

                Logger.Print($"Попытка подключения от {clientIp}");

                lock (ConnectionLock)
                {
                    var existingConnection = ActiveConnections.Find(c =>
                        c.Socket != null && c.Socket.Connected &&
                        ((IPEndPoint)c.Socket.RemoteEndPoint).Address.ToString() == clientIp);

                    if (existingConnection != null)
                    {
                        Logger.Print($"Отклонено: уже существует активное соединение с {clientIp}");
                        client.Close(); // Закрываем новое соединение
                        return;
                    }
                }

                if (!ConnectionAttempts.ContainsKey(clientIp))
                {
                    ConnectionAttempts[clientIp] = new ConnectionAttemptCounter();
                }

                var attemptCounter = ConnectionAttempts[clientIp];
                attemptCounter.AttemptCount++;
                if ((DateTime.Now - attemptCounter.FirstAttemptTime).TotalSeconds > 10)
                {
                    attemptCounter.FirstAttemptTime = DateTime.Now;
                    attemptCounter.AttemptCount = 1;
                }

                if (attemptCounter.AttemptCount > 3)
                {
                    BanIp(clientIp);
                    Logger.Print($"IP {clientIp} заблокирован за слишком частые попытки подключения.");
                    return;
                }

                if (!PacketCounters.ContainsKey(clientIp))
                {
                    PacketCounters[clientIp] = new PacketCounter();
                }

                Connection connection = new Connection(client);
                lock (ConnectionLock)
                {
                    ActiveConnections.Add(connection);
                }
                Logger.Print($"Новое подключение от {clientIp}");

                Connections.AddConnection(connection);
                client.BeginReceive(connection.ReadBuffer, 0, 1024, SocketFlags.None, new AsyncCallback(OnReceive), connection);
            }
            catch (Exception ex)
            {
                Logger.Print($"Ошибка при приеме подключения: {ex.Message}\n{ex.StackTrace}");
            }
            finally
            {
                AcceptEvent.Set();
            }
        }

        private static void OnReceive(IAsyncResult ar)
        {
            Connection connection = (Connection)ar.AsyncState;
            if (connection == null || connection.Socket == null || !connection.Socket.Connected)
                return;

            string clientIp = ((IPEndPoint)connection.Socket.RemoteEndPoint).Address.ToString();

            try
            {
                int r = connection.Socket.EndReceive(ar);
                if (r <= 0)
                {
                    Logger.Print($"{clientIp} отключился.");
                    RemoveConnection(connection);
                    return;
                }

                if (PacketCounters.ContainsKey(clientIp))
                {
                    var counter = PacketCounters[clientIp];
                    counter.PacketCount++;
                    if ((DateTime.Now - counter.FirstPacketTime).TotalSeconds > 10)
                    {
                        counter.FirstPacketTime = DateTime.Now;
                        counter.PacketCount = 1;
                    }

                    if (counter.PacketCount > 50)
                    {
                        BanIp(clientIp);
                        Logger.Print($"IP {clientIp} заблокирован за превышение лимита пакетов.");
                        RemoveConnection(connection);
                        return;
                    }
                }

                connection.Memory.Write(connection.ReadBuffer, 0, r);
                connection.UpdateLastActiveTime();

                if (connection.Messaging.OnReceive() != 0)
                {
                    RemoveConnection(connection);
                    Logger.Print($"{clientIp} отключился.");
                    return;
                }
                connection.Socket.BeginReceive(connection.ReadBuffer, 0, 1024, SocketFlags.None, new AsyncCallback(OnReceive), connection);
            }
            catch (ObjectDisposedException)
            {
                Logger.Print($"Сокет клиента {clientIp} уже был закрыт.");
            }
            catch (SocketException)
            {
                RemoveConnection(connection);
                Logger.Print($"{clientIp} отключился из-за ошибки сокета.");
            }
            catch (Exception exception)
            {
                Logger.Print($"Неожиданная ошибка от {clientIp}: {exception.Message}");
                RemoveConnection(connection);
            }
        }

        private static void CleanupInactiveConnections(object state)
        {
            DateTime now = DateTime.Now;
            var connectionsToRemove = new List<Connection>();

            lock (ConnectionLock)
            {
                for (int i = ActiveConnections.Count - 1; i >= 0; i--)
                {
                    var connection = ActiveConnections[i];

                    if (connection != null && connection.Socket != null)
                    {
                        if (connection.Socket.Connected)
                        {
                            if ((now - connection.LastActiveTime).TotalSeconds > 120)
                            {
                                Logger.Print($"Закрытие неактивного соединения от {connection.Socket.RemoteEndPoint}.");
                                connectionsToRemove.Add(connection);
                            }
                        }
                        else
                        {
                            Logger.Print($"Сокет для соединения уже закрыт и будет удален.");
                            connectionsToRemove.Add(connection);
                        }
                    }
                    else
                    {
                        Logger.Print("Соединение или его сокет равны null, удаляем.");
                        connectionsToRemove.Add(connection);
                    }
                }

                foreach (var conn in connectionsToRemove)
                {
                    ActiveConnections.Remove(conn);
                    conn.Close();
                }
            }
        }

        private static void RemoveConnection(Connection connection)
        {
            lock (ConnectionLock)
            {
                if (ActiveConnections.Contains(connection))
                {
                    ActiveConnections.Remove(connection);
                }
                connection.Close();
                if (connection.MessageManager.HomeMode != null)
                {
                    Sessions.Remove(connection.Avatar.AccountId);
                }
            }
        }

        public static void OnSend(IAsyncResult ar)
        {
            try
            {
                Socket socket = (Socket)ar.AsyncState;
                socket.EndSend(ar);
            }
            catch (Exception ex)
            {
                Logger.Print($"Ошибка при отправке данных: {ex.Message}");
            }
        }

        private static void BanIp(string ip)
        {
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "/bin/bash",
                Arguments = $"-c \"iptables -A INPUT -s {ip} -j DROP\"",
                RedirectStandardOutput = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            Process.Start(psi);
        }
    }

    public class PacketCounter
    {
        public DateTime FirstPacketTime { get; set; }
        public int PacketCount { get; set; }

        public PacketCounter()
        {
            FirstPacketTime = DateTime.Now;
            PacketCount = 0;
        }
    }

    public class ConnectionAttemptCounter
    {
        public DateTime FirstAttemptTime { get; set; }
        public int AttemptCount { get; set; }

        public ConnectionAttemptCounter()
        {
            FirstAttemptTime = DateTime.Now;
            AttemptCount = 0;
        }
    }
}
