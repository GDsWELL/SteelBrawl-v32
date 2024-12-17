namespace Supercell.Laser.Server.Database
{
    using MySql.Data.MySqlClient;
    using Newtonsoft.Json;
    using Supercell.Laser.Logic.Data.Helper;
    using Supercell.Laser.Logic.Home;
    using Supercell.Laser.Logic.Club;
    using Supercell.Laser.Logic.Home.Items;
    using Supercell.Laser.Logic.Home.Structures;
    using Supercell.Laser.Server.Database.Cache;
    using Supercell.Laser.Server.Database.Models;
    using Supercell.Laser.Server.Settings;
    using Supercell.Laser.Server.Utils;

    public static class Accounts
    {
        private static long AvatarIdCounter;
        private static string ConnectionString;

        public static void Init(string user, string password)
        {
            MySqlConnectionStringBuilder builder = new MySqlConnectionStringBuilder();
            builder.Server = "127.0.0.1";
            builder.UserID = user;
            builder.Password = password;
            builder.SslMode = MySqlSslMode.Disabled;
            builder.Database = Configuration.Instance.DatabaseName;
            builder.CharacterSet = "utf8mb4";


            JsonConvert.DefaultSettings = () => new JsonSerializerSettings
            {
                DefaultValueHandling = DefaultValueHandling.Ignore,
                NullValueHandling = NullValueHandling.Ignore
            };

            ConnectionString = builder.ToString();

            AccountCache.Init();

            AvatarIdCounter = GetMaxAvatarId();
        }

        public static long GetMaxAvatarId()
        {
           using var Connection = new MySqlConnection(ConnectionString);
            Connection.Open();
            MySqlCommand command = new MySqlCommand("SELECT coalesce(MAX(Id), 0) FROM accounts", Connection);

            long result = Convert.ToInt64(command.ExecuteScalar());
            Connection.Close();
            return result;
        }

        public static Account Create()
        {
            Account account = new Account();
            account.AccountId = ++AvatarIdCounter;
            account.PassToken = Helpers.RandomString(40);

            account.Avatar.AccountId = account.AccountId;
            account.Avatar.PassToken = account.PassToken;

            account.Home.HomeId = account.AccountId;

            NotificationFactory n = new();
            n.Add(new Notification
            {
                Id = 83,
                PrimaryMessageEntry = "Добро пожаловать в SteelBrawl",
                SecondaryMessageEntry = "Также рекомендуем зайти в наш тг канал (t.me/steel_brawl)",
                ButtonMessageEntry = "<cff003f>П<cff007f>е<cff00bf>р<cff00ff>е<cff00ff>й<cbf00ff>т<c7f00ff>и</c>",
                FileLocation = "pop_up_1920x1235_welcome.png",
                FileSha = "6bb3b752a80107a14671c7bdebe0a1b662448d0c",
                ExtLint = "brawlstars://extlink?page=https%3A%2F%2Ft.me/steel_brawl",
            });
            account.Home.NotificationFactory = n;

            Hero hero = new Hero(16000000, 23000000);
            account.Avatar.Heroes.Add(hero);

            string json = JsonConvert.SerializeObject(account);

            var Connection = new MySqlConnection(ConnectionString);
            Connection.Open();
            MySqlCommand command = new MySqlCommand($"INSERT INTO accounts (`Id`, `Trophies`, `Data`) VALUES ({(long)account.AccountId}, {account.Avatar.Trophies}, @data)", Connection);
            command.Parameters?.AddWithValue("@data", json);
            command.ExecuteNonQuery();
            Connection.Close();

            AccountCache.Cache(account);

            return account;
        }

        public static void Save(Account account)
        {
            if (account == null) return;

            string json = JsonConvert.SerializeObject(account);

            var Connection = new MySqlConnection(ConnectionString);
            Connection.Open();
            MySqlCommand command = new MySqlCommand($"UPDATE accounts SET `Trophies`='{account.Avatar.Trophies}', `Data`=@data WHERE Id = '{account.AccountId}'", Connection);
            command.Parameters?.AddWithValue("@data", json);
            command.ExecuteNonQuery();
            Connection.Close();
        }

        public static Account Load(long id)
        {
            if (AccountCache.IsAccountCached(id))
            {
                return AccountCache.GetAccount(id);
            }

            var Connection = new MySqlConnection(ConnectionString);
            Connection.Open();
            MySqlCommand command = new MySqlCommand($"SELECT * FROM accounts WHERE Id = '{id}'", Connection);
            MySqlDataReader reader = command.ExecuteReader();
            if (reader.Read())
            {
                Account account = JsonConvert.DeserializeObject<Account>((string)reader["Data"]);
                AccountCache.Cache(account);
                Connection.Close();
                return account;
            }
            Connection.Close();
            return null;
        }

        public static Account LoadNoChache(long id)
        {
            if (AccountCache.IsAccountCached(id))
            {
                return AccountCache.GetAccount(id);
            }

            var Connection = new MySqlConnection(ConnectionString);
            Connection.Open();
            MySqlCommand command = new MySqlCommand($"SELECT * FROM accounts WHERE Id = '{id}'", Connection);
            MySqlDataReader reader = command.ExecuteReader();
            if (reader.Read())
            {
                Account account = JsonConvert.DeserializeObject<Account>((string)reader["Data"]);
                Connection.Close();
                return account;
            }
            Connection.Close();
            return null;
        }

        public static List<Account> GetRankingList()
        {
            #region GetGlobal

            var list = new List<Account>();

            try
            {
                using (var connection = new MySqlConnection(ConnectionString))
                {
                    connection.Open();

                    using (var cmd = new MySqlCommand($"SELECT * FROM accounts ORDER BY `Trophies` DESC LIMIT 200",
                        connection))
                    {
                        var reader = cmd.ExecuteReader();

                        while (reader.Read())
                        {
                            var account = JsonConvert.DeserializeObject<Account>((string)reader["Data"]);
                            long allianceId = account.Avatar.AllianceId;
                            if (allianceId > 0)
                            {
                                Alliance alliance = Alliances.Load(allianceId);
                                if (alliance != null) 
                                {
                                    account.Avatar.AllianceName = alliance.Name;
                                }
                                
                            }

                            list.Add(account);
                        }
                        //list.Add(JsonConvert.DeserializeObject<Account>((string)reader["Data"]) with { AllianceName = "test" });
                    }

                    connection.Close();
                }

                return list;
            }
            catch (Exception exception)
            {
                return list;
            }

            #endregion
        }

          public static void MiokiID_DataUpdate(HomeMode homeMode)
        {
            using (var connection = new MySqlConnection(ConnectionString))
            {
                connection.Open();
                var command = new MySqlCommand($"UPDATE accounts SET `login`='{homeMode.Avatar.Login}', `password`='{homeMode.Avatar.Password}' WHERE Id = '{homeMode.Avatar.AccountId}'", connection);
                command.ExecuteNonQuery();
                connection.Close();
            }
        }

        public static void MiokiID_DataUpdate_Account(Account account)
        {
            using (var connection = new MySqlConnection(ConnectionString))
            {
                connection.Open();
                var command = new MySqlCommand($"UPDATE accounts SET `login`='{account.Avatar.Login}', `password`='{account.Avatar.Password}' WHERE Id = '{account.AccountId}'", connection);
                command.ExecuteNonQuery();
                connection.Close();
            }
        }
    
                

        public static Boolean LoginUsed(string Login)
        {
            using (var connection = new MySqlConnection(ConnectionString))
            {
                connection.Open();
                MySqlCommand command = new MySqlCommand($"SELECT * FROM accounts WHERE login = '{Login}'", connection);
                MySqlDataReader reader = command.ExecuteReader();
                if (reader.Read())
                {
                    return true;
                }
                connection.Close();
            }
            return false;
        }

        public static Account MiokiID_GetAccount(string Login, string Password)
        {
            using (var connection = new MySqlConnection(ConnectionString))
            {
                connection.Open();
                MySqlCommand command = new MySqlCommand($"SELECT * FROM accounts WHERE login = '{Login}'", connection);
                MySqlDataReader reader = command.ExecuteReader();
                if (reader.Read())
                {
                    Account account = JsonConvert.DeserializeObject<Account>((string)reader["Data"]);
                    if (account.Avatar.Login == Login && account.Avatar.Password == Password){
                        return account;
                    }
                    else {
                        return null;
                    }
                }
                connection.Close();
            }
            return null;
        }

        public static Dictionary<int, List<Account>> GetBrawlersRankingList()
        {
            #region GetGlobal

            var list = new Dictionary<int, List<Account>>();
            List<int> Brawlers = new() { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40 };
            try
            {
                using (var connection = new MySqlConnection(ConnectionString))
                {
                    connection.Open();

                    using (var cmd = new MySqlCommand($"SELECT * FROM accounts",
                        connection))
                    {
                        var reader = cmd.ExecuteReader();

                        while (reader.Read())
                        {
                            try
                            {
                                var account = JsonConvert.DeserializeObject<Account>((string)reader["Data"]);
                                long allianceId = account.Avatar.AllianceId;
                                if (allianceId > 0)
                                {
                                    Alliance alliance = Alliances.Load(allianceId);
                                if (alliance == null)
                                {
                                    continue;
                                }
                                account.Avatar.AllianceName = alliance.Name;
                                }
                                foreach (Hero hero in account.Avatar.Heroes)
                                {
                                    if (list.ContainsKey(hero.CharacterId))
                                    {
                                        list[hero.CharacterId].Add(account);
                                    }
                                    else
                                    {
                                        List<Account> a = new();
                                        a.Add(account);
                                        list.Add(hero.CharacterId, a);
                                    }
                                }
                            }
                            catch (Exception e)
                            {
                                Logger.Error("LB Error" + e.ToString());
                            }

                        }
                        //list.Add(JsonConvert.DeserializeObject<Account>((string)reader["Data"]) with { AllianceName = "test" });
                    }

                    connection.Close();
                }

                return list;
            }
            catch (Exception exception)
            {
                return list;
            }

            #endregion
        }
    }
}

