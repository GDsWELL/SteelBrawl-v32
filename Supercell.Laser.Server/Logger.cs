namespace Supercell.Laser.Server
{
    using Supercell.Laser.Titan.Debug;
    using System;
    using System.Text;

    public static class Logger
    {

        private static StringBuilder FileLogger;
        public static void Print(string log)
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("[DEBUG] " + log);
        }

        public static void Init()
        {
            FileLogger = new StringBuilder();
            Console.ForegroundColor = ConsoleColor.Cyan;
            Debugger.SetListener(new DebuggerListener());
        }

        public static void Warning(string log)
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("[WARNING] " + log);
        }

        public static void Error(string log)
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("[ERROR] " + log);
        }
        public static void Log(string log)
        {
            FileLogger.Append($"[{DateTime.Now}][WARN!!] " + log + "\n");
            File.AppendAllText("./log.txt", FileLogger.ToString());
            FileLogger.Clear();
        }

        public static void BLog(string log)
        {
            FileLogger.Append($"[{DateTime.Now}] " + log + "\n");
            File.AppendAllText("./battles.txt", FileLogger.ToString());
            FileLogger.Clear();
        }

        public static void HandleReport(string log)
        {
            FileLogger.Append($"[{DateTime.Now}] " + log + "\n");
            File.AppendAllText("./chatreports.txt", FileLogger.ToString());
            FileLogger.Clear();
        }
    }

    public class DebuggerListener : IDebuggerListener
    {
        public void Error(string message)
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("[LOGIC] Error: " + message);
        }

        public void Print(string message)
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("[LOGIC] Info: " + message);
        }

        public void Warning(string message)
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("[LOGIC] Warning: " + message);
        }
    }
}
