namespace Supercell.Laser.Server
{
    using Supercell.Laser.Server.Handler;
    using Supercell.Laser.Server.Settings;
    using System.Drawing;

    static class Program
    {
        public const string SERVER_VERSION = "29.258.1";
        public const string BUILD_TYPE = "Beta";

        private static void Main(string[] args)
        {
            Console.Title = "SteelBrawl - server emulator v" + SERVER_VERSION + " Build: " + BUILD_TYPE;
            Directory.SetCurrentDirectory(AppContext.BaseDirectory);

            Colorful.Console.WriteWithGradient(
                @"  
   ______          __  ___                  __
  / __/ /____ ___ / / / _ )_______ __    __/ /
 _\ \/ __/ -_) -_) / / _  / __/ _ `/ |/|/ / / 
/___/\__/\__/\__/_/ /____/_/  \_,_/|__,__/_/                                                                                                                                                            
       " + "\n\n\n", Color.Blue, Color.Green, 8);

            Logger.Init();
            Configuration.Instance = Configuration.LoadFromFile("config.json");

            Resources.InitDatabase();
            Resources.InitLogic();
            Resources.InitNetwork();

            Logger.Print("Server started! Let's play SteelBrawl!");

            ExitHandler.Init();
            CmdHandler.Start();
        }
    }
}