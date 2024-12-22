

using System.Linq;

namespace Supercell.Laser.Logic.Home
{
    using Newtonsoft.Json;
    using Newtonsoft.Json.Linq;
    using Supercell.Laser.Logic.Command.Home;
    using Supercell.Laser.Logic.Data;
    using Supercell.Laser.Logic.Data.Helper;
    using Supercell.Laser.Logic.Helper;
    using Supercell.Laser.Logic.Home.Gatcha;
    using Supercell.Laser.Logic.Home.Items;
    using Supercell.Laser.Logic.Home.Quest;
    using Supercell.Laser.Logic.Home.Structures;
    using Supercell.Laser.Logic.Message.Home;
    using Supercell.Laser.Titan.DataStream;
    using System;
    using System.Collections.Generic;
    using System.Collections.Immutable;
    using System.Numerics;
    using System.Reflection.Metadata;
    using System.Text.RegularExpressions;
    using System.Xml.Linq;
    using static System.Collections.Specialized.BitVector32;

    [JsonObject(MemberSerialization.OptIn)]
    public class ClientHome
    {
        public const int DAILYOFFERS_COUNT = 6;

        public static readonly int[] GoldPacksPrice = new int[]
        {
            20, 50, 140, 280
        };

        public static readonly int[] GoldPacksAmount = new int[]
        {
            150, 400, 1200, 2600
        };

        [JsonProperty] public long HomeId;
        [JsonProperty] public int ThumbnailId;
        [JsonProperty] public int NameColorId;
        [JsonProperty] public int CharacterId;

        [JsonProperty] public List<OfferBundle> OfferBundles;

        [JsonProperty] public int TrophiesReward;
        [JsonProperty] public int TokenReward;
        [JsonProperty] public int StarTokenReward;
        [JsonProperty] public int StarPointsGained;
        [JsonProperty] public int PowerPlayTrophiesReward;

        [JsonProperty] public BigInteger BrawlPassProgress;
        [JsonProperty] public BigInteger PremiumPassProgress;
        [JsonProperty] public int BrawlPassTokens;
        [JsonProperty] public bool HasPremiumPass;
        [JsonProperty] public List<int> UnlockedEmotes;

        [JsonProperty] public int Experience;
        [JsonProperty] public int TokenDoublers;

        [JsonProperty] public int TrophyRoadProgress;
        [JsonProperty] public Quests Quests;
        [JsonProperty] public NotificationFactory NotificationFactory;
        [JsonProperty] public List<int> UnlockedSkins;
        [JsonProperty] public int[] SelectedSkins;
        [JsonProperty] public int PowerPlayGamesPlayed;
        [JsonProperty] public int PowerPlayScore;
        [JsonProperty] public int PowerPlayHighestScore;
        [JsonProperty] public int BattleTokens;
        [JsonProperty] public DateTime BattleTokensRefreshStart;
        [JsonProperty] public DateTime PremiumEndTime;
        [JsonProperty] public DateTime ChatBanEndTime;
        [JsonProperty] public DateTime BanEndTime;
        [JsonProperty] public List<long> ReportsIds;
        [JsonProperty] public bool BlockFriendRequests;
        [JsonProperty] public string IpAddress;
        [JsonProperty] public string Device;
        [JsonProperty] public List<string> OffersClaimed;
        [JsonProperty] public string Day;


        [JsonIgnore] public EventData[] Events;

        public PlayerThumbnailData Thumbnail => DataTables.Get(DataType.PlayerThumbnail).GetDataByGlobalId<PlayerThumbnailData>(ThumbnailId);
        public NameColorData NameColor => DataTables.Get(DataType.NameColor).GetDataByGlobalId<NameColorData>(NameColorId);
        public CharacterData Character => DataTables.Get(DataType.Character).GetDataByGlobalId<CharacterData>(CharacterId);

        public HomeMode HomeMode;

        [JsonProperty] public DateTime LastVisitHomeTime;
        [JsonProperty] public DateTime LastRotateDate;

        [JsonIgnore] public bool ShouldUpdateDay;

        public ClientHome()
        {
            ThumbnailId = GlobalId.CreateGlobalId(28, 0);
            NameColorId = GlobalId.CreateGlobalId(43, 0);
            CharacterId = GlobalId.CreateGlobalId(16, 0);
            SelectedSkins = new int[] { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

            OfferBundles = new List<OfferBundle>();
            OffersClaimed = new List<string>();
            ReportsIds = new List<long>();
            UnlockedSkins = new List<int>();
            LastVisitHomeTime = DateTime.UnixEpoch;

            TrophyRoadProgress = 1;

            BrawlPassProgress = 1;
            PremiumPassProgress = 1;

            UnlockedEmotes = new List<int>();
            BattleTokens = 200;
            BattleTokensRefreshStart = new();
            if (NotificationFactory == null)
            {
                NotificationFactory = new NotificationFactory();
            }

        }

        public void HomeVisited()
        {
            
            // RotateShopContent(DateTime.UtcNow, OfferBundles.Count == 0);
            LastVisitHomeTime = DateTime.UtcNow;
            //Quests = null;
            UpdateOfferBundles();

            string Today = LastVisitHomeTime.ToString("d");
            if (Today != Day)
            {
                Day = Today;
            }

            if (Quests == null && TrophyRoadProgress >= 11)
            {
                Quests = new Quests();
                Quests.AddRandomQuests(HomeMode.Avatar.Heroes, 6);
            }
        }

        /*public void Tick()
        {
            LastVisitHomeTime = DateTime.UtcNow;
            TokenReward = 0;
            TrophiesReward = 0;
            StarTokenReward = 0;
            StarPointsGained = 0;
            PowerPlayTrophiesReward = 0;
        }*/
        public int TimerMath(DateTime timer_start, DateTime timer_end)
        {
            {
                DateTime timer_now = DateTime.Now;
                if (timer_now > timer_start)
                {
                    if (timer_now < timer_end)
                    {
                        int time_sec = (int)(timer_end - timer_now).TotalSeconds;
                        return time_sec;
                    }
                    else
                    {
                        return -1;
                    }
                }
                else
                {
                    return -1;
                }
            }
        }
        public void Tick()
        {
            LastVisitHomeTime = DateTime.UtcNow;
            while (ShouldAddTokens())
            {
                BattleTokensRefreshStart = BattleTokensRefreshStart.AddMinutes(30);
                BattleTokens = Math.Min(200, BattleTokens + 30);
                if (BattleTokens == 200)
                {
                    BattleTokensRefreshStart = new();
                    break;
                }
            }

        }

        public int GetbattleTokensRefreshSeconds()
        {
            if (BattleTokensRefreshStart == new DateTime())
            {
                return -1;
            }
            return (int)BattleTokensRefreshStart.AddMinutes(30).Subtract(DateTime.UtcNow).TotalSeconds;
        }
        public bool ShouldAddTokens()
        {
            if (BattleTokensRefreshStart == new DateTime())
            {
                return false;
            }
            return GetbattleTokensRefreshSeconds() < 1;
        }

        public void PurchaseOffer(int index)
        {
            // if (index < 0 || index >= OfferBundles.Count) return;

            OfferBundle bundle = OfferBundles[index];
            // if (bundle.Purchased) return;

            if (bundle.Currency == 0)
            {
                if (!HomeMode.Avatar.UseDiamonds(bundle.Cost)) return;
            }
            else if (bundle.Currency == 1)
            {
                if (!HomeMode.Avatar.UseGold(bundle.Cost)) return;
            }
            else if (bundle.Currency == 3)
            {
                if (!HomeMode.Avatar.UseStarPoints(bundle.Cost)) return;
            }

            // bundle.Purchased = true;

            if (bundle.Claim == "debug")
            {
                ;
            }
            else
            {
                OffersClaimed.Add(bundle.Claim);
            }

            LogicGiveDeliveryItemsCommand command = new LogicGiveDeliveryItemsCommand();
            Random rand = new Random();

            foreach (Offer offer in bundle.Items)
            {
                if (offer.Type == ShopItem.BrawlBox || offer.Type == ShopItem.FreeBox)
                {
                    for (int x = 0; x < offer.Count; x++)
                    {
                        DeliveryUnit unit = new DeliveryUnit(10);
                        HomeMode.SimulateGatcha(unit);
                        if (x + 1 != offer.Count)
                        {
                            command.Execute(HomeMode);
                        }
                        command.DeliveryUnits.Add(unit);
                    }
                }
                else if (offer.Type == ShopItem.HeroPower)
                {
                    DeliveryUnit unit = new DeliveryUnit(100);
                    GatchaDrop reward = new GatchaDrop(6);
                    reward.DataGlobalId = offer.ItemDataId;
                    reward.Count = offer.Count;
                    unit.AddDrop(reward);
                    command.DeliveryUnits.Add(unit);
                }
                else if (offer.Type == ShopItem.BigBox)
                {
                    for (int x = 0; x < offer.Count; x++)
                    {
                        DeliveryUnit unit = new DeliveryUnit(12);
                        HomeMode.SimulateGatcha(unit);
                        if (x + 1 != offer.Count)
                        {
                            command.Execute(HomeMode);
                        }
                        command.DeliveryUnits.Add(unit);
                    }
                }
                else if (offer.Type == ShopItem.MegaBox)
                {
                    for (int x = 0; x < offer.Count; x++)
                    {
                        DeliveryUnit unit = new DeliveryUnit(11);
                        HomeMode.SimulateGatcha(unit);
                        if (x + 1 != offer.Count)
                        {
                            command.Execute(HomeMode);
                        }
                        command.DeliveryUnits.Add(unit);
                    }
                }
                else if (offer.Type == ShopItem.Skin)
                {
                    DeliveryUnit unit = new DeliveryUnit(100);
                    GatchaDrop reward = new GatchaDrop(9);
                    reward.SkinGlobalId = GlobalId.CreateGlobalId(29, offer.SkinDataId);
                    unit.AddDrop(reward);
                    command.DeliveryUnits.Add(unit);
                }
                else if (offer.Type == ShopItem.Gems)
                {
                    DeliveryUnit unit = new DeliveryUnit(100);
                    GatchaDrop reward = new GatchaDrop(8);
                    reward.Count = offer.Count;
                    unit.AddDrop(reward);
                    command.DeliveryUnits.Add(unit);
                }
                else if (offer.Type == ShopItem.Coin)
                {
                    DeliveryUnit unit = new DeliveryUnit(100);
                    GatchaDrop reward = new GatchaDrop(7);
                    reward.Count = offer.Count;
                    unit.AddDrop(reward);
                    command.DeliveryUnits.Add(unit);
                }
                else if (offer.Type == ShopItem.GuaranteedHero)
                {
                    DeliveryUnit unit = new DeliveryUnit(100);
                    GatchaDrop reward = new GatchaDrop(1);
                    reward.DataGlobalId = offer.ItemDataId;
                    reward.Count = 1;
                    unit.AddDrop(reward);
                    command.DeliveryUnits.Add(unit);
                }
                else if (offer.Type == ShopItem.CoinDoubler)
                {
                    DeliveryUnit unit = new DeliveryUnit(100);
                    GatchaDrop reward = new GatchaDrop(2);
                    reward.Count = offer.Count;
                    unit.AddDrop(reward);
                    command.DeliveryUnits.Add(unit);
                }
                else if (offer.Type == ShopItem.EmoteBundle)
                {
                    DeliveryUnit unit = new DeliveryUnit(100);
                    List<int> Emotes_All = new List<int> { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300 };
                    List<int> Emotes_Locked = Emotes_All.Except(UnlockedEmotes).OrderBy(x => Guid.NewGuid()).Take(3).ToList();;

                    foreach (int x in Emotes_Locked){
                        GatchaDrop reward = new GatchaDrop(11);
                        reward.Count = 1;
                        reward.PinGlobalId = 52000000 + x;
                        unit.AddDrop(reward);
                        UnlockedEmotes.Add(x);
                    }
                    command.DeliveryUnits.Add(unit);
                }
                else if (offer.Type == ShopItem.Emote)
                {
                    DeliveryUnit unit = new DeliveryUnit(100);
                    GatchaDrop reward = new GatchaDrop(11);
                    reward.Count = 1;
                    reward.PinGlobalId = 52000155;
                    unit.AddDrop(reward);
                    command.DeliveryUnits.Add(unit);
                }
                else
                {
                    // todo...
                }

                command.Execute(HomeMode);

                
            }
            UpdateOfferBundles();
            AvailableServerCommandMessage message = new AvailableServerCommandMessage();
            message.Command = command;
            HomeMode.GameListener.SendMessage(message);
        }

        public List<int> StaticSkinsData(string Data){
            List<int> skinsID = new List<int>();
            List<int> skinsPrice = new List<int>();
            List<int> skinsSalePrice = new List<int>();
            List<int> skinsBrawler = new List<int>();

            {
                skinsID.Add(2); // Айди скина // Бандитка Шелли
                skinsPrice.Add(30); // Цена
                skinsSalePrice.Add(19); // Цена по скидке
                skinsBrawler.Add(1); // Боец скина
            }

            {
                skinsID.Add(11); // Айди скина // Сакура Спайк
                skinsPrice.Add(80); // Цена
                skinsSalePrice.Add(39); // Цена по скидке
                skinsBrawler.Add(5); // Боец скина
            }

            {
                skinsID.Add(58); // Айди скина // Кунг Фу Брок
                skinsPrice.Add(150); // Цена
                skinsSalePrice.Add(79); // Цена по скидке
                skinsBrawler.Add(3); // Боец скина
            }


            if (Data == "price"){
                return skinsPrice;
            }
            else if (Data == "saleprice"){
                return skinsSalePrice;
            }
            else if (Data == "brawler"){
                return skinsBrawler;
            }
            else{
                return skinsID;
            }
        }

        private void UpdateOfferBundles()
        {
            OfferBundles.Clear();

            // Пример перебора скинов
            for (int x = 0; x < StaticSkinsData("id").Count; x++){
                GenerateOffer(
                    new DateTime(2024, 10, 1, 12, 0, 0), new DateTime(2024, 12, 1, 12, 0, 0),
                    StaticSkinsData("brawler")[x], (13000000), StaticSkinsData("id")[x], ShopItem.Skin, 
                    StaticSkinsData("price")[x], 15000, 0, 
                    "zeta", "ОСОБАЯ АКЦИЯ", "offer_legendary"
                );
            }

            // Пример произвольного скина по скидке
            GenerateOffer(
                new DateTime(2024, 10, 31, 12, 0, 0), new DateTime(2024, 12, 1, 12, 0, 0),
                StaticSkinsData("brawler")[2], (13000000), StaticSkinsData("id")[2], ShopItem.Skin, 
                StaticSkinsData("saleprice")[2], StaticSkinsData("price")[2], 0, 
                "zeta", "ОСОБАЯ АКЦИЯ", "offer_legendary"
            );

            if(HomeMode.Avatar.HighestTrophies >= 250){ // Подарок на 250 кубкав сами сделаете
                GenerateOffer(
                    new DateTime(2024, 4, 20, 12, 0, 0), new DateTime(2024, 9, 22, 10, 0, 0),
                    100000000, 999, 180, ShopItem.Gems,
                    100000000, 1000, 0,
                    "gems", "Гемы", "offer_xmas"
                );
            }                                
            GenerateOffer(
                new DateTime(2024, 10, 2, 10, 0, 0), new DateTime(2024, 11, 2, 10, 0, 0),
                24, (13000000), 241, ShopItem.Skin,
                0, 0, 0,
                "18s222200", "Подарок к обновлению!", "offer_gems"
                );
            GenerateOffer(
                new DateTime(2024, 10, 2, 10, 0, 0), new DateTime(2024, 12, 6, 10, 0, 0),
                6, 999, 210, ShopItem.MegaBox,
                0, 0, 0,
                "18ss111w100", "1/7", "offer_gems"
                );      
            GenerateOffer(
                new DateTime(2024, 10, 31, 12, 0, 0), new DateTime(2024, 11, 6, 10, 0, 0),
                2000, 999, 210, ShopItem.Coin,
                0, 0, 0,
                "181sswww11100", "2/7", "offer_gems"
                );  
            GenerateOffer(
                new DateTime(2024, 11, 1, 12, 0, 0), new DateTime(2024, 11, 6, 10, 0, 0),
                50, 999, 210, ShopItem.Gems,
                0, 0, 0,
                "181sswssss11100", "3/7", "offer_gems"
                );                              
            GenerateOffer(
                new DateTime(2024, 11, 2, 12, 0, 0), new DateTime(2024, 11, 6, 10, 0, 0),
                8, 999, 210, ShopItem.BigBox,
                0, 0, 0,
                "181sssss11100", "4/7", "offer_gems"
                );    
GenerateOffer(
                    new DateTime(2024, 10, 1, 12, 0, 0), new DateTime(2024, 11, 7, 12, 0, 0),
                    3, (13000000), 261, ShopItem.Skin, 
                    0, 15000, 0, 
                    "zeta22", "5/7", "offer_legendary"
                );           
            GenerateOffer(
                new DateTime(2024, 11, 4, 10, 0, 0), new DateTime(2024, 11, 6, 10, 0, 0),
                100, 999, 210, ShopItem.Gems,
                0, 0, 0,
                "181sasssss11100", "6/7", "offer_gems"
                );          
            GenerateOffer(
                new DateTime(2024, 11, 5, 10, 0, 0), new DateTime(2024, 1