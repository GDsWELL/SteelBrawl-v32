namespace Supercell.Laser.Server.Networking.Session
{
    using Supercell.Laser.Logic.Friends;
    using Supercell.Laser.Logic.Home;
    using Supercell.Laser.Logic.Listener;
    using Supercell.Laser.Logic.Message.Account;
    using Supercell.Laser.Logic.Message.Account.Auth;
    using Supercell.Laser.Logic.Message.Friends;
    using Supercell.Laser.Logic.Util;
    using Supercell.Laser.Server.Logic.Game;
    using System.Collections.Concurrent;

    public static class Sessions
    {
        public static bool Maintenance;

        public static ConcurrentDictionary<long, Session> ActiveSessions = new ConcurrentDictionary<long, Session>();
        public static Dictionary<string, string> RequestedSSID;
        public static Dictionary<string, List<string>> LeaveJoin;
        public static Dictionary<string, string> RegistratedSSID;


        public static int Count
        {
            get
            {
                return ActiveSessions.Count;
            }
        }

        public static void Init()
        {
            ActiveSessions = new ConcurrentDictionary<long, Session>();
            RequestedSSID = new();
            RegistratedSSID = new();
            LeaveJoin = new();
        }

        public static void StartShutdown()
        {
            Maintenance = true;
            foreach (var session in ActiveSessions.Values.ToArray())
            {
                session.Connection.Send(new ShutdownStartedMessage());
                session.Connection.Avatar.BattleStartTime = new DateTime();
            }

            Thread.Sleep(1000 * 10);

            foreach (var session in ActiveSessions.Values.ToArray())
            {
                session.Connection.Send(new AuthenticationFailedMessage()
                {
                    ErrorCode = 10,
                });
            }
        }

        public static void Remove(long id)
        {
            if (ActiveSessions.ContainsKey(id))
            {
                RequestedSSID.Remove(LogicLongCodeGenerator.ToCode(ActiveSessions[id].Home.Avatar.AccountId));
                RegistratedSSID.Remove(LogicLongCodeGenerator.ToCode(ActiveSessions[id].Home.Avatar.AccountId));
                ActiveSessions[id].Home.Avatar.LastOnline = DateTime.UtcNow;
                ActiveSessions[id].Home.Avatar.PlayerStatus = 0;

                FriendOnlineStatusEntryMessage entryMessage = new FriendOnlineStatusEntryMessage();
                entryMessage.AvatarId = ActiveSessions[id].Home.Avatar.AccountId;
                entryMessage.PlayerStatus = 0;

                foreach (Friend friend in ActiveSessions[id].Home.Avatar.Friends.ToArray())
                {
                    if (LogicServerListener.Instance.IsPlayerOnline(friend.AccountId))
                    {
                        LogicServerListener.Instance.GetGameListener(friend.AccountId).SendTCPMessage(entryMessage);
                    }
                }

                if (ActiveSessions[id].Home.Avatar.TeamId > 0)
                {
                    var team = Teams.Get(ActiveSessions[id].Home.Avatar.TeamId);
                    if (team != null)
                    {
                        var member = team.GetMember(id);
                        if (member != null)
                        {
                            member.State = 0;
                            team.TeamUpdated();
                        }
                    }
                }
            }
            ActiveSessions.Remove(id, out _);
        }

        public static Session Create(HomeMode home, Connection connection)
        {
            if (ActiveSessions.ContainsKey(home.Avatar.AccountId))
            {
                Session oldSession = ActiveSessions[home.Avatar.AccountId];
                oldSession.Connection.Send(new DisconnectedMessage()
                {
                    Reason = 1
                });

                Session s = new Session(home, connection);
                ActiveSessions[home.Avatar.AccountId] = s;
                return s;
            }

            Session session = new Session(home, connection);
            ActiveSessions[home.Avatar.AccountId] =  session;
            return session;
        }

        public static bool IsSessionActive(long id)
        {
            return ActiveSessions.ContainsKey(id);
        }

        public static Session GetSession(long id)
        {
            if (ActiveSessions.ContainsKey(id))
            {
                return ActiveSessions[id];
            }
            return null;
        }
    }
}
