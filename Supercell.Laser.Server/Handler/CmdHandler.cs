namespace Supercell.Laser.Server.Handler
{
    using Supercell.Laser.Logic.Avatar;
    using Supercell.Laser.Logic.Data;
    using Supercell.Laser.Logic.Home;
    using Supercell.Laser.Logic.Message.Account;
    using Supercell.Laser.Logic.Message.Account.Auth;
    using Supercell.Laser.Logic.Util;
    using Supercell.Laser.Server.Database;
    using Supercell.Laser.Server.Database.Cache;
    using Supercell.Laser.Server.Database.Models;
    using Supercell.Laser.Server.Networking.Session;
    using System.Reflection;

    public static class CmdHandler
    {
        public static void Start()
        {
            while (true)
            {
                try
                {
                    string cmd = Console.ReadLine();
                    if (cmd == null) continue;
                    if (!cmd.StartsWith("/")) continue;
                    cmd = cmd.Substring(1);
                    string[] args = cmd.Split(" ");
                    if (args.Length < 1) continue;
                    switch (args[0])
                    {
                        case "premium":
                            ExecuteGivePremiumToAccount(args);
                            break;
                        case "ban":
                            ExecuteBanAccount(args);
                            break;
                        case "unban":
                            ExecuteUnbanAccount(args);
                            break;
                        case "changename":
                            ExecuteChangeNameForAccount(args);
                            break;
                        case "getvalue":
                            ExecuteGetFieldValue(args);
                            break;
                        case "changevalue":
                            ExecuteChangeValueForAccount(args);
                            break;
                        case "unlockall":
                            ExecuteUnlockAllForAccount(args);
                            break;
                        case "maintenance":
                            Console.WriteLine("Starting maintenance...");
                            ExecuteShutdown();
                            Console.WriteLine("Maintenance started!");
                            break;
                    }
                }
                catch (Exception) { }
            }
        }

        private static void ExecuteUnlockAllForAccount(string[] args)
        {
            if (args.Length != 2)
            {
                Console.WriteLine("Usage: /unlockall [TAG]");
                return;
            }

            long id = LogicLongCodeGenerator.ToId(args[1]);
            Account account = Accounts.Load(id);
            if (account == null)
            {
                Console.WriteLine("Fail: account not found!");
                return;
            }

            for (int i = 0; i < HomeMode.UNLOCKABLE_HEROES_COUNT; i++)
            {
                if (!account.Avatar.HasHero(16000000 + i))
                {
                    CharacterData character = DataTables.Get(16).GetDataWithId<CharacterData>(i);
                    CardData card = DataTables.Get(23).GetData<CardData>(character.Name + "_unlock");

                    account.Avatar.UnlockHero(character.GetGlobalId(), card.GetGlobalId());
                }
            }

            Logger.Print($"Successfully unlocked all brawlers for account {account.AccountId.GetHigherInt()}-{account.AccountId.GetLowerInt()} ({args[1]})");

            if (Sessions.IsSessionActive(id))
            {
                var session = Sessions.GetSession(id);
                session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                {
                    Message = "Your account updated!"
                });
                Sessions.Remove(id);
            }
        }

        private static void ExecuteGivePremiumToAccount(string[] args)
        {
            if (args.Length != 2)
            {
                Console.WriteLine("Usage: /premium [TAG]");
                return;
            }

            long id = LogicLongCodeGenerator.ToId(args[1]);
            Account account = Accounts.Load(id);
            if (account == null)
            {
                Console.WriteLine("Fail: account not found!");
                return;
            }

            account.Avatar.IsPremium = true;
            if (Sessions.IsSessionActive(id))
            {
                var session = Sessions.GetSession(id);
                session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                {
                    Message = "Your account updated!"
                });
                Sessions.Remove(id);
            }
        }

        private static void ExecuteUnbanAccount(string[] args)
        {
            if (args.Length != 2)
            {
                Console.WriteLine("Usage: /unban [TAG]");
                return;
            }

            long id = LogicLongCodeGenerator.ToId(args[1]);
            Account account = Accounts.Load(id);
            if (account == null)
            {
                Console.WriteLine("Fail: account not found!");
                return;
            }

            account.Avatar.Banned = false;
            if (Sessions.IsSessionActive(id))
            {
                var session = Sessions.GetSession(id);
                session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                {
                    Message = "Your account updated!"
                });
                Sessions.Remove(id);
            }
        }

        private static void ExecuteBanAccount(string[] args)
        {
            if (args.Length != 5)
            {
                Console.WriteLine("Usage: /ban [TAG] [Reason] [Day] [Month]");
                return;
            }

            long id = LogicLongCodeGenerator.ToId(args[1]);
            Account account = Accounts.Load(id);
            if (account == null)
            {
                Console.WriteLine("Fail: account not found!");
                return;
            }

            account.Avatar.Banned = true;
            account.Avatar.OldBans.Add(int.Parse(args[2]));
            account.Avatar.BannedReason = int.Parse(args[2]);
            account.Avatar.BanTime[0] = int.Parse(args[3]);
            account.Avatar.BanTime[1] = int.Parse(args[4]);

            if (account.Avatar.BanTime[1] == 99){
                account.Avatar.ResetTrophies();
                account.Avatar.Name = "Brawler";
            }
            else{
                account.Avatar.Name = "Аккаунт временно заблокирован!";
            }
            Accounts.Save(account);

            if (Sessions.IsSessionActive(id))
            {
                var session = Sessions.GetSession(id);
                session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                {
                    Message = "Вас заблокировали!"
                });
                Sessions.Remove(id);
            }
        }

        private static void ExecuteChangeNameForAccount(string[] args)
        {
            if (args.Length != 3)
            {
                Console.WriteLine("Usage: /changevalue [TAG] [NewName]");
                return;
            }

            long id = LogicLongCodeGenerator.ToId(args[1]);
            Account account = Accounts.Load(id);
            if (account == null)
            {
                Console.WriteLine("Fail: account not found!");
                return;
            }

            account.Avatar.Name = args[2];
            if (Sessions.IsSessionActive(id))
            {
                var session = Sessions.GetSession(id);
                session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                {
                    Message = "Your account updated!"
                });
                Sessions.Remove(id);
            }
        }

        private static void ExecuteGetFieldValue(string[] args)
        {
            if (args.Length != 3)
            {
                Console.WriteLine("Usage: /changevalue [TAG] [FieldName]");
                return;
            }

            long id = LogicLongCodeGenerator.ToId(args[1]);
            Account account = Accounts.Load(id);
            if (account == null)
            {
                Console.WriteLine("Fail: account not found!");
                return;
            }

            Type type = typeof(ClientAvatar);
            FieldInfo field = type.GetField(args[2]);
            if (field == null)
            {
                Console.WriteLine($"Fail: LogicClientAvatar::{args[2]} not found!");
                return;
            }

            int value = (int)field.GetValue(account.Avatar);
            Console.WriteLine($"LogicClientAvatar::{args[2]} = {value}");
        }

        private static void ExecuteChangeValueForAccount(string[] args)
        {
            if (args.Length != 4)
            {
                Console.WriteLine("Usage: /changevalue [TAG] [FieldName] [Value]");
                return;
            }

            long id = LogicLongCodeGenerator.ToId(args[1]);
            Account account = Accounts.Load(id);
            if (account == null)
            {
                Console.WriteLine("Fail: account not found!");
                return;
            }

            Type type = typeof(ClientAvatar);
            FieldInfo field = type.GetField(args[2]);
            if (field == null)
            {
                Console.WriteLine($"Fail: LogicClientAvatar::{args[2]} not found!");
                return;
            }

            field.SetValue(account.Avatar, int.Parse(args[3]));
            if (Sessions.IsSessionActive(id))
            {
                var session = Sessions.GetSession(id);
                session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                {
                    Message = "Your account updated!"
                });
                Sessions.Remove(id);
            }
        }

        private static void ExecuteShutdown()
        {
            Sessions.StartShutdown();
            AccountCache.SaveAll();
            AllianceCache.SaveAll();

            AccountCache.Started = false;
            AllianceCache.Started = false;
        }
    }
}
