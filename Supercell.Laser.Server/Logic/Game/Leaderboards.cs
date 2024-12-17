namespace Supercell.Laser.Server.Logic.Game
{
    using Newtonsoft.Json;
    using Supercell.Laser.Logic.Club;
    using Supercell.Laser.Server.Database.Models;
    using Supercell.Laser.Server.Networking.Session;
    using System.Text;

    public class DataEntry
    {
        public DateTime Time { get; set; }
        [JsonProperty(DefaultValueHandling = DefaultValueHandling.Populate)]
        public int Online { get; set; }
    }

    public class DataContainer
    {
        public List<DataEntry> Data { get; set; }
    }

    public static class Leaderboards
    {
        private static List<Account> Accounts;
        private static List<Alliance> Alliances;
        private static Dictionary<int, List<Account>> Brawlers;
        private static Thread Thread;
        private static int timeg;

        private static StringBuilder FileLogger;

        public static void Init()
        {
            Accounts = new List<Account>();
            Alliances = new List<Alliance>();
            Brawlers = new Dictionary<int, List<Account>>();

            Thread = new Thread(Update);
            Thread.Start();
            FileLogger = new();
        }

        public static Account[] GetAvatarRankingList()
        {
            return Accounts.ToArray();
        }

        public static Dictionary<int, List<Account>> GetBrawlersRankingList()
        {
            return Brawlers;
        }

        public static Alliance[] GetAllianceRankingList()
        {
            return Alliances.ToArray();
        }

        private static void Update()
        {
            while (true)
            {
                Accounts = Database.Accounts.GetRankingList();
                Alliances = Database.Alliances.GetRankingList();
                Brawlers = Database.Accounts.GetBrawlersRankingList();

                /*List<DataEntry> entries;

                if (File.Exists(@"./online.json"))
                {
                    // Якщо файл існує, зчитуємо дані з нього
                    string existingData = File.ReadAllText(@"./online.json");
                    DataContainer c = JsonConvert.DeserializeObject<DataContainer>(existingData);
                    entries = c.Data;
                }
                else
                {
                    // Якщо файл не існує, створюємо новий список
                    entries = new List<DataEntry>();
                }

                // Додаємо новий об'єкт DataEntry до списку
                entries.Add(new DataEntry { Time = DateTime.Now, Online = Sessions.Count });

                // Записуємо дані в об'єкт контейнера
                DataContainer container = new DataContainer { Data = entries };

                // Конвертуємо об'єкт в JSON рядок
                string json = JsonConvert.SerializeObject(container, Formatting.Indented);

                File.WriteAllText(@"./online.json", json);
                FileLogger.Append(json);

                // Зупиняємо виконання на 60 секунд
                Thread.Sleep(60 * 1000);*/
            }
        }
    }
}
