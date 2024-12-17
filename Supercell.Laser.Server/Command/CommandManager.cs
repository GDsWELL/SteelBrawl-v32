namespace Supercell.Laser.Server.Message
{
    using Supercell.Laser.Logic;
    using Supercell.Laser.Logic.Avatar;
    using Supercell.Laser.Logic.Avatar.Structures;
    using Supercell.Laser.Logic.Battle;
    using Supercell.Laser.Logic.Battle.Objects;
    using Supercell.Laser.Logic.Club;
    using Supercell.Laser.Logic.Command;
    using Supercell.Laser.Logic.Command.Avatar;
    using Supercell.Laser.Logic.Command.Home;
    using Supercell.Laser.Logic.Data;
    using Supercell.Laser.Logic.Data.Helper;
    using Supercell.Laser.Logic.Friends;
    using Supercell.Laser.Logic.Home;
    using Supercell.Laser.Logic.Home.Gatcha;
    using Supercell.Laser.Logic.Home.Items;
    using Supercell.Laser.Logic.Home.Quest;
    using Supercell.Laser.Logic.Home.Structures;
    using Supercell.Laser.Logic.Listener;
    using Supercell.Laser.Logic.Message;
    using Supercell.Laser.Logic.Message.Account;
    using Supercell.Laser.Logic.Message.Account.Auth;
    using Supercell.Laser.Logic.Message.Battle;
    using Supercell.Laser.Logic.Message.Club;
    using Supercell.Laser.Logic.Message.Friends;
    using Supercell.Laser.Logic.Message.Home;
    using Supercell.Laser.Logic.Message.Ranking;
    using Supercell.Laser.Logic.Message.Security;
    using Supercell.Laser.Logic.Message.Team;
    using Supercell.Laser.Logic.Message.Team.Stream;
    using Supercell.Laser.Logic.Message.Udp;
    using Supercell.Laser.Logic.Stream;
    using Supercell.Laser.Logic.Stream.Entry;
    using Supercell.Laser.Logic.Team;
    using Supercell.Laser.Logic.Team.Stream;
    using Supercell.Laser.Logic.Util;
    using Supercell.Laser.Server.Database;
    using Supercell.Laser.Server.Database.Cache;
    using Supercell.Laser.Server.Database.Models;
    using Supercell.Laser.Server.Logic;
    using Supercell.Laser.Server.Logic.Game;
    using Supercell.Laser.Server.Networking;
    using Supercell.Laser.Server.Networking.Security;
    using Supercell.Laser.Server.Networking.Session;
    using Supercell.Laser.Server.Networking.UDP.Game;
    using Supercell.Laser.Server.Settings;
    using Supercell.Laser.Titan.Debug;
    using System;
    //using System.Diagnostics;
    using System.Linq;
    using System.Security.Cryptography;
    using System.Security.Principal;
    using System.Xml.Linq;

    public class CommandManager
    {
        public Connection Connection { get; }

        public HomeMode HomeMode;


        public CommandManager(HomeMode homeMode, Connection connection)
        {
            HomeMode = homeMode;
            Connection = connection;
        }


        public bool ReceiveCommand(Command command)
        {
            try
            {
                switch (command.GetCommandType())
                {
                    case 500:
                        return LogicGatchaReceived((LogicGatchaCommand)command);
                    case 503:
                        return LogicClaimDailyRewardReceived((LogicClaimDailyRewardCommand)command);
                    case 505:
                        return LogicSetPlayerThumbnailReceived((LogicSetPlayerThumbnailCommand)command);
                    case 506:
                        return LogicSelectSkinReceived((LogicSelectSkinCommand)command);
                    case 509:
                        return LogicPurchaseDoubleCoinsReceived((LogicPurchaseDoubleCoinsCommand)command);
                    case 514:
                        return LogicDeleteNotificationReceived((LogicDeleteNotificationCommand)command);
                    case 515:
                        return LogicClearShopTickersReceived((LogicClearShopTickersCommand)command);
                    case 520:
                        return LogicLevelUpReceived((LogicLevelUpCommand)command);
                    case 517:
                        return LogicClaimRankUpRewardReceived((LogicClaimRankUpRewardCommand)command);
                    case 519:
                        return LogicPurchaseOfferReceived((LogicPurchaseOfferCommand)command);
                    case 521:
                        return LogicPurchaseHeroLvlUpMaterialReceived((LogicPurchaseHeroLvlUpMaterialCommand)command);
                    case 522:
                        return LogicHeroSeenReceived((LogicHeroSeenCommand)command);
                    case 525:
                        return LogicSelectCharacterReceived((LogicSelectCharacterCommand)command);
                    case 527:
                        return LogicSetPlayerNameColorReceived((LogicSetPlayerNameColorCommand)command);
                    case 528:
                        return LogicViewInboxNotificationReceived((LogicViewInboxNotificationCommand)command);
                    case 529:
                        return LogicSelectStarPowerReceived((LogicSelectStarPowerCommand)command);
                    case 533:
                        return LogicQuestsSeenReceived((LogicQuestsSeenCommand)command);
                    case 534:
                        return LogicPurchaseBrawlPassReceived((LogicPurchaseBrawlPassCommand)command);
                    case 535:
                        return LogicClaimTailRewardReceived((LogicClaimTailRewardCommand)command);
                    case 536:
                        return LogicPurchaseBrawlPassProgressReceived((LogicPurchaseBrawlPassProgressCommand)command);
                    default:
                        Logger.Print($"CommandManager::ReceiveCommand - no case for {command.GetType().Name} ({command.GetCommandType()})");
                        return false;
                }
            }
            catch (Exception e)
            {
                return false;
            }
        }

        private bool LogicHeroSeenReceived(LogicHeroSeenCommand command)
        {
            if (command.CharacterId == 0) return false;
            Hero h = HomeMode.Avatar.GetHero(command.CharacterId);
            if (h == null) return false;
            h.IsNew = false;
            return true;
        }

        private bool LogicPurchaseBrawlPassProgressReceived(LogicPurchaseBrawlPassProgressCommand command)
        {
            if (HomeMode.Avatar.UseDiamonds(30))
            {
                for (int x = 966; x < 1036 + 1; x++)
                {
                    MilestoneData milestoneData = DataTables.Get(DataType.Milestone).GetDataByGlobalId<MilestoneData>(GlobalId.CreateGlobalId((int)DataType.Milestone, x));
                    if (milestoneData.ProgressStart <= HomeMode.Home.BrawlPassTokens && (milestoneData.ProgressStart + milestoneData.Progress) > HomeMode.Home.BrawlPassTokens)
                    {
                        HomeMode.Home.BrawlPassTokens = milestoneData.ProgressStart + milestoneData.Progress;
                        return true;
                    }
                }
            }
            return false;
        }

        private bool LogicViewInboxNotificationReceived(LogicViewInboxNotificationCommand command)
        {
            if (command.NotificationIndex < 0) return false;
            if (command.NotificationIndex > HomeMode.Home.NotificationFactory.GetIndex()) return false;
            if (HomeMode.Home.NotificationFactory.NotificationList[command.NotificationIndex].IsViewed) return false;
            if (HomeMode.Home.NotificationFactory.NotificationList[command.NotificationIndex].Id == 79)
            {
                foreach (int a in HomeMode.Home.NotificationFactory.NotificationList[command.NotificationIndex].StarpointsAwarded)
                {
                    HomeMode.Avatar.StarPoints += a;
                }
            }
            if (HomeMode.Home.NotificationFactory.NotificationList[command.NotificationIndex].Id == 89)
            {
                LogicGiveDeliveryItemsCommand delivery = new LogicGiveDeliveryItemsCommand();
                DeliveryUnit unit = new DeliveryUnit(100);
                GatchaDrop reward = new GatchaDrop(8);
                reward.Count = HomeMode.Home.NotificationFactory.NotificationList[command.NotificationIndex].DonationCount;
                unit.AddDrop(reward);
                delivery.DeliveryUnits.Add(unit);
                delivery.Execute(HomeMode);

                AvailableServerCommandMessage message = new AvailableServerCommandMessage();
                message.Command = delivery;
                HomeMode.GameListener.SendMessage(message);
            }
             HomeMode.Home.NotificationFactory.NotificationList[command.NotificationIndex].IsViewed = true;
            return true;
        }
        private bool LogicDeleteNotificationReceived(LogicDeleteNotificationCommand command)
        {
            if (command.NotificationIndex < 0) return false;
            if (command.NotificationIndex > HomeMode.Home.NotificationFactory.GetIndex()) return false;
            if (HomeMode.Home.NotificationFactory.NotificationList[command.NotificationIndex].IsViewed) return false;
            HomeMode.Home.NotificationFactory.NotificationList.Remove(HomeMode.Home.NotificationFactory.NotificationList[command.NotificationIndex]);
            return true;
        }
        private bool LogicClaimTailRewardReceived(LogicClaimTailRewardCommand command)
        {
            if (HomeMode.Home.BrawlPassTokens < (500)) return false;

            HomeMode.Home.BrawlPassTokens -= 500;
            LogicGiveDeliveryItemsCommand delivery = new LogicGiveDeliveryItemsCommand();
            DeliveryUnit unit = new DeliveryUnit(12);
            HomeMode.SimulateGatcha(unit);
            delivery.DeliveryUnits.Add(unit);
            delivery.Execute(HomeMode);

            AvailableServerCommandMessage message = new AvailableServerCommandMessage();
            message.Command = delivery;
            HomeMode.GameListener.SendMessage(message);
            return true;
        }

        private bool LogicSelectStarPowerReceived(LogicSelectStarPowerCommand command)
        {
            CharacterData hero;
            CardData card = DataTables.Get(DataType.Card).GetDataByGlobalId<CardData>(GlobalId.CreateGlobalId(29, command.StarpowerInstanceId));
            if (card == null) return false;
            if (card.MetaType != 5)
            {
                string m = card.Name.Replace("_2", "");
                m = m.Replace("_3", "");
                CardData card1 = DataTables.Get(DataType.Card).GetData<CardData>(m);
                CardData card2 = DataTables.Get(DataType.Card).GetData<CardData>(m + "_2");
                CardData card3 = DataTables.Get(DataType.Card).GetData<CardData>(m + "_3");
                hero = DataTables.Get(DataType.Character).GetData<CharacterData>(card.Name.Split("_")[0]);
                Hero h = HomeMode.Avatar.GetHero(hero.GetGlobalId());
                h.HasStarpower = true;

                HomeMode.Avatar.SelectedStarpowers.Remove(card1.GetGlobalId());
                HomeMode.Avatar.SelectedStarpowers.Remove(card2.GetGlobalId());
                if (card3 != null)
                {
                    HomeMode.Avatar.SelectedStarpowers.Remove(card3.GetGlobalId());
                }


                HomeMode.Avatar.SelectedStarpowers.Add(card.GetGlobalId());
            }
            else
            {
                string[] cards = { "GrowBush", "Shield", "Heal", "Jump", "ShootAround", "DestroyPet", "PetSlam", "Slow", "Push", "Dash", "SpeedBoost", "BurstHeal", "Spin", "Teleport", "Immunity", "Trail", "Totem", "Grab", "Swing", "Vision", "Regen", "HandGun", "Promote", "Sleep", "Slow", "Reload", "Reload", "Fake", "Trampoline", "Explode", "Blink", "PoisonTrigger", "Barrage", "Focus", "MineTrigger", "Reload", "Seeker", "Meteor", "HealPotion", "Stun", "TurretBuff" };
                CharacterData cd = DataTables.Get(DataType.Character).GetData<CharacterData>(card.Name.Split("_")[0]);
                hero = cd;
                CardData WildCard = null;
                foreach (string cardname in cards)
                {
                    string n = char.ToUpper(cd.Name[0]) + cd.Name.Substring(1);
                    Console.WriteLine(n + "" + cardname);
                    WildCard = DataTables.Get(DataType.Card).GetData<CardData>(n + "_" + cardname);
                    if (WildCard != null || WildCard == card)
                    {
                        break;
                    }
                }
                if (WildCard != null)
                {
                    HomeMode.Avatar.SelectedStarpowers.Remove(WildCard.GetGlobalId());
                    HomeMode.Avatar.SelectedStarpowers.Add(card.GetGlobalId());
                }
            }
            if (HomeMode.Avatar.TeamId > 0)
            {
                TeamEntry team = Teams.Get(HomeMode.Avatar.TeamId);
                if (team == null) return true;
                TeamMember me = team.GetMember(HomeMode.Avatar.AccountId);
                if (me == null) return true;
                if (me.CharacterId != hero.GetGlobalId()) return true;
                if (card.MetaType != 5)
                    me.Starpower = card.GetGlobalId();
                else
                    me.Gadget = card.GetGlobalId();
                team.TeamUpdated();
            }

            return true;
        }

        private bool LogicQuestsSeenReceived(LogicQuestsSeenCommand command)
        {
            foreach (Quest quest in HomeMode.Home.Quests.QuestList.ToArray())
            {
                quest.QuestSeen = true;
            }
            return true;
        }

        private bool LogicPurchaseBrawlPassReceived(LogicPurchaseBrawlPassCommand command)
        {
            if (HomeMode.Avatar.UseDiamonds(169))
            {
                HomeMode.Home.HasPremiumPass = true;
                if (HomeMode.Avatar.AllianceId > 0)
                {
                    Alliance alliance = Alliances.Load(HomeMode.Avatar.AllianceId);
                    AllianceMember member = alliance.GetMemberById(HomeMode.Avatar.AccountId);
                    member.DisplayData.HighNameColorId = HomeMode.Home.NameColorId;
                }
                foreach (Friend friend in HomeMode.Avatar.Friends)
                {
                    Friend entry = friend.Avatar.GetFriendById(HomeMode.Avatar.AccountId);
                    entry.DisplayData.HighNameColorId = HomeMode.Home.NameColorId;
                    if (LogicServerListener.Instance.IsPlayerOnline(friend.Avatar.AccountId))
                    {
                        FriendListUpdateMessage update = new()
                        {
                            Entry = entry
                        };
                        LogicServerListener.Instance.GetGameListener(friend.AccountId).SendTCPMessage(update);
                    }

                }
                return true;
            }

            return false;
        }
        private bool LogicGatchaReceived(LogicGatchaCommand command)
        {
            if (command.BoxIndex == 3)
            {
                if (!HomeMode.Avatar.UseDiamonds(80)) return false;

                LogicGiveDeliveryItemsCommand LogicGiveDeliveryItems = new();
                DeliveryUnit unit = new(11);
                HomeMode.SimulateGatcha(unit);
                LogicGiveDeliveryItems.DeliveryUnits.Add(unit);
                LogicGiveDeliveryItems.Execute(HomeMode);

                AvailableServerCommandMessage message = new()
                {
                    Command = LogicGiveDeliveryItems
                };
                HomeMode.GameListener.SendMessage(message);
            }
            else if (command.BoxIndex == 1)
            {
                if (!HomeMode.Avatar.UseDiamonds(30)) return false;

                LogicGiveDeliveryItemsCommand LogicGiveDeliveryItems = new();
                DeliveryUnit unit = new(12);
                HomeMode.SimulateGatcha(unit);
                LogicGiveDeliveryItems.DeliveryUnits.Add(unit);
                LogicGiveDeliveryItems.Execute(HomeMode);

                AvailableServerCommandMessage message = new()
                {
                    Command = LogicGiveDeliveryItems
                };
                HomeMode.GameListener.SendMessage(message);
            }
            else if (command.BoxIndex == 4)
            {
                if (!HomeMode.Avatar.UseStarTokens(10)) return false;

                LogicGiveDeliveryItemsCommand LogicGiveDeliveryItems = new();
                DeliveryUnit unit = new(12);
                HomeMode.SimulateGatcha(unit);
                LogicGiveDeliveryItems.DeliveryUnits.Add(unit);
                LogicGiveDeliveryItems.Execute(HomeMode);

                AvailableServerCommandMessage message = new()
                {
                    Command = LogicGiveDeliveryItems
                };
                HomeMode.GameListener.SendMessage(message);
            }
            else if (command.BoxIndex == 5)
            {
                if (!HomeMode.Avatar.UseTokens(100)) return false;

                LogicGiveDeliveryItemsCommand LogicGiveDeliveryItems = new();
                DeliveryUnit unit = new(10);
                HomeMode.SimulateGatcha(unit);
                LogicGiveDeliveryItems.DeliveryUnits.Add(unit);
                LogicGiveDeliveryItems.Execute(HomeMode);

                AvailableServerCommandMessage message = new()
                {
                    Command = LogicGiveDeliveryItems
                };
                HomeMode.GameListener.SendMessage(message);
            }
            else
            {

            }

            return true;
        }
        private bool LogicSelectSkinReceived(LogicSelectSkinCommand command)
        {
            int skin = GlobalId.CreateGlobalId(29, command.SkinId);
            Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------1");
            int skind = GlobalId.CreateGlobalId(44, command.SkinId);
            Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------2");
            SkinData skinData = DataTables.Get(DataType.Skin).GetDataByGlobalId<SkinData>(skin);
            Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------3");
            if (command.SkinId != 63){
                Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------31");
                foreach (int _skin in HomeMode.Home.UnlockedSkins){
                    Console.WriteLine($"HomeMode.Home.UnlockedSkins - {_skin}");
                }
                Console.WriteLine($"skin - {skin}");
                Console.WriteLine($"!sk");
                bool _x = !skinData.Name.EndsWith("Default");
                Console.WriteLine($"!sk");
                bool _y = !HomeMode.Home.UnlockedSkins.Contains(skin);
                Console.WriteLine($"!sk");
                if (!skinData.Name.EndsWith("Default") && !HomeMode.Home.UnlockedSkins.Contains(skin)) return false;
                Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------32");
            }
            Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------4");
            //Console.WriteLine(skinData.Conf);
            Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------5");
            SkinConfData sk = DataTables.Get(DataType.SkinConf).GetData<SkinConfData>(skinData.Conf);
            Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------6");
            CharacterData c = DataTables.Get(DataType.Character).GetData<CharacterData>(sk.Character);
            Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------7");
            Console.WriteLine(c.GetGlobalId());
            Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------8");
            HomeMode.Home.SelectedSkins[c.GetInstanceId()] = command.SkinId;
            Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------9");
            if (HomeMode.Avatar.TeamId > 0)
            {
                TeamEntry team = Teams.Get(HomeMode.Avatar.TeamId);
                Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------10");
                if (team == null)
                {
                    return true;
                }
                Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------11");
                TeamMember m = team.GetMember(HomeMode.Avatar.AccountId);
                if (m == null)
                {
                    return true;
                }
                Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------12");
                m.SkinId = skin;
                Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------13");
                team.TeamUpdated();
            }
            Console.WriteLine("HUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIII-------------------14");
            return true;
        }

        private bool LogicClaimDailyRewardReceived(LogicClaimDailyRewardCommand command)
        {
            if (Events.CollectEvent(HomeMode.Avatar.AccountId, command.Slot))
            {
                if (command.Slot != 7)
                {
                    HomeMode.Avatar.AddTokens(10);
                }
                else
                {
                    HomeMode.Avatar.AddTokens(10);
                    //HomeMode.Home.Tickets += 1;
                    //TODO:
                }
                return true;
            }
            return false;
        }
        private bool LogicLevelUpReceived(LogicLevelUpCommand command)
        {
            Hero hero = HomeMode.Avatar.GetHero(command.CharacterId);
            if (hero == null) return false;

            if (hero.PowerLevel > Hero.UpgradeCostTable.Length) return false;
            if (hero.PowerPoints < Hero.UpgradePowerPointsTable[hero.PowerLevel]) return false;

            if (!HomeMode.Avatar.UseGold(Hero.UpgradeCostTable[hero.PowerLevel])) return false;

            hero.PowerLevel++;

            return true;
        }
        private bool LogicPurchaseOfferReceived(LogicPurchaseOfferCommand command)
        {
            HomeMode.Home.PurchaseOffer(command.OfferIndex);

            return true;
        }
        private bool LogicSelectCharacterReceived(LogicSelectCharacterCommand command)
        {
            int globalId = GlobalId.CreateGlobalId(16, command.CharacterInstanceId);
            if (HomeMode.Avatar.HasHero(globalId))
            {
                HomeMode.Home.CharacterId = globalId;
                HomeMode.CharacterChanged.Invoke(globalId);
                if (HomeMode.Avatar.TeamId > 0)
                {
                    Hero hero = HomeMode.Avatar.GetHero(globalId);
                    TeamEntry team = Teams.Get(HomeMode.Avatar.TeamId);
                    TeamMember member = team.GetMember(HomeMode.Avatar.AccountId);
                    if (hero.HasStarpower)
                    {
                        CardData card = null;
                        CharacterData cd = DataTables.Get(DataType.Character).GetDataByGlobalId<CharacterData>(hero.CharacterId);
                        card = DataTables.Get(DataType.Card).GetData<CardData>(cd.Name + "_unique");
                        CardData card2 = DataTables.Get(DataType.Card).GetData<CardData>(cd.Name + "_unique_2");
                        if (HomeMode.Avatar.SelectedStarpowers.Contains(card.GetGlobalId()))
                        {
                            member.HeroLevel = 9;
                            member.Starpower = card.GetGlobalId();
                        }
                        else if (HomeMode.Avatar.SelectedStarpowers.Contains(card2.GetGlobalId()))
                        {
                            member.HeroLevel = 9;
                            member.Starpower = card2.GetGlobalId();
                        }
                        else if (HomeMode.Avatar.Starpowers.Contains(card.GetGlobalId()))
                        {
                            member.HeroLevel = 9;
                            member.Starpower = card.GetGlobalId();
                        }
                        else if (HomeMode.Avatar.Starpowers.Contains(card2.GetGlobalId()))
                        {
                            member.HeroLevel = 9;
                            member.Starpower = card2.GetGlobalId();
                        }
                        else
                        {
                            member.Starpower = 0;
                        }

                    }
                    else
                    {
                        member.Starpower = 0;
                    }
                    if (hero.PowerLevel > 5)
                    {
                        string[] cards = { "GrowBush", "Shield", "Heal", "Jump", "ShootAround", "DestroyPet", "PetSlam", "Slow", "Push", "Dash", "SpeedBoost", "BurstHeal", "Spin", "Teleport", "Immunity", "Trail", "Totem", "Grab", "Swing", "Vision", "Regen", "HandGun", "Promote", "Sleep", "Slow", "Reload", "Fake", "Trampoline", "Explode", "Blink", "PoisonTrigger", "Barrage", "Focus", "MineTrigger", "Reload", "Seeker", "Meteor", "HealPotion", "Stun", "TurretBuff" };
                        CharacterData cd = DataTables.Get(DataType.Character).GetDataByGlobalId<CharacterData>(hero.CharacterId);
                        CardData WildCard = null;
                        foreach (string cardname in cards)
                        {
                            string n = char.ToUpper(cd.Name[0]) + cd.Name.Substring(1);
                            Console.WriteLine(n + "_" + cardname);
                            WildCard = DataTables.Get(DataType.Card).GetData<CardData>(n + "_" + cardname);
                            if (WildCard != null)
                            {
                                if (HomeMode.Avatar.Starpowers.Contains(WildCard.GetGlobalId()))
                                {
                                    member.Gadget = WildCard.GetGlobalId();
                                    break;
                                }
                                
                            }
                        }
                    }
                    else
                    {
                        member.Gadget = 0;
                    }
                    member.SkinId = GlobalId.CreateGlobalId(29, HomeMode.Home.SelectedSkins[GlobalId.GetInstanceId(HomeMode.Home.CharacterId)]);
                    team.TeamUpdated();
                }
                return true;
            }


            return false;
        }
        private bool LogicSetPlayerThumbnailReceived(LogicSetPlayerThumbnailCommand command)
        {
            if (command.ThumbnailInstanceId < 0) return false;
            if (command.ThumbnailInstanceId > DataTables.Get(DataType.PlayerThumbnail).Count) return false;

            HomeMode.Home.ThumbnailId = GlobalId.CreateGlobalId(28, command.ThumbnailInstanceId);
            if (HomeMode.Avatar.AllianceId > 0)
            {
                Alliance alliance = Alliances.Load(HomeMode.Avatar.AllianceId);
                AllianceMember member = alliance.GetMemberById(HomeMode.Avatar.AccountId);
                member.DisplayData.ThumbnailId = HomeMode.Home.ThumbnailId;
                AllianceDataMessage data = new()
                {
                    Alliance = alliance,
                    IsMyAlliance = true
                };
                //alliance.SendToAlliance(data);
            }
            foreach (Friend friend in HomeMode.Avatar.Friends)
            {
                Friend entry = friend.Avatar.GetFriendById(HomeMode.Avatar.AccountId);
                entry.DisplayData.ThumbnailId = HomeMode.Home.ThumbnailId;
                if (LogicServerListener.Instance.IsPlayerOnline(friend.Avatar.AccountId))
                {
                    FriendListUpdateMessage update = new()
                    {
                        Entry = entry
                    };
                    LogicServerListener.Instance.GetGameListener(friend.AccountId).SendTCPMessage(update);
                }

            }

            return true;
        }
        private bool LogicSetPlayerNameColorReceived(LogicSetPlayerNameColorCommand command)
        {
            if (command.NameColorInstanceId < 0) return false;
            if (command.NameColorInstanceId > (DataTables.Get(DataType.NameColor).Count)) return false;

            HomeMode.Home.NameColorId = GlobalId.CreateGlobalId(43, command.NameColorInstanceId);
            if (HomeMode.Avatar.AllianceId > 0)
            {
                Alliance alliance = Alliances.Load(HomeMode.Avatar.AllianceId);
                if (alliance == null) 
                {
                    HomeMode.Avatar.AllianceId = -1;
                    return true;
                }
                AllianceMember member = alliance.GetMemberById(HomeMode.Avatar.AccountId);
                if (member == null)
                {
                    return true;
                }
                member.DisplayData.NameColorId = HomeMode.Home.NameColorId;
                AllianceDataMessage data = new()
                {
                    Alliance = alliance,
                    IsMyAlliance = true
                };
                //alliance.SendToAlliance(data);
            }
            foreach (Friend friend in HomeMode.Avatar.Friends)
            {
                Friend entry = friend.Avatar.GetFriendById(HomeMode.Avatar.AccountId);
                entry.DisplayData.NameColorId = HomeMode.Home.NameColorId;
                if (LogicServerListener.Instance.IsPlayerOnline(friend.Avatar.AccountId))
                {
                    FriendListUpdateMessage update = new()
                    {
                        Entry = entry
                    };
                    LogicServerListener.Instance.GetGameListener(friend.AccountId).SendTCPMessage(update);
                }

            }

            return true;
        }
        private bool LogicClearShopTickersReceived(LogicClearShopTickersCommand command)
        {
            OfferBundle[] bundles = HomeMode.Home.OfferBundles.ToArray();
            foreach (OfferBundle bundle in bundles)
            {
                bundle.State = 2;
            }

            return true;
        }


        private bool LogicPurchaseDoubleCoinsReceived(LogicPurchaseDoubleCoinsCommand command)
        {
            if (HomeMode.Avatar.UseDiamonds(40))
            {
                HomeMode.Home.TokenDoublers += 1000;
                return true;
            }

            return false;
        }
        private bool LogicPurchaseHeroLvlUpMaterialReceived(LogicPurchaseHeroLvlUpMaterialCommand command)
        {
            if (command.PackIndex < 0 || command.PackIndex > ClientHome.GoldPacksAmount.Length) return false;

            if (!HomeMode.Avatar.UseDiamonds(ClientHome.GoldPacksPrice[command.PackIndex])) return false;

            HomeMode.Avatar.AddGold(ClientHome.GoldPacksAmount[command.PackIndex]);

            return true;
        }
        private bool LogicClaimRankUpRewardReceived(LogicClaimRankUpRewardCommand command)
        {
            Debugger.Print($"Claim rankup reward: milestone: {command.MilestoneId}, data: {command.UnknownDataId}, Unk2: {command.Unk2}, Unk3: {command.Unk3}");

            if (command.MilestoneId == 6)
            {
                string name = $"goal_6_{HomeMode.Home.TrophyRoadProgress - 1}";


                MilestoneData milestoneData = DataTables.Get(DataType.Milestone).GetData<MilestoneData>(name);
                if (milestoneData == null)
                {
                    Debugger.Error($"Milestone data is NULL - {name}");
                    return false;
                }

                if (HomeMode.Avatar.HighestTrophies < milestoneData.Progress + milestoneData.ProgressStart)
                {
                    Debugger.Warning($"current progress: {HomeMode.Avatar.HighestTrophies}, required progress: {milestoneData.Progress + milestoneData.ProgressStart}");
                    return false;
                }

                if (command.ProcessReward(HomeMode, milestoneData, false, 6, HomeMode.Home.TrophyRoadProgress + 1, false) != 0) return false;

                HomeMode.Home.TrophyRoadProgress++;
            }
            else if (command.MilestoneId == 9 || command.MilestoneId == 10)
            {
                string name = $"Goal_{command.MilestoneId}_3_{(command.MilestoneId == 10 ? command.RequieredMilestone : command.RequieredMilestone)}";
                if (command.MilestoneId == 9 && !HomeMode.Home.HasPremiumPass)
                {
                    return false;
                }

                MilestoneData milestoneData = DataTables.Get(DataType.Milestone).GetData<MilestoneData>(name);
                if (milestoneData == null)
                {
                    Debugger.Error($"Milestone data is NULL - {name}");
                    return false;
                }

                if (HomeMode.Home.BrawlPassTokens < milestoneData.Progress + milestoneData.ProgressStart)
                {
                    Debugger.Warning($"current progress: {HomeMode.Home.BrawlPassTokens}, required progress: {milestoneData.Progress + milestoneData.ProgressStart}");
                    return false;
                }
                if (command.MilestoneId == 9 && LogicBitHelper.Get(HomeMode.Home.PremiumPassProgress, command.RequieredMilestone + 2))
                    return false;
                if (command.MilestoneId == 10 && LogicBitHelper.Get(HomeMode.Home.BrawlPassProgress, command.RequieredMilestone + 2))
                    return false;

                if (command.ProcessReward(HomeMode, milestoneData, false, command.MilestoneId, command.MilestoneId == 10 ? command.RequieredMilestone + 2 : command.RequieredMilestone + 2, true) != 0) return false;

                if (command.MilestoneId == 9)
                    HomeMode.Home.PremiumPassProgress = LogicBitHelper.Set(HomeMode.Home.PremiumPassProgress, command.RequieredMilestone + 2, true);
                else
                    HomeMode.Home.BrawlPassProgress = LogicBitHelper.Set(HomeMode.Home.BrawlPassProgress, command.RequieredMilestone + 2, true);
            }
            else
            {
                return false;
            }

            return true;
        }
    }
}
