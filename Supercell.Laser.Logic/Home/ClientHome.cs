

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
            SelectedSkins = new int[] { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

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
                new DateTime(2024, 11, 5, 10, 0, 0), new DateTime(2024, 11, 6, 10, 0, 0),
                1, 43, 210, ShopItem.GuaranteedHero,
                0, 0, 0,
                "18111sasssss11100", "7/7", "offer_gems"
                );                                              
GenerateOffer(
                    new DateTime(2024, 10, 1, 12, 0, 0), new DateTime(2024, 11, 7, 12, 0, 0),
                    32, (13000000), 255, ShopItem.Skin, 
                    450, 15000, 0, 
                    "zeta1", "ОСОБАЯ АКЦИЯ", "offer_legendary"
                );  
GenerateOffer(
                    new DateTime(2024, 10, 1, 12, 0, 0), new DateTime(2024, 11, 7, 12, 0, 0),
                    15, (13000000), 257, ShopItem.Skin, 
                    450, 15000, 0, 
                    "zeta2", "ОСОБАЯ АКЦИЯ", "offer_legendary"
                );
GenerateOffer(
                    new DateTime(2024, 10, 1, 12, 0, 0), new DateTime(2024, 11, 7, 12, 0, 0),
                    26, (13000000), 239, ShopItem.Skin, 
                    500, 15000, 0, 
                    "zeta3", "ОСОБАЯ АКЦИЯ", "offer_legendary"
                );  
GenerateOffer(
                    new DateTime(2024, 10, 1, 12, 0, 0), new DateTime(2024, 11, 7, 12, 0, 0),
                    36, (13000000), 256, ShopItem.Skin, 
                    450, 15000, 0, 
                    "zeta4", "ОСОБАЯ АКЦИЯ", "offer_legendary"
                );                                  
GenerateOffer(
                    new DateTime(2024, 10, 1, 12, 0, 0), new DateTime(2024, 11, 7, 12, 0, 0),
                    1, (13000000), 240, ShopItem.Skin, 
                    9000, 20000, 0, 
                    "zeta5", "ОСОБАЯ АКЦИЯ", "offer_legendary"
                );    
            GenerateOffer(
                new DateTime(2024, 10, 2, 10, 0, 0), new DateTime(2024, 11, 7, 10, 0, 0),
                1, 42, 210, ShopItem.GuaranteedHero,
                2500, 0, 0,
                "18sw111100", "Ранний доступ!", "offer_legendary"
                );                                                                                                        



        }

        public void GenerateOffer(
            DateTime OfferStart,
            DateTime OfferEnd,
            int Count,
            int BrawlerID,
            int Extra,
            ShopItem Item,
            int Cost,
            int OldCost,
            int Currency,
            string Claim,
            string Title,
            string BGR
            ){

            OfferBundle bundle = new OfferBundle();
            bundle.IsDailyDeals = false;
            bundle.IsTrue = true;
            bundle.EndTime = OfferEnd;
            bundle.Cost = Cost; 
            bundle.OldCost = OldCost; 
            bundle.Currency = Currency;
            bundle.Claim = Claim;
            bundle.Title = Title;
            bundle.BackgroundExportName = BGR;

            if (OffersClaimed.Contains(bundle.Claim))
            {
                bundle.Purchased = true;
            }
            if (TimerMath(OfferStart, OfferEnd) == -1)
            {
                bundle.Purchased = true;
            }
            if (HomeMode.HasHeroUnlocked(16000000 + BrawlerID) && Item == ShopItem.GuaranteedHero)
            {
                bundle.Purchased = true;
            }
            if (!HomeMode.HasHeroUnlocked(16000000 + BrawlerID) && Item == ShopItem.HeroPower)
            {
                bundle.Purchased = true;
            }
            if (Item == ShopItem.Skin && (!HomeMode.HasHeroUnlocked(16000000 + Count) || UnlockedSkins.Contains(Extra)))
            {
                bundle.Purchased = true;
            }

            Offer offer = new Offer(Item, Count, (16000000 + BrawlerID), Extra);
            bundle.Items.Add(offer);

            OfferBundles.Add(bundle);
        }

        public void GenerateOfferDaily(
            DateTime OfferStart,
            DateTime OfferEnd,
            int Count,
            int BrawlerID,
            int Extra,
            ShopItem Item,
            int Cost,
            int OldCost,
            int Currency,
            string Claim,
            string Title,
            string BGR
            ){

            OfferBundle bundle = new OfferBundle();
            bundle.IsDailyDeals = true;
            bundle.IsTrue = true;
            bundle.EndTime = OfferEnd;
            bundle.Cost = Cost; 
            bundle.OldCost = OldCost; 
            bundle.Currency = Currency;
            bundle.Claim = Claim;
            bundle.Title = Title;
            bundle.BackgroundExportName = BGR;

            if (OffersClaimed.Contains(bundle.Claim))
            {
                bundle.Purchased = true;
            }
            if (TimerMath(OfferStart, OfferEnd) == -1)
            {
                bundle.Purchased = true;
            }
            if (HomeMode.HasHeroUnlocked(16000000 + BrawlerID) && Item == ShopItem.GuaranteedHero)
            {
                bundle.Purchased = true;
            }
            if (!HomeMode.HasHeroUnlocked(16000000 + BrawlerID) && Item == ShopItem.HeroPower)
            {
                bundle.Purchased = true;
            }
            if (Item == ShopItem.Skin && (!HomeMode.HasHeroUnlocked(16000000 + Count) || UnlockedSkins.Contains(Extra)))
            {
                bundle.Purchased = true;
            }

            Offer offer = new Offer(Item, Count, (16000000 + BrawlerID), Extra);
            bundle.Items.Add(offer);

            OfferBundles.Add(bundle);
        }

        public void GenerateOffer2(
            DateTime OfferStart,
            DateTime OfferEnd,
            int Count,
            int BrawlerID,
            int Extra,
            ShopItem Item,
            int Count2,
            int BrawlerID2,
            int Extra2,
            ShopItem Item2,
            int Cost,
            int OldCost,
            int Currency,
            string Claim,
            string Title,
            string BGR
            ){

            OfferBundle bundle = new OfferBundle();
            bundle.IsDailyDeals = false;
            bundle.IsTrue = true;
            bundle.EndTime = OfferEnd;
            bundle.Cost = Cost; 
            bundle.OldCost = OldCost; 
            bundle.Currency = Currency;
            bundle.Claim = Claim;
            bundle.Title = Title;
            bundle.BackgroundExportName = BGR;

            if (OffersClaimed.Contains(bundle.Claim))
            {
                bundle.Purchased = true;
            }
            if (TimerMath(OfferStart, OfferEnd) == -1)
            {
                bundle.Purchased = true;
            }
            if (HomeMode.HasHeroUnlocked(16000000 + BrawlerID) && Item == ShopItem.GuaranteedHero)
            {
                bundle.Purchased = true;
            }
            if (!HomeMode.HasHeroUnlocked(16000000 + BrawlerID) && Item == ShopItem.HeroPower)
            {
                bundle.Purchased = true;
            }
            if (Item == ShopItem.Skin && (!HomeMode.HasHeroUnlocked(16000000 + Count) || UnlockedSkins.Contains(Extra)))
            {
                bundle.Purchased = true;
            }

            Offer offer = new Offer(Item, Count, (16000000 + BrawlerID), Extra);
            bundle.Items.Add(offer);
            Offer offer2 = new Offer(Item2, Count2, (16000000 + BrawlerID2), Extra2);
            bundle.Items.Add(offer2);

            OfferBundles.Add(bundle);
        }

        public void GenerateOffer4(
            DateTime OfferStart,
            DateTime OfferEnd,
            int Count,
            int BrawlerID,
            int Extra,
            ShopItem Item,
            int Count2,
            int BrawlerID2,
            int Extra2,
            ShopItem Item2,
            int Cost,
            int OldCost,
            int Currency,
            string Claim,
            string Title,
            string BGR
            ){

            OfferBundle bundle = new OfferBundle();
            bundle.IsDailyDeals = false;
            bundle.IsTrue = true;
            bundle.EndTime = OfferEnd;
            bundle.Cost = Cost; 
            bundle.OldCost = OldCost; 
            bundle.Currency = Currency;
            bundle.Claim = Claim;
            bundle.Title = Title;
            bundle.BackgroundExportName = BGR;

            if (OffersClaimed.Contains(bundle.Claim))
            {
                bundle.Purchased = true;
            }
            if (TimerMath(OfferStart, OfferEnd) == -1)
            {
                bundle.Purchased = true;
            }
            if (HomeMode.HasHeroUnlocked(16000000 + BrawlerID) && Item == ShopItem.GuaranteedHero)
            {
                bundle.Purchased = true;
            }
            if (!HomeMode.HasHeroUnlocked(16000000 + BrawlerID) && Item == ShopItem.HeroPower)
            {
                bundle.Purchased = true;
            }
            if (Item == ShopItem.Skin && (!HomeMode.HasHeroUnlocked(16000000 + Count) || UnlockedSkins.Contains(Extra)))
            {
                bundle.Purchased = true;
            }

            Offer offer = new Offer(Item, Count, (16000000 + BrawlerID), Extra);
            bundle.Items.Add(offer);
            Offer offer2 = new Offer(Item2, Count2, (16000000 + BrawlerID2), Extra2);
            bundle.Items.Add(offer2);

            OfferBundles.Add(bundle);
        }

        public void GenerateOffer3(
            DateTime OfferStart,
            DateTime OfferEnd,
            int Count,
            int BrawlerID,
            int Extra,
            ShopItem Item,
            int Count2,
            int BrawlerID2,
            int Extra2,
            ShopItem Item2,
            int Count3,
            int BrawlerID3,
            int Extra3,
            ShopItem Item3,
            int Cost,
            int OldCost,
            int Currency,
            string Claim,
            string Title,
            string BGR
            ){

            OfferBundle bundle = new OfferBundle();
            bundle.IsDailyDeals = false;
            bundle.IsTrue = true;
            bundle.EndTime = OfferEnd;
            bundle.Cost = Cost; 
            bundle.OldCost = OldCost; 
            bundle.Currency = Currency;
            bundle.Claim = Claim;
            bundle.Title = Title;
            bundle.BackgroundExportName = BGR;

            if (OffersClaimed.Contains(bundle.Claim))
            {
                bundle.Purchased = true;
            }
            if (TimerMath(OfferStart, OfferEnd) == -1)
            {
                bundle.Purchased = true;
            }
            if (HomeMode.HasHeroUnlocked(16000000 + BrawlerID) && Item == ShopItem.GuaranteedHero)
            {
                bundle.Purchased = true;
            }
            if (!HomeMode.HasHeroUnlocked(16000000 + BrawlerID) && Item == ShopItem.HeroPower)
            {
                bundle.Purchased = true;
            }
            if (Item == ShopItem.Skin && (!HomeMode.HasHeroUnlocked(16000000 + Count) || UnlockedSkins.Contains(Extra)))
            {
                bundle.Purchased = true;
            }

            Offer offer = new Offer(Item, Count, (16000000 + BrawlerID), Extra);
            bundle.Items.Add(offer);
            Offer offer2 = new Offer(Item2, Count2, (16000000 + BrawlerID2), Extra2);
            bundle.Items.Add(offer2);
            Offer offer3 = new Offer(Item3, Count3, (16000000 + BrawlerID3), Extra3);
            bundle.Items.Add(offer3);

            OfferBundles.Add(bundle);
        }

        public void LogicDailyData(ByteStream encoder, DateTime utcNow)
        {

            encoder.WriteVInt(utcNow.Year * 1000 + utcNow.DayOfYear); // 0x78d4b8
            encoder.WriteVInt(utcNow.Hour * 3600 + utcNow.Minute * 60 + utcNow.Second); // 0x78d4cc
            encoder.WriteVInt(HomeMode.Avatar.Trophies); // 0x78d4e0
            encoder.WriteVInt(HomeMode.Avatar.HighestTrophies); // 0x78d4f4
            encoder.WriteVInt(HomeMode.Avatar.HighestTrophies); // highest trophy again?
            encoder.WriteVInt(TrophyRoadProgress);
            encoder.WriteVInt(Experience + 1909); // experience

            ByteStreamHelper.WriteDataReference(encoder, Thumbnail);
            ByteStreamHelper.WriteDataReference(encoder, NameColorId);

            encoder.WriteVInt(18); // Played game modes
            for (int i = 0; i < 18; i++)
            {
                encoder.WriteVInt(i);
            }

            encoder.WriteVInt(39); // Selected Skins Dictionary
            for (int i = 0; i < 39; i++)
            {
                encoder.WriteVInt(29);
                try
                {
                    encoder.WriteVInt(SelectedSkins[i]);
                }
                catch
                {
                    encoder.WriteVInt(0);
                    SelectedSkins = new int[] { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
                }
            }


            encoder.WriteVInt(UnlockedSkins.Count); // Played game modes
            foreach (int s in UnlockedSkins)
            {
                ByteStreamHelper.WriteDataReference(encoder, s);
            }

            encoder.WriteVInt(0);

            encoder.WriteVInt(0);
            encoder.WriteVInt(HomeMode.Avatar.HighestTrophies); // 122
            encoder.WriteVInt(0);
            encoder.WriteVInt(0);
            encoder.WriteBoolean(true);
            encoder.WriteVInt(TokenDoublers);
            DateTime targetDateTime = new DateTime(2024, 12, 11, 16, 0, 0);
            TimeSpan timeDifference = targetDateTime - utcNow;
            int secondsRemaining = (int)timeDifference.TotalSeconds;
            encoder.WriteVInt(secondsRemaining); // SESOIN TIME
            encoder.WriteVInt(0);

            DateTime BPtargetDateTime = new DateTime(2024, 12, 10, 16, 0, 0);
            TimeSpan BPtimeDifference = BPtargetDateTime - utcNow;
            int BPsecondsRemaining = (int)BPtimeDifference.TotalSeconds;
            encoder.WriteVInt(BPsecondsRemaining); // BP TIME

            encoder.WriteVInt(0);
            encoder.WriteVInt(0);
            encoder.WriteVInt(0);

            encoder.WriteBoolean(false);
            encoder.WriteBoolean(false);
            encoder.WriteBoolean(true);
            encoder.WriteBoolean(false);
            encoder.WriteVInt(2);
            encoder.WriteVInt(2);
            encoder.WriteVInt(2);
            encoder.WriteVInt(0);
            encoder.WriteVInt(0);

            encoder.WriteVInt(OfferBundles.Count); // Shop offers at 0x78e0c4
            foreach (OfferBundle offerBundle in OfferBundles)
            {
                offerBundle.Encode(encoder);
            }

            encoder.WriteVInt(0);

            encoder.WriteVInt(BattleTokens); // 0x78e228
            encoder.WriteVInt(GetbattleTokensRefreshSeconds()); // 0x78e23c
            encoder.WriteVInt(0); // 0x78e250
            encoder.WriteVInt(0); // 0x78e3a4
            encoder.WriteVInt(0); // 0x78e3a4

            ByteStreamHelper.WriteDataReference(encoder, Character);

            encoder.WriteString("RU");
            encoder.WriteString("SteelBrawl");

            encoder.WriteVInt(6);
            {
                encoder.WriteInt(3);
                encoder.WriteInt(TokenReward); // tokens

                encoder.WriteInt(4);
                encoder.WriteInt(TrophiesReward); // trophies

                encoder.WriteInt(8);
                encoder.WriteInt(StarPointsGained); // trophies

                encoder.WriteInt(7);
                encoder.WriteInt(HomeMode.Avatar.DoNotDisturb ? 1 : 0); // trophies

                encoder.WriteInt(9);
                encoder.WriteInt(1); // trophies

                encoder.WriteInt(10);
                encoder.WriteInt(PowerPlayTrophiesReward); // trophies

            }

            TokenReward = 0;
            TrophiesReward = 0;
            StarTokenReward = 0;
            StarPointsGained = 0;
            PowerPlayTrophiesReward = 0;

            encoder.WriteVInt(0); // array

            encoder.WriteVInt(1); // BrawlPassSeasonData
            {
                encoder.WriteVInt(3);
                encoder.WriteVInt(BrawlPassTokens);
                //encoder.WriteVInt(PremiumPassProgress);
                encoder.WriteBoolean(HasPremiumPass);
                encoder.WriteVInt(0);

                if (encoder.WriteBoolean(true)) // Track 9
                {
                    encoder.WriteLongLong128(PremiumPassProgress);
                }
                if (encoder.WriteBoolean(true)) // Track 10
                {
                    encoder.WriteLongLong128(BrawlPassProgress);
                }
            }

            encoder.WriteVInt(1);
            {
                encoder.WriteVInt(2);
                encoder.WriteVInt(PowerPlayScore);
            }

            if (Quests != null)
            {
                encoder.WriteBoolean(true);
                Quests.Encode(encoder);
            }
            else
            {
                encoder.WriteBoolean(true);
                encoder.WriteVInt(0);
            }

            encoder.WriteBoolean(true);

            encoder.WriteVInt(UnlockedEmotes.Count);
            foreach (int i in UnlockedEmotes)
            {
                encoder.WriteVInt(52);
                encoder.WriteVInt(i);
                encoder.WriteVInt(1);
                encoder.WriteVInt(1);
                encoder.WriteVInt(1);
            }
        }

        public void LogicConfData(ByteStream encoder, DateTime utcNow)
        {
            encoder.WriteVInt(utcNow.Year * 1000 + utcNow.DayOfYear);
            encoder.WriteVInt(100);
            encoder.WriteVInt(10);
            encoder.WriteVInt(30);
            encoder.WriteVInt(3);
            encoder.WriteVInt(80);
            encoder.WriteVInt(10);
            encoder.WriteVInt(40);
            encoder.WriteVInt(1000);
            encoder.WriteVInt(550);
            encoder.WriteVInt(0);
            encoder.WriteVInt(999900);

            encoder.WriteVInt(0); // Array

            encoder.WriteVInt(9);
            for (int i = 1; i <= 9; i++)
                encoder.WriteVInt(i);

            encoder.WriteVInt(Events.Length);
            foreach (EventData data in Events)
            {
                data.IsSecondary = false;
                data.Encode(encoder);
            }

            encoder.WriteVInt(Events.Length);
            foreach (EventData data in Events)
            {
                data.IsSecondary = true;
                data.EndTime.AddSeconds((int)(data.EndTime - DateTime.Now).TotalSeconds);
                data.Encode(encoder);
            }

            encoder.WriteVInt(8);
            {
                encoder.WriteVInt(20);
                encoder.WriteVInt(35);
                encoder.WriteVInt(75);
                encoder.WriteVInt(140);
                encoder.WriteVInt(290);
                encoder.WriteVInt(480);
                encoder.WriteVInt(800);
                encoder.WriteVInt(1250);
            }

            encoder.WriteVInt(8);
            {
                encoder.WriteVInt(1);
                encoder.WriteVInt(2);
                encoder.WriteVInt(3);
                encoder.WriteVInt(4);
                encoder.WriteVInt(5);
                encoder.WriteVInt(10);
                encoder.WriteVInt(15);
                encoder.WriteVInt(20);
            }

            encoder.WriteVInt(3);
            {
                encoder.WriteVInt(10);
                encoder.WriteVInt(30);
                encoder.WriteVInt(80);
            }

            encoder.WriteVInt(3);
            {
                encoder.WriteVInt(6);
                encoder.WriteVInt(20);
                encoder.WriteVInt(60);
            }

            ByteStreamHelper.WriteIntList(encoder, GoldPacksPrice);
            ByteStreamHelper.WriteIntList(encoder, GoldPacksAmount);

            encoder.WriteVInt(2);
            encoder.WriteVInt(200);
            encoder.WriteVInt(20);

            encoder.WriteVInt(8640);
            encoder.WriteVInt(10);
            encoder.WriteVInt(5);

            encoder.WriteBoolean(false);
            encoder.WriteBoolean(false);
            encoder.WriteBoolean(false);

            encoder.WriteVInt(50);
            encoder.WriteVInt(604800);

            encoder.WriteBoolean(true);

            encoder.WriteVInt(0); // Array

            encoder.WriteVInt(2); // IntValueEntries
            {
                encoder.WriteInt(1);
                encoder.WriteInt(41000015); // theme

                encoder.WriteInt(46);
                encoder.WriteInt(1);
            }
        }

        public void Encode(ByteStream encoder)
        {
            DateTime utcNow = DateTime.UtcNow;

            LogicDailyData(encoder, utcNow);
            LogicConfData(encoder, utcNow);

            encoder.WriteVInt(0);
            encoder.WriteVInt(0);

            encoder.WriteLong(HomeId);
            NotificationFactory.Encode(encoder);
            /*encoder.WriteVInt(1);
            {
                encoder.WriteVInt(83);
                encoder.WriteInt(0);
                encoder.WriteBoolean(false);
                encoder.WriteInt(0);
                encoder.WriteString(null);
                encoder.WriteInt(0);
                encoder.WriteStringReference("Добро пожаловать в Simple Brawl");
                encoder.WriteInt(0);
                encoder.WriteStringReference("Также рекомендуем зайти в наш тг канал и чат нажав кнопку ниже!(t.me/simpleservers)");
                encoder.WriteInt(0);
                encoder.WriteStringReference("Перейти");
                encoder.WriteStringReference("pop_up_1920x1235_welcome.png");
                encoder.WriteStringReference("6bb3b752a80107a14671c7bdebe0a1b662448d0c");
                encoder.WriteStringReference("brawlstars://extlink?page=https%3A%2F%2Ft.me%simpleservers%2F");
                encoder.WriteVInt(0);
            }*/

            encoder.WriteVInt(0);
            encoder.WriteBoolean(false);
            encoder.WriteVInt(0);
            encoder.WriteVInt(0);
        }
    }
}
