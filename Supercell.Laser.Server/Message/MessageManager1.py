namespace Supercell.Laser.Server.Message
{
    using Supercell.Laser.Logic.Avatar;
    using Supercell.Laser.Server.Utils;
    using Supercell.Laser.Logic.Avatar.Structures;
    using Supercell.Laser.Logic.Club;
    using Supercell.Laser.Logic.Command.Avatar;
    using Supercell.Laser.Logic.Data;
    using Supercell.Laser.Logic.Friends;
    using Supercell.Laser.Logic.Home;
    using Supercell.Laser.Logic.Home.Structures;
    using Supercell.Laser.Logic.Listener;
    using Supercell.Laser.Logic.Message.Account;
    using Supercell.Laser.Logic.Message.Club;
    using Supercell.Laser.Logic.Message.Friends;
    using Supercell.Laser.Logic.Message.Home;
    using Supercell.Laser.Logic.Message.Ranking;
    using Supercell.Laser.Logic.Message.Security;
    using Supercell.Laser.Logic.Message.Team;
    using Supercell.Laser.Logic.Message.Udp;
    using Supercell.Laser.Logic.Stream.Entry;
    using Supercell.Laser.Logic.Team;
    using Supercell.Laser.Server.Database;
    using Supercell.Laser.Server.Database.Models;
    using Supercell.Laser.Server.Logic.Game;
    using Supercell.Laser.Server.Networking;
    using Supercell.Laser.Server.Networking.Session;
    using Supercell.Laser.Server.Settings;
    using Supercell.Laser.Server.Logic;
    using System.Diagnostics;
    using Supercell.Laser.Server.Database.Cache;
    using Supercell.Laser.Logic.Util;
    using Supercell.Laser.Logic.Battle;
    using Supercell.Laser.Logic.Message.Battle;
    using Supercell.Laser.Server.Networking.UDP.Game;
    using Supercell.Laser.Server.Networking.Security;
    using Supercell.Laser.Logic.Home.Items;
    using Supercell.Laser.Logic.Team.Stream;
    using Supercell.Laser.Logic.Message.Team.Stream;
    using Supercell.Laser.Logic.Message;
    using Supercell.Laser.Logic.Message.Account.Auth;
    using Supercell.Laser.Logic.Message.Latency;
    using Supercell.Laser.Logic.Command;
    using Supercell.Laser.Logic.Battle.Structures;
    using Newtonsoft.Json.Linq;
    using System.Reflection;
    using System.Numerics;
    using Supercell.Laser.Logic.Home.Quest;
    using Supercell.Laser.Logic.Data.Helper;
    using System.Linq;
    using Supercell.Laser.Logic.Command.Home;
    using Supercell.Laser.Logic.Message.Api;
    using Ubiety.Dns.Core;
    using System.Xml.Linq;
    using Microsoft.VisualBasic;
    using Org.BouncyCastle.Cms;

    public class MessageManager
    {
        public Connection Connection { get; }

        public HomeMode HomeMode;

        public CommandManager CommandManager;

        private DateTime LastKeepAlive;

        public MessageManager(Connection connection)
        {
            Connection = connection;
            LastKeepAlive = DateTime.UtcNow;
        }


        public bool IsAlive()
        {
            return (int)(DateTime.UtcNow - LastKeepAlive).TotalSeconds < 30;
        }
        public string GetPingIconByMs(int ms)
        {
            string str = "▂   ";
            if (ms <= 75)
            {
                str = "▂▄▆█";
            }
            else if (ms <= 125)
            {
                str = "▂▄▆ ";
            }
            else if (ms <= 300)
            {
                str = "▂▄  ";
            }
            return str;
        }

        public void ShowLobbyInfo()
        {
            string abd = $"Connection: {GetPingIconByMs(0)} (---ms)\n";
            if (Connection.Ping != 0)
            {
                abd = $"Connection: {GetPingIconByMs(Connection.Ping)} ({Connection.Ping}ms)\n";
            }
            
            LobbyInfoMessage b = new()
            {
                LobbyData = $"AlahBrawl\n<cff1f00>t<cff3f00>.<cff5f00>m<cff7f00>e<cff9f00>/<cffbf00>a<cffdf00>l<cffff00>a<cdfff00>h<cbfff00>s<c9fff00>e<c7fff00>r<c5fff00>v<c3fff00>e<c1fff00>r<c00ff00>s</c>\n{abd}Players Online: {Sessions.Count}\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nzachem ti eto chitaeh'",
                PlayersCount = 0
            };
            Connection.Send(b);
        }

        public void ReceiveMessage(GameMessage message)
        {
            switch (message.GetMessageType())
            {
                case 10100:
                    ClientHelloReceived((ClientHelloMessage)message);
                    break;
                case 10101:
                    LoginReceived((AuthenticationMessage)message);
                    break;
                case 10107:
                    ClientCapabilitesReceived((ClientCapabilitiesMessage)message);
                    //Connection.Send(new StartLatencyTestRequestMessage());
                    break;
                case 10108:
                    LastKeepAlive = DateTime.UtcNow;
                    Connection.Send(new KeepAliveServerMessage());
                    ShowLobbyInfo();
                    if (!Sessions.IsSessionActive(HomeMode.Avatar.AccountId))
                    {
                        Sessions.Create(HomeMode, Connection);
                    }
                    break;
                case 10110:
                    ShowLobbyInfo();
                    break;
                case 10119:
                    ReportAllianceStreamReceived((ReportAllianceStreamMessage)message);
                    break;
                case 10212:
                    ChangeName((ChangeAvatarNameMessage)message);
                    break;
                case 10177:
                    ClientInfoReceived((ClientInfoMessage)message);
                    break;
                case 10501:
                    AcceptFriendReceived((AcceptFriendMessage)message);
                    break;
                case 10502:
                    AddFriendReceived((AddFriendMessage)message);
                    break;
                case 10504:
                    AskForFriendListReceived((AskForFriendListMessage)message);
                    break;
                case 10506:
                    RemoveFriendReceived((RemoveFriendMessage)message);
                    break;
                case 10576:
                    SetBlockFriendRequestsReceived((SetBlockFriendRequestsMessage)message);
                    break;
                case 10555:
                    break;
                case 14101:
                    GoHomeReceived((GoHomeMessage)message);
                    break;
                case 14102:
                    EndClientTurnReceived((EndClientTurnMessage)message);
                    break;
                case 14103:
                    MatchmakeRequestReceived((MatchmakeRequestMessage)message);
                    break;
                case 14104:
                    StartSpectateReceived((StartSpectateMessage)message);
                    break;
                case 14106:
                    CancelMatchMaking((CancelMatchmakingMessage)message);
                    break;
                case 14107:
                    StopSpectateReceived((StopSpectateMessage)message);
                    break;
                case 14109:
                    GoHomeFromOfflinePractiseReceived((GoHomeFromOfflinePractiseMessage)message);
                    break;
                case 14110:
                    AskForBattleEndReceived((AskForBattleEndMessage)message);
                    break;
                case 14113:
                    GetPlayerProfile((GetPlayerProfileMessage)message);
                    break;
                case 14166:
                    break;
                case 14277:
                    GetSeasonRewardsReceived((GetSeasonRewardsMessage)message);
                    break;
                case 14301:
                    CreateAllianceReceived((CreateAllianceMessage)message);
                    break;
                case 14302:
                    AskForAllianceDataReceived((AskForAllianceDataMessage)message);
                    break;
                case 14303:
                    AskForJoinableAllianceListReceived((AskForJoinableAllianceListMessage)message);
                    break;
                case 14305:
                    JoinAllianceReceived((JoinAllianceMessage)message);
                    break;
                case 14306:
                    ChangeAllianceMemberRoleReceived((ChangeAllianceMemberRoleMessage)message);
                    break;
                case 14307:
                    KickAllianceMemberReceived((KickAllianceMemberMessage)message);
                    break;
                case 14308:
                    LeaveAllianceReceived((LeaveAllianceMessage)message);
                    break;
                case 14315:
                    ChatToAllianceStreamReceived((ChatToAllianceStreamMessage)message);
                    break;
                case 14316:
                    ChangeAllianceSettingsReceived((ChangeAllianceSettingsMessage)message);
                    break;
                case 14350:
                    TeamCreateReceived((TeamCreateMessage)message);
                    break;
                case 14353:
                    TeamLeaveReceived((TeamLeaveMessage)message);
                    break;
                case 14354:
                    TeamChangeMemberSettingsReceived((TeamChangeMemberSettingsMessage)message);
                    break;
                case 14355:
                    TeamSetMemberReadyReceived((TeamSetMemberReadyMessage)message);
                    break;
                case 14358:
                    TeamSpectateMessageReceived((TeamSpectateMessage)message);
                    break;
                case 14359:
                    TeamChatReceived((TeamChatMessage)message);
                    break;
                case 14361:
                    TeamMemberStatusReceived((TeamMemberStatusMessage)message);
                    ShowLobbyInfo();
                    break;
                case 14362:
                    TeamSetEventReceived((TeamSetEventMessage)message);
                    break;
                case 14363:
                    TeamSetLocationReceived((TeamSetLocationMessage)message);
                    break;
                case 14365:
                    TeamInviteReceived((TeamInviteMessage)message);
                    break;
                case 14366:
                    PlayerStatusReceived((PlayerStatusMessage)message);
                    ShowLobbyInfo();
                    break;
                case 14369:
                    TeamPremadeChatReceived((TeamPremadeChatMessage)message);
                    break;
                case 14370:
                    TeamInviteReceived((TeamInviteMessage)message);
                    break;
                case 14403:
                    GetLeaderboardReceived((GetLeaderboardMessage)message);
                    break;
                case 14479:
                    TeamInvitationResponseReceived((TeamInvitationResponseMessage)message);
                    break;
                case 14600:
                    AvatarNameCheckRequestReceived((AvatarNameCheckRequestMessage)message);
                    break;
                case 14777:
                    SetInvitesBlockedReceived((SetInvitesBlockedMessage)message);
                    break;
                case 19001:
                    LatencyTestResultReceived((LatencyTestResultMessage)message);
                    break;
                case 11000:
                    RequestSyncSSIDReceived((RequestSyncSSID)message);
                    break;
                case 19996:
                    RequestMaintenanceReceived((RequestMaintenance)message);
                    break;
                case 19997:
                    RequestSaveAllReceived((RequestSaveAll)message);
                    break;
                case 19998:
                    RequestDBChangesReceived((RequestDBChanges)message);
                    break;
                case 19999:
                    RequestServerReceived((RequestServerStatus)message);
                    break;


                    Logger.Print($"[MessageManager::ReceiveMessage] Message received! PacketName: {message.GetType().Name}, PacketID: {message.GetMessageType()}");

                default:
                    Logger.Print($"MessageManager::ReceiveMessage - no case for {message.GetType().Name} ({message.GetMessageType()})");
                    break;
            }
        }

        
        private void TeamSpectateMessageReceived(TeamSpectateMessage message)
        {
            TeamEntry team = Teams.Get(message.TeamId);
            if (team == null) return;
            HomeMode.Avatar.TeamId = team.Id;
            TeamMember member = new TeamMember();
            member.AccountId = HomeMode.Avatar.AccountId;
            member.CharacterId = HomeMode.Home.CharacterId;
            member.DisplayData = new PlayerDisplayData(HomeMode.Home.HasPremiumPass, HomeMode.Home.ThumbnailId, HomeMode.Home.NameColorId, HomeMode.Avatar.Name);

            Hero hero = HomeMode.Avatar.GetHero(HomeMode.Home.CharacterId);
            member.HeroLevel = hero.PowerLevel;
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
            member.HeroTrophies = hero.Trophies;
            member.HeroHighestTrophies = hero.HighestTrophies;

            member.IsOwner = false;
            member.State = 2;
            team.Members.Add(member);
            team.TeamUpdated();
        }

        private void SetBlockFriendRequestsReceived(SetBlockFriendRequestsMessage message)
        {
            //HomeMode.Home.BlockFriendRequests = message.State;
        }

        private void ReportAllianceStreamReceived(ReportAllianceStreamMessage message)
        {
            if (HomeMode.Avatar.AllianceId < 0) return;
            Alliance myAlliance = Alliances.Load(HomeMode.Avatar.AllianceId);
            if (myAlliance == null) return;
            if (HomeMode.Home.ReportsIds.Count > 5)
            {
                Connection.Send(new ReportUserStatusMessage()
                {
                    Status = 2
                });
                return;
            }
            long index = 0;
            foreach (AllianceStreamEntry e in myAlliance.Stream.GetEntries())
            {
                index++;
                if (e.Id == message.MessageIndex)
                {
                    if (HomeMode.Home.ReportsIds.Contains(e.AuthorId))
                    {
                        Connection.Send(new ReportUserStatusMessage()
                        {
                            Status = 3
                        });
                        return;
                    }
                    string reporterTag = LogicLongCodeGenerator.ToCode(HomeMode.Avatar.AccountId);
                    string reporterName = HomeMode.Avatar.Name;
                    string susTag = LogicLongCodeGenerator.ToCode(e.AuthorId);
                    string susName = e.AuthorName;
                    HomeMode.Home.ReportsIds.Add(e.AuthorId);
                    string text = "";
                    try { text += myAlliance.Stream.GetEntries()[index - 5].SendTime + " " + LogicLongCodeGenerator.ToCode(myAlliance.Stream.GetEntries()[index - 5].AuthorId) + " " + myAlliance.Stream.GetEntries()[index - 5].AuthorName + ">>> " + myAlliance.Stream.GetEntries()[index - 5].Message + "\n"; } catch { }
                    try { text += myAlliance.Stream.GetEntries()[index - 4].SendTime + " " + LogicLongCodeGenerator.ToCode(myAlliance.Stream.GetEntries()[index - 4].AuthorId) + " " + myAlliance.Stream.GetEntries()[index - 4].AuthorName + ">>> " + myAlliance.Stream.GetEntries()[index - 4].Message + "\n"; } catch { }
                    try { text += myAlliance.Stream.GetEntries()[index - 3].SendTime + " " + LogicLongCodeGenerator.ToCode(myAlliance.Stream.GetEntries()[index - 3].AuthorId) + " " + myAlliance.Stream.GetEntries()[index - 3].AuthorName + ">>> " + myAlliance.Stream.GetEntries()[index - 3].Message + "\n"; } catch { }
                    try { text += myAlliance.Stream.GetEntries()[index - 2].SendTime + " " + LogicLongCodeGenerator.ToCode(myAlliance.Stream.GetEntries()[index - 2].AuthorId) + " " + myAlliance.Stream.GetEntries()[index - 2].AuthorName + ">>> " + myAlliance.Stream.GetEntries()[index - 2].Message + "\n"; } catch { }
                    try { text += myAlliance.Stream.GetEntries()[index - 1].SendTime + " " + LogicLongCodeGenerator.ToCode(myAlliance.Stream.GetEntries()[index - 1].AuthorId) + " " + myAlliance.Stream.GetEntries()[index - 1].AuthorName + ">>> " + myAlliance.Stream.GetEntries()[index - 1].Message + "\n"; } catch { }
                    try { text += myAlliance.Stream.GetEntries()[index - 0].SendTime + " " + LogicLongCodeGenerator.ToCode(myAlliance.Stream.GetEntries()[index - 0].AuthorId) + " " + myAlliance.Stream.GetEntries()[index - 0].AuthorName + ">>> " + myAlliance.Stream.GetEntries()[index - 0].Message + "\n"; } catch { }
                    try { text += myAlliance.Stream.GetEntries()[index + 1].SendTime + " " + LogicLongCodeGenerator.ToCode(myAlliance.Stream.GetEntries()[index + 1].AuthorId) + " " + myAlliance.Stream.GetEntries()[index + 1].AuthorName + ">>> " + myAlliance.Stream.GetEntries()[index + 1].Message + "\n"; } catch { }
                    try { text += myAlliance.Stream.GetEntries()[index + 2].SendTime + " " + LogicLongCodeGenerator.ToCode(myAlliance.Stream.GetEntries()[index + 2].AuthorId) + " " + myAlliance.Stream.GetEntries()[index + 2].AuthorName + ">>> " + myAlliance.Stream.GetEntries()[index + 2].Message + "\n"; } catch { }
                    try { text += myAlliance.Stream.GetEntries()[index + 3].SendTime + " " + LogicLongCodeGenerator.ToCode(myAlliance.Stream.GetEntries()[index + 3].AuthorId) + " " + myAlliance.Stream.GetEntries()[index + 3].AuthorName + ">>> " + myAlliance.Stream.GetEntries()[index + 3].Message + "\n"; } catch { }
                    try { text += myAlliance.Stream.GetEntries()[index + 4].SendTime + " " + LogicLongCodeGenerator.ToCode(myAlliance.Stream.GetEntries()[index + 4].AuthorId) + " " + myAlliance.Stream.GetEntries()[index + 4].AuthorName + ">>> " + myAlliance.Stream.GetEntries()[index + 4].Message + "\n"; } catch { }
                    try { text += myAlliance.Stream.GetEntries()[index + 5].SendTime + " " + LogicLongCodeGenerator.ToCode(myAlliance.Stream.GetEntries()[index + 5].AuthorId) + " " + myAlliance.Stream.GetEntries()[index + 5].AuthorName + ">>> " + myAlliance.Stream.GetEntries()[index + 5].Message + "\n"; } catch { }
                    Logger.HandleReport($"Player {reporterName}, {reporterTag} reported player {susName}, {susTag}, in this msgs:\n`\n{text}`");
                    Connection.Send(new ReportUserStatusMessage()
                    {
                        Status = 1
                    });
                    break;
                }
            }
        }
        private void GetSeasonRewardsReceived(GetSeasonRewardsMessage message)
        {
            Connection.Send(new SeasonRewardsMessage());
        }

        private void SetInvitesBlockedReceived(SetInvitesBlockedMessage message)
        {
            HomeMode.Avatar.DoNotDisturb = message.State;
            LogicInviteBlockingChangedCommand command = new LogicInviteBlockingChangedCommand();
            command.State = message.State;
            AvailableServerCommandMessage serverCommandMessage = new AvailableServerCommandMessage();
            serverCommandMessage.Command = command;
            Connection.Send(serverCommandMessage);
            if (HomeMode.Avatar.AllianceId > 0)
            {
                Alliance a = Alliances.Load(HomeMode.Avatar.AllianceId);
                AllianceMember m = a.GetMemberById(HomeMode.Avatar.AccountId);
                m.DoNotDisturb = message.State;
                AllianceDataMessage dataMessage = new AllianceDataMessage()
                {
                    Alliance = a,
                    IsMyAlliance = true,
                };
                a.SendToAlliance(dataMessage);
            }
        }
        private void LatencyTestResultReceived(LatencyTestResultMessage message)
        {
            LatencyTestStatusMessage l = new()
            {
                Ping = Connection.Ping
            };
            Connection.Send(l);
        }
        private void TeamPremadeChatReceived(TeamPremadeChatMessage message)
        {
            if (HomeMode.Avatar.TeamId <= 0) return;

            TeamEntry team = GetTeam();
            if (team == null) return;

            QuickChatStreamEntry entry = new QuickChatStreamEntry();
            entry.AccountId = HomeMode.Avatar.AccountId;
            entry.TargetId = message.TargetId;
            entry.Name = HomeMode.Avatar.Name;

            if (message.TargetId > 0)
            {
                TeamMember member = team.GetMember(message.TargetId);
                if (member != null)
                {
                    entry.TargetPlayerName = member.DisplayData.Name;
                }
            }

            entry.MessageDataId = message.MessageDataId;
            entry.Unknown1 = message.Unknown1;
            entry.Unknown2 = message.Unknown2;

            team.AddStreamEntry(entry);
        }

        private void TeamChatReceived(TeamChatMessage message)
        {
            if (HomeMode.Avatar.TeamId <= 0) return;
            if (HomeMode.Avatar.IsCommunityBanned) return;

            TeamEntry team = GetTeam();
            if (team == null) return;

            ChatStreamEntry entry = new ChatStreamEntry();
            entry.AccountId = HomeMode.Avatar.AccountId;
            entry.Name = HomeMode.Avatar.Name;
            entry.Message = message.Message;

            team.AddStreamEntry(entry);
        }

        private void AvatarNameCheckRequestReceived(AvatarNameCheckRequestMessage message)
        {
            LogicChangeAvatarNameCommand command = new LogicChangeAvatarNameCommand();
            command.Name = message.Name;
            command.ChangeNameCost = 0;
            command.Execute(HomeMode);
            if (HomeMode.Avatar.AllianceId >= 0)
            {
                Alliance a = Alliances.Load(HomeMode.Avatar.AllianceId);
                if (a == null) return;
                AllianceMember m = a.GetMemberById(HomeMode.Avatar.AccountId);
                m.DisplayData.Name = message.Name;
            }
            AvailableServerCommandMessage serverCommandMessage = new AvailableServerCommandMessage();
            serverCommandMessage.Command = command;
            Connection.Send(serverCommandMessage);
        }

        private void TeamSetEventReceived(TeamSetEventMessage message)
        {
            if (HomeMode.Avatar.TeamId <= 0) return;

            TeamEntry team = GetTeam();
            if (team == null) return;
            if (message.EventSlot == 2) return;

            EventData data = Events.GetEvent(message.EventSlot);
            if (data == null) return;

            team.EventSlot = message.EventSlot;
            team.LocationId = data.LocationId;
            team.TeamUpdated();
        }

        private BattleMode SpectatedBattle;
        private void StopSpectateReceived(StopSpectateMessage message)
        {
            if (SpectatedBattle != null)
            {
                SpectatedBattle.RemoveSpectator(Connection.UdpSessionId);
                SpectatedBattle = null;
            }

            if (Connection.Home != null && Connection.Avatar != null)
            {
                OwnHomeDataMessage ohd = new OwnHomeDataMessage();
                ohd.Home = Connection.Home;
                ohd.Avatar = Connection.Avatar;
                Connection.Send(ohd);
            }
        }

        private void StartSpectateReceived(StartSpectateMessage message)
        {
            Account data = Accounts.Load(message.AccountId);
            if (data == null) return;

            ClientAvatar avatar = data.Avatar;
            long battleId = avatar.BattleId;

            BattleMode battle = Battles.Get(battleId);
            if (battle == null) return;

            SpectatedBattle = battle;
            UDPSocket socket = UDPGateway.CreateSocket();
            socket.Battle = battle;
            socket.IsSpectator = true;
            socket.TCPConnection = Connection;
            Connection.UdpSessionId = socket.SessionId;
            battle.AddSpectator(socket.SessionId, new UDPGameListener(socket, Connection));

            StartLoadingMessage startLoading = new StartLoadingMessage();
            startLoading.LocationId = battle.Location.GetGlobalId();
            startLoading.TeamIndex = 0;
            startLoading.OwnIndex = 0;
            startLoading.GameMode = battle.GetGameModeVariation() == 6 ? 6 : 1;
            startLoading.Players.AddRange(battle.GetPlayers());
            startLoading.SpectateMode = 1;

            Connection.Send(startLoading);

            UdpConnectionInfoMessage info = new UdpConnectionInfoMessage();
            info.SessionId = Connection.UdpSessionId;
            info.ServerAddress = Configuration.Instance.UdpHost;
            info.ServerPort = Configuration.Instance.UdpPort;
            Connection.Send(info);
        }

        private void GoHomeFromOfflinePractiseReceived(GoHomeFromOfflinePractiseMessage message)
        {
            if (Connection.Home != null && Connection.Avatar != null)
            {
                if (Connection.Avatar.IsTutorialState())
                {
                    Connection.Avatar.SkipTutorial();
                }
                if (false)//(HomeMode.Avatar.BattleStartTime != new DateTime())
                {
                    Hero h = HomeMode.Avatar.GetHero(HomeMode.Home.CharacterId);
                    int lose = 0;
                    int brawlerTrophies = h.Trophies;
                    if (brawlerTrophies <= 49)
                    {
                        lose = 0;
                    }
                    else if (50 <= brawlerTrophies && brawlerTrophies <= 99)
                    {
                        lose = -1;
                    }
                    else if (100 <= brawlerTrophies && brawlerTrophies <= 199)
                    {
                        lose = -2;
                    }
                    else if (200 <= brawlerTrophies && brawlerTrophies <= 299)
                    {
                        lose = -3;
                    }
                    else if (300 <= brawlerTrophies && brawlerTrophies <= 399)
                    {
                        lose = -4;
                    }
                    else if (400 <= brawlerTrophies && brawlerTrophies <= 499)
                    {
                        lose = -5;
                    }
                    else if (500 <= brawlerTrophies && brawlerTrophies <= 599)
                    {
                        lose = -6;
                    }
                    else if (600 <= brawlerTrophies && brawlerTrophies <= 699)
                    {
                        lose = -7;
                    }
                    else if (700 <= brawlerTrophies && brawlerTrophies <= 799)
                    {
                        lose = -8;
                    }
                    else if (800 <= brawlerTrophies && brawlerTrophies <= 899)
                    {
                        lose = -9;
                    }
                    else if (900 <= brawlerTrophies && brawlerTrophies <= 999)
                    {
                        lose = -10;
                    }
                    else if (1000 <= brawlerTrophies && brawlerTrophies <= 1099)
                    {
                        lose = -11;
                    }
                    else if (1100 <= brawlerTrophies && brawlerTrophies <= 1199)
                    {
                        lose = -12;
                    }
                    else if (brawlerTrophies >= 1200)
                    {
                        lose = -12;
                    }
                    h.AddTrophies(lose);
                    HomeMode.Home.PowerPlayGamesPlayed = Math.Max(0, HomeMode.Home.PowerPlayGamesPlayed - 1);
                    HomeMode.Avatar.BattleStartTime = new DateTime();
                    Logger.BLog($"Player {LogicLongCodeGenerator.ToCode(HomeMode.Avatar.AccountId)} left battle!");
                }
                Connection.Home.Events = Events.GetEventsById(HomeMode.Home.PowerPlayGamesPlayed, Connection.Avatar.AccountId);

                OwnHomeDataMessage ohd = new OwnHomeDataMessage();
                ohd.Home = Connection.Home;
                ohd.Avatar = Connection.Avatar;
                ShowLobbyInfo();
                Connection.Send(ohd);
            }
        }

        private void TeamSetLocationReceived(TeamSetLocationMessage message)
        {
            if (HomeMode.Avatar.TeamId <= 0) return;

            TeamEntry team = GetTeam();
            if (team == null) return;

            team.Type = 1;
            team.TeamUpdated();
        }

        private void ChangeAllianceSettingsReceived(ChangeAllianceSettingsMessage message)
        {
            if (HomeMode.Avatar.AllianceId <= 0) return;

            if (HomeMode.Avatar.AllianceRole != AllianceRole.Leader && HomeMode.Avatar.AllianceRole != AllianceRole.CoLeader) return;

            Alliance alliance = Alliances.Load(HomeMode.Avatar.AllianceId);
            if (alliance == null) return;

            if (message.BadgeId >= 8000000 && message.BadgeId < 8000000 + DataTables.Get(DataType.AllianceBadge).Count)
            {
                alliance.AllianceBadgeId = message.BadgeId;
            }
            else
            {
                alliance.AllianceBadgeId = 8000000;
            }

            alliance.Type = message.Type == 1 ? 1 : 3;
            alliance.Description = message.Description;
            alliance.RequiredTrophies = message.RequiredTrophies;

            Connection.Send(new AllianceResponseMessage()
            {
                ResponseType = 10
            });

            MyAllianceMessage myAlliance = new MyAllianceMessage();
            myAlliance.Role = HomeMode.Avatar.AllianceRole;
            myAlliance.OnlineMembers = alliance.OnlinePlayers;
            myAlliance.AllianceHeader = alliance.Header;
            Connection.Send(myAlliance);
        }

        private void KickAllianceMemberReceived(KickAllianceMemberMessage message)
        {
            if (HomeMode.Avatar.AllianceId <= 0) return;
            if (HomeMode.Avatar.AllianceRole == AllianceRole.Member || HomeMode.Avatar.AllianceRole == AllianceRole.None) return;

            Alliance alliance = Alliances.Load(HomeMode.Avatar.AllianceId);
            if (alliance == null) return;

            AllianceMember member = alliance.GetMemberById(message.AccountId);
            if (member == null) return;

            ClientAvatar avatar = Accounts.Load(message.AccountId).Avatar;

            if (alliance.getRoleVector(avatar.AllianceRole, (AllianceRole)HomeMode.Avatar.AllianceRole)) return;

            alliance.Members.Remove(member);
            avatar.AllianceId = -1;

            AllianceStreamEntry entry = new AllianceStreamEntry();
            entry.AuthorId = HomeMode.Avatar.AccountId;
            entry.AuthorName = HomeMode.Avatar.Name;
            entry.Id = ++alliance.Stream.EntryIdCounter;
            entry.PlayerId = avatar.AccountId;
            entry.PlayerName = avatar.Name;
            entry.Type = 4;
            entry.Event = 1; // kicked
            entry.AuthorRole = HomeMode.Avatar.AllianceRole;
            alliance.AddStreamEntry(entry);

            AllianceResponseMessage response = new AllianceResponseMessage();
            response.ResponseType = 70;
            Connection.Send(response);

            if (LogicServerListener.Instance.IsPlayerOnline(avatar.AccountId))
            {
                LogicServerListener.Instance.GetGameListener(avatar.AccountId).SendTCPMessage(new AllianceResponseMessage()
                {
                    ResponseType = 100
                });
                LogicServerListener.Instance.GetGameListener(avatar.AccountId).SendTCPMessage(new MyAllianceMessage());
            }
        }

        private void TeamSetMemberReadyReceived(TeamSetMemberReadyMessage message)
        {
            TeamEntry team = Teams.Get(HomeMode.Avatar.TeamId);
            if (team == null) return;

            TeamMember member = team.GetMember(HomeMode.Avatar.AccountId);
            if (member == null) return;

            member.IsReady = message.IsReady;

            team.TeamUpdated();

            //if (team.IsEveryoneReady())
            // {
            //Teams.StartGame(team);
            //}
        }

        private void TeamChangeMemberSettingsReceived(TeamChangeMemberSettingsMessage message)
        {
            ;
        }

        private void TeamMemberStatusReceived(TeamMemberStatusMessage message)
        {
            if (HomeMode == null) return;
            if (message.Status < 0) return;
            TeamEntry team = Teams.Get(HomeMode.Avatar.TeamId);
            if (team == null) return;

            TeamMember member = team.GetMember(HomeMode.Avatar.AccountId);
            if (member == null) return;

            member.State = message.Status;
            team.TeamUpdated();
        }

        private void TeamInvitationResponseReceived(TeamInvitationResponseMessage message)
        {
            bool isAccept = message.Response == 1;

            TeamEntry team = Teams.Get(message.TeamId);
            if (team == null) return;

            TeamInviteEntry invite = team.GetInviteById(HomeMode.Avatar.AccountId);
            if (invite == null) return;

            team.Invites.Remove(invite);

            if (isAccept)
            {
                TeamMember member = new TeamMember();
                member.AccountId = HomeMode.Avatar.AccountId;
                member.CharacterId = HomeMode.Home.CharacterId;
                member.DisplayData = new PlayerDisplayData(HomeMode.Home.HasPremiumPass, HomeMode.Home.ThumbnailId, HomeMode.Home.NameColorId, HomeMode.Avatar.Name);

                Hero hero = HomeMode.Avatar.GetHero(HomeMode.Home.CharacterId);
                member.HeroTrophies = hero.Trophies;
                member.HeroHighestTrophies = hero.HighestTrophies;
                member.HeroLevel = hero.PowerLevel;
                member.IsOwner = false;
                member.State = 0;
                team.Members.Add(member);

                HomeMode.Avatar.TeamId = team.Id;
            }

            team.TeamUpdated();
        }

        private TeamEntry GetTeam()
        {
            return Teams.Get(HomeMode.Avatar.TeamId);
        }

        private void TeamInviteReceived(TeamInviteMessage message)
        {
            TeamEntry team = GetTeam();
            if (team == null) return;

            Account data = Accounts.Load(message.AvatarId);
            if (data == null) return;

            TeamInviteEntry entry = new TeamInviteEntry();
            entry.Slot = message.Team;
            entry.Name = data.Avatar.Name;
            entry.Id = message.AvatarId;
            entry.InviterId = HomeMode.Avatar.AccountId;

            team.Invites.Add(entry);

            team.TeamUpdated();

            LogicGameListener gameListener = LogicServerListener.Instance.GetGameListener(message.AvatarId);
            if (gameListener != null)
            {
                TeamInvitationMessage teamInvitationMessage = new TeamInvitationMessage();
                teamInvitationMessage.TeamId = team.Id;

                Friend friendEntry = new Friend();
                friendEntry.AccountId = HomeMode.Avatar.AccountId;
                friendEntry.DisplayData = new PlayerDisplayData(HomeMode.Home.HasPremiumPass, HomeMode.Home.ThumbnailId, HomeMode.Home.NameColorId, HomeMode.Avatar.Name);
                friendEntry.Trophies = HomeMode.Avatar.Trophies;
                teamInvitationMessage.Unknown = 1;
                teamInvitationMessage.FriendEntry = friendEntry;

                gameListener.SendTCPMessage(teamInvitationMessage);
            }
        }

        private void TeamLeaveReceived(TeamLeaveMessage message)
        {
            if (HomeMode.Avatar.TeamId <= 0) return;

            TeamEntry team = Teams.Get(HomeMode.Avatar.TeamId);

            if (team == null)
            {
                Logger.Print("TeamLeave - Team is NULL!");
                HomeMode.Avatar.TeamId = -1;
                Connection.Send(new TeamLeftMessage());
                return;
            }

            TeamMember entry = team.GetMember(HomeMode.Avatar.AccountId);

            if (entry == null) return;
            HomeMode.Avatar.TeamId = -1;

            team.Members.Remove(entry);

            Connection.Send(new TeamLeftMessage());
            team.TeamUpdated();

            if (team.Members.Count == 0)
            {
                Teams.Remove(team.Id);
            }
        }

        private void TeamCreateReceived(TeamCreateMessage message)
        {
            TeamEntry team = Teams.Create();

            team.Type = message.TeamType;
            team.LocationId = Events.GetEvents()[0].LocationId;

            TeamMember member = new TeamMember();
            member.AccountId = HomeMode.Avatar.AccountId;
            member.CharacterId = HomeMode.Home.CharacterId;
            member.DisplayData = new PlayerDisplayData(HomeMode.Home.HasPremiumPass, HomeMode.Home.ThumbnailId, HomeMode.Home.NameColorId, HomeMode.Avatar.Name);

            Hero hero = HomeMode.Avatar.GetHero(HomeMode.Home.CharacterId);
            member.HeroLevel = hero.PowerLevel;
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
            }
            else
            {
                member.Starpower = 0;
            }
            if (hero.PowerLevel > 5)
            {
                string[] cards = { "GrowBush", "Shield", "Heal", "Jump", "ShootAround", "DestroyPet", "PetSlam", "Slow", "Push", "Dash", "SpeedBoost", "BurstHeal", "Spin", "Teleport", "Immunity", "Trail", "Totem", "Grab", "Swing", "Vision", "Regen", "HandGun", "Promote", "Sleep", "Slow", "Reload", "Reload", "Fake", "Trampoline", "Explode" };
                CharacterData cd = DataTables.Get(DataType.Character).GetDataByGlobalId<CharacterData>(hero.CharacterId);
                CardData WildCard = null;
                foreach (string cardname in cards)
                {
                    string n = char.ToUpper(cd.Name[0]) + cd.Name.Substring(1);
                    Console.WriteLine(n + "_" + cardname);
                    WildCard = DataTables.Get(DataType.Card).GetData<CardData>(n + "_" + cardname);
                    if (WildCard != null)
                    {
                        break;
                    }
                }
                if (HomeMode.Avatar.Starpowers.Contains(WildCard.GetGlobalId()))
                {
                    member.Gadget = WildCard.GetGlobalId();
                }
            }
            else
            {
                member.Gadget = 0;
            }
            //member.SkinId = HomeMode.Home.SelectedSkins[GlobalId.GetInstanceId(HomeMode.Home.CharacterId)];
            member.HeroTrophies = hero.Trophies;
            member.HeroHighestTrophies = hero.HighestTrophies;

            member.IsOwner = true;
            member.State = 2;
            team.Members.Add(member);

            TeamMessage teamMessage = new TeamMessage();
            teamMessage.Team = team;
            HomeMode.Avatar.TeamId = team.Id;
            Connection.Send(teamMessage);
        }

        private void AcceptFriendReceived(AcceptFriendMessage message)
        {
            Account data = Accounts.Load(message.AvatarId);
            if (data == null) return;

            {
                Friend entry = HomeMode.Avatar.GetRequestFriendById(message.AvatarId);
                if (entry == null) return;

                Friend oldFriend = HomeMode.Avatar.GetAcceptedFriendById(message.AvatarId);
                if (oldFriend != null)
                {
                    HomeMode.Avatar.Friends.Remove(entry);
                    Connection.Send(new OutOfSyncMessage());
                    return;
                }

                entry.FriendReason = 0;
                entry.FriendState = 4;

                FriendListUpdateMessage update = new FriendListUpdateMessage();
                update.Entry = entry;
                Connection.Send(update);
            }

            {
                ClientAvatar avatar = data.Avatar;
                Friend entry = avatar.GetFriendById(HomeMode.Avatar.AccountId);
                if (entry == null) return;

                entry.FriendState = 4;
                entry.FriendReason = 0;

                if (LogicServerListener.Instance.IsPlayerOnline(avatar.AccountId))
                {
                    FriendListUpdateMessage update = new FriendListUpdateMessage();
                    update.Entry = entry;
                    LogicServerListener.Instance.GetGameListener(avatar.AccountId).SendTCPMessage(update);
                }
            }
        }

        private void RemoveFriendReceived(RemoveFriendMessage message)
        {
            Account data = Accounts.Load(message.AvatarId);
            if (data == null) return;

            ClientAvatar avatar = data.Avatar;

            Friend MyEntry = HomeMode.Avatar.GetFriendById(message.AvatarId);
            if (MyEntry == null) return;

            MyEntry.FriendState = 0;

            HomeMode.Avatar.Friends.Remove(MyEntry);

            FriendListUpdateMessage update = new FriendListUpdateMessage();
            update.Entry = MyEntry;
            Connection.Send(update);

            Friend OtherEntry = avatar.GetFriendById(HomeMode.Avatar.AccountId);

            if (OtherEntry == null) return;

            OtherEntry.FriendState = 0;

            avatar.Friends.Remove(OtherEntry);

            if (LogicServerListener.Instance.IsPlayerOnline(avatar.AccountId))
            {
                FriendListUpdateMessage update2 = new FriendListUpdateMessage();
                update2.Entry = OtherEntry;
                LogicServerListener.Instance.GetGameListener(avatar.AccountId).SendTCPMessage(update2);
            }
        }

        private void AddFriendReceived(AddFriendMessage message)
        {
            Account data = Accounts.Load(message.AvatarId);
            if (data == null)
            {
                Connection.Send(new AddFriendFailedMessage
                {
                    Reason = 5
                });
                return;
            }
            if (data.Avatar.AccountId == HomeMode.Avatar.AccountId)
            {
                // 2 - too many invites
                // 4 - invite urself
                // 5 doesnt exist
                // 7 - u have too many friends, rm
                // 8 - u have too many friends
                Connection.Send(new AddFriendFailedMessage
                {
                    Reason = 4
                });
                return;
            }
            if (data.Home.BlockFriendRequests)
            {
                Connection.Send(new AddFriendFailedMessage
                {
                    Reason = 0
                });
                return;
            }

            ClientAvatar avatar = data.Avatar;

            Friend requestEntry = HomeMode.Avatar.GetFriendById(message.AvatarId);
            if (requestEntry != null)
            {
                AcceptFriendReceived(new AcceptFriendMessage()
                {
                    AvatarId = message.AvatarId
                });
                return;
            }
            else
            {
                Friend friendEntry = new Friend();
                friendEntry.AccountId = HomeMode.Avatar.AccountId;
                friendEntry.DisplayData = new PlayerDisplayData(HomeMode.Home.HasPremiumPass, HomeMode.Home.ThumbnailId, HomeMode.Home.NameColorId, HomeMode.Avatar.Name);
                friendEntry.FriendReason = message.Reason;
                friendEntry.FriendState = 3;
                avatar.Friends.Add(friendEntry);

                Friend request = new Friend();
                request.AccountId = avatar.AccountId;
                request.DisplayData = new PlayerDisplayData(data.Home.HasPremiumPass, data.Home.ThumbnailId, data.Home.NameColorId, data.Avatar.Name);
                request.FriendReason = 0;
                request.FriendState = 2;
                HomeMode.Avatar.Friends.Add(request);

                if (LogicServerListener.Instance.IsPlayerOnline(message.AvatarId))
                {
                    var gameListener = LogicServerListener.Instance.GetGameListener(message.AvatarId);

                    FriendListUpdateMessage update = new FriendListUpdateMessage();
                    update.Entry = friendEntry;

                    gameListener.SendTCPMessage(update);
                }

                FriendListUpdateMessage update2 = new FriendListUpdateMessage();
                update2.Entry = request;
                Connection.Send(update2);
            }
        }

        private void AskForFriendListReceived(AskForFriendListMessage message)
        {
            FriendListMessage friendList = new FriendListMessage();
            friendList.Friends = HomeMode.Avatar.Friends.ToArray();
            Connection.Send(friendList);
        }

        private void RequestSyncSSIDReceived(RequestSyncSSID message)
        {
            if (message.AuthPass != "672a2746a7afbce8f06dc23d79135ba5")
            {

                return;
            }
            foreach (KeyValuePair<string, string> pair in message.Requests)
            {
                if (!Sessions.RegistratedSSID.ContainsKey(pair.Key))
                {
                    Sessions.RegistratedSSID.Add(pair.Key, pair.Value);
                }
                else
                {
                    Sessions.RegistratedSSID[pair.Key] = pair.Value;
                }
            }
            foreach (string k in message.DisposeRequests)
            {
                Sessions.RegistratedSSID.Remove(k);
            }
            Connection.Send(new SyncSSIDResponce()
            {
                Requests = Sessions.RequestedSSID,
                RecAccs = Sessions.LeaveJoin
            });
            Sessions.RequestedSSID = new();
            Sessions.LeaveJoin = new();
        }
		private void RequestMaintenanceReceived(RequestMaintenance message)
        {
            if (message.AuthPass != "672a2746a7afbce8f06dc23d79135ba5")
            {
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"dsadas"));
                return;
            }
            Sessions.StartShutdown();
            AccountCache.SaveAll();
            AllianceCache.SaveAll();

            AccountCache.Started = false;
            AllianceCache.Started = false;

            Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes("Done!"));
        }

        private void RequestSaveAllReceived(RequestSaveAll message)
        {
            if (message.AuthPass != "672a2746a7afbce8f06dc23d79135ba5")
            {
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"dsadas"));
                return;
            }
            AccountCache.SaveAll();
            AllianceCache.SaveAll();

            Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes("Done!"));
        }

        private void RequestDBChangesReceived(RequestDBChanges message)
        {
            if (message.AuthPass != "672a2746a7afbce8f06dc23d79135ba5")
            {
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"dsadas"));
                return;
            }

            string[] cmd = message.Message.Substring(1).Split(' ');
            if (cmd[0] == "giveprem")
            {
                if (cmd.Length != 2)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }
                if (account.Home.PremiumEndTime < DateTime.UtcNow)
                {
                    account.Home.PremiumEndTime = DateTime.UtcNow.AddMonths(1);
                }
                else
                {
                    account.Home.PremiumEndTime = account.Home.PremiumEndTime.AddMonths(1);
                }

                account.Avatar.PremiumLevel = 1;
                Notification n = new Notification
                {
                    Id = 89,
                    DonationCount = 30,
                    //Time = DateTime.UtcNow,
                    MessageEntry = $"<c6>Vip статус активирован/продлён до {account.Home.PremiumEndTime} UTC, спасибо за поддержку сервера!</c>"
                };
                account.Home.NotificationFactory.Add(n);
                LogicAddNotificationCommand acm = new()
                {
                    Notification = n
                };
                AvailableServerCommandMessage asm = new AvailableServerCommandMessage();
                asm.Command = acm;
                if (Sessions.IsSessionActive(id))
                {
                    var session = Sessions.GetSession(id);
                    session.GameListener.SendTCPMessage(asm);
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: set vip status for {d} activated/extended to {account.Home.PremiumEndTime} UTC!"));
            }
            else if (cmd[0] == "chat_unmute")
            {
                if (cmd.Length != 3)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }

                account.Home.ChatBanEndTime = DateTime.MinValue;
                Notification wn = new Notification
                {
                    Id = 81,
                    //Time = DateTime.UtcNow,
                    MessageEntry = $"<c25c42b>Блокировка чата твоего аккаунта была снята досрочно</c>"
                };
                account.Home.NotificationFactory.Add(wn);
                if (LogicServerListener.Instance.IsPlayerOnline(account.Avatar.AccountId))
                {
                    LogicServerListener.Instance.GetGameListener(account.Avatar.AccountId).SendTCPMessage(new AvailableServerCommandMessage
                    {
                        Command = new LogicAddNotificationCommand()
                        {
                            Notification = wn
                        }
                    });
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: unmuted {d}"));
            }
            else if (cmd[0] == "chat_mute")
            {
                if (cmd.Length != 3)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }

                account.Home.ChatBanEndTime = DateTime.UtcNow.AddDays(int.Parse(cmd[2]));
                Notification wwn = new Notification
                {
                    Id = 81,
                    //Time = DateTime.UtcNow,
                    MessageEntry = $"Твоему аккаунт был временно отключён чат за нарушение правил.\n<ceb4034>Блокировка продлиться до {account.Home.ChatBanEndTime} UTC</c>\nПоследующие нарушения могут привести к блокировке чата навсегда"
                };
                account.Home.NotificationFactory.Add(wwn);
                if (LogicServerListener.Instance.IsPlayerOnline(account.Avatar.AccountId))
                {
                    LogicServerListener.Instance.GetGameListener(account.Avatar.AccountId).SendTCPMessage(new AvailableServerCommandMessage
                    {
                        Command = new LogicAddNotificationCommand()
                        {
                            Notification = wwn
                        }
                    });
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: muted {d} for {int.Parse(cmd[2])}d"));
            }
            else if (cmd[0] == "resetseason")
            {
                long lastAccId = Accounts.GetMaxAvatarId();
                for (int accid = 1; accid <= lastAccId; accid++)
                {
                    Account thisAcc = Accounts.LoadNoChache(accid);
                    if (thisAcc == null) continue;
                    if (thisAcc.Avatar.Trophies >= 550)
                    {
                        List<int> hhh = new();
                        List<int> ht = new();
                        List<int> htr = new();
                        List<int> sa = new();
                        int[] StarPointsTrophiesStart = { 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400 };
                        int[] StarPointsTrophiesEnd = { 599, 649, 699, 749, 799, 849, 899, 949, 999, 1049, 1099, 1149, 1199, 1249, 1299, 1349, 1399, 1000000 };
                        int[] StarPointsSeasonRewardAmount = { 70, 120, 160, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400, 420, 440, 460, 480 };
                        int[] StarPointsTrophiesInReset = { 549, 599, 649, 699, 749, 799, 849, 899, 924, 949, 974, 1024, 1049, 1074, 1099, 1124, 1149, 1174 };
                        foreach (Hero h in thisAcc.Avatar.Heroes)
                        {
                            if (h.Trophies >= StarPointsTrophiesStart[0])
                            {
                                hhh.Add(h.CharacterId);
                                ht.Add(h.Trophies);
                                int i = 0;
                                while (true)
                                {
                                    if (h.Trophies >= StarPointsTrophiesStart[i] && h.Trophies <= StarPointsTrophiesEnd[i])
                                    {
                                        if (StarPointsTrophiesStart[i] != 1400)
                                        {
                                            htr.Add(h.Trophies - StarPointsTrophiesInReset[i]);
                                            h.Trophies = StarPointsTrophiesInReset[i];
                                            sa.Add(StarPointsSeasonRewardAmount[i]);
                                        }
                                        else
                                        {
                                            int b = h.Trophies - 1440;
                                            b /= 2;
                                            htr.Add(h.Trophies - StarPointsTrophiesInReset[i] - b);
                                            h.Trophies = (StarPointsTrophiesInReset[i] + b);
                                            sa.Add(StarPointsSeasonRewardAmount[i] + b / 2);
                                        }
                                        break;
                                    }
                                    else
                                    {
                                        i++;
                                    }
                                }
                            }

                        }
                        if (hhh.Count > 0)
                        {
                            thisAcc.Home.NotificationFactory.Add(new Notification
                            {
                                Id = 79,
                                //Time = DateTime.UtcNow,
                                HeroesIds = hhh,
                                HeroesTrophies = ht,
                                HeroesTrophiesReseted = htr,
                                StarpointsAwarded = sa,
                            });
                        }
                    }
                    Accounts.Save(thisAcc);
                    Console.WriteLine(accid);
                }
            }
            else if (cmd[0] == "addgems")
            {
                if (cmd.Length != 3)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }
                //account.Avatar.Diamonds += int.Parse(cmd[2]);
                Notification n = new Notification
                {
                    Id = 89,
                    DonationCount = int.Parse(cmd[2]),
                    //Time = DateTime.UtcNow,
                    MessageEntry = $"<c6>Thanks for donation!</c>"
                };
                account.Home.NotificationFactory.Add(n);
                LogicAddNotificationCommand acm = new()
                {
                    Notification = n
                };
                AvailableServerCommandMessage asm = new AvailableServerCommandMessage();
                asm.Command = acm;
                if (Sessions.IsSessionActive(id))
                {
                    var session = Sessions.GetSession(id);
                    session.GameListener.SendTCPMessage(asm);
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: added {int.Parse(cmd[2])} gems for {d}!"));
            }
            else if (cmd[0] == "settrophy")
            {
                if (cmd.Length != 4)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }
                Hero h = account.Avatar.GetHero(int.Parse(cmd[2]));
                h.Trophies = int.Parse(cmd[3]);
                if (h.Trophies > h.HighestTrophies)
                {
                    h.HighestTrophies = h.Trophies;
                }
                if (account.Avatar.Trophies > account.Avatar.HighestTrophies)
                {
                    account.Avatar.HighestTrophies = account.Avatar.Trophies;
                }
                //account.Avatar.Diamonds += int.Parse(cmd[2]);
                if (Sessions.IsSessionActive(id))
                {
                    var session = Sessions.GetSession(id);
                    session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                    {
                        Message = "Some data changed, please re-enter game!"
                    });
                    Sessions.Remove(id);
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: set {int.Parse(cmd[3])} trophies for brawler {int.Parse(cmd[2])} for {d}!"));
            }
            else if (cmd[0] == "addgold")
            {
                if (cmd.Length != 3)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }
                //account.Avatar.Diamonds += int.Parse(cmd[2]);
                Notification n = new Notification
                {
                    Id = 90,
                    //Time = DateTime.UtcNow,
                    DonationCount = int.Parse(cmd[2]),
                    //DonationGlobalId = GlobalId.CreateGlobalId(5, 8),
                    MessageEntry = $"<c6>Thanks for donation!</c>"
                };
                account.Home.NotificationFactory.Add(n);
                LogicAddNotificationCommand acm = new()
                {
                    Notification = n
                };
                AvailableServerCommandMessage asm = new AvailableServerCommandMessage();
                asm.Command = acm;
                if (Sessions.IsSessionActive(id))
                {
                    var session = Sessions.GetSession(id);
                    session.GameListener.SendTCPMessage(asm);
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: added {int.Parse(cmd[2])} gold for {d}!"));
            }
            else if (cmd[0] == "addspints")
            {
                if (cmd.Length != 3)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }
                //account.Avatar.Diamonds += int.Parse(cmd[2]);
                Notification n = new Notification
                {
                    Id = 90,
                    DonationCount = int.Parse(cmd[2]),
                    //DonationGlobalId = GlobalId.CreateGlobalId(5, 10),
                    //Time = DateTime.UtcNow,
                    MessageEntry = $"<c6>Thanks for donation!</c>"
                };
                account.Home.NotificationFactory.Add(n);
                LogicAddNotificationCommand acm = new()
                {
                    Notification = n
                };
                AvailableServerCommandMessage asm = new AvailableServerCommandMessage();
                asm.Command = acm;
                if (Sessions.IsSessionActive(id))
                {
                    var session = Sessions.GetSession(id);
                    session.GameListener.SendTCPMessage(asm);
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: added {int.Parse(cmd[2])} starpoints for {d}!"));
            }
            else if (cmd[0] == "addbrawler" || cmd[0] == "addskin")
            {
                if (cmd.Length != 3)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }
                //account.Avatar.Diamonds += int.Parse(cmd[2]);
                Notification n = new Notification
                {
                    Id = cmd[0] == "addbrawler" ? 93 : 94,
                    DonationCount = 0,
                    //Time = DateTime.UtcNow,
                    //DonationGlobalId = int.Parse(cmd[2]),
                    MessageEntry = $"<c6>Thanks for donation!</c>"
                };
                account.Home.NotificationFactory.Add(n);
                LogicAddNotificationCommand acm = new()
                {
                    Notification = n
                };
                AvailableServerCommandMessage asm = new AvailableServerCommandMessage();
                asm.Command = acm;
                if (Sessions.IsSessionActive(id))
                {
                    var session = Sessions.GetSession(id);
                    session.GameListener.SendTCPMessage(asm);
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.UTF8.GetBytes($"Done: added ксвкакое-то {int.Parse(cmd[2])} for {d}!"));
            }
            else if (cmd[0] == "addstartokens")
            {
                if (cmd.Length != 3)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }
                //account.Avatar.Diamonds += int.Parse(cmd[2]);
                Notification n = new Notification
                {
                    Id = 90,
                    DonationCount = int.Parse(cmd[2]),
                    //DonationGlobalId = GlobalId.CreateGlobalId(5, 9),
                    //Time = DateTime.UtcNow,
                    MessageEntry = $"<c6>Thanks for donation!</c>"
                };
                account.Home.NotificationFactory.Add(n);
                LogicAddNotificationCommand acm = new()
                {
                    Notification = n
                };
                AvailableServerCommandMessage asm = new AvailableServerCommandMessage();
                asm.Command = acm;
                if (Sessions.IsSessionActive(id))
                {
                    var session = Sessions.GetSession(id);
                    session.GameListener.SendTCPMessage(asm);
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: added {int.Parse(cmd[2])} startokens for {d}!"));
            }
            else if (cmd[0] == "getusrinfo")
            {
                if (cmd.Length != 2)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }

                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                /*Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: Information of {d}!\n" +
                    $"IpAddress: {ConvertInfoToData(account.Home.IpAddress)}\n" +
                    $"Last Login Time: {account.Home.LastVisitHomeTime} UTC\n" +
                    $"Device: {ConvertInfoToData(account.Home.Device)}\n" +
                    $"Device(?) Identificator: {ConvertInfoToData(account.Home.DeviceIdenteficdactor)}\n" +
                    $"Language: {ConvertInfoToData(account.Home.Lang)}\n" +
                    $"Os Version: {ConvertInfoToData(account.Home.OsVersion)}"));*/
            }
            else if (cmd[0] == "resettoken")
            {
                if (cmd.Length < 2)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }
                account.PassToken = Helpers.RandomString(40);
                if (Sessions.IsSessionActive(id))
                {
                    var session = Sessions.GetSession(id);
                    session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                    {
                        Message = "Some data changed, please re-enter game!"
                    });
                    Sessions.Remove(id);
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: reseted pass token for {d}!"));
            }
            else if (cmd[0] == "chname")
            {
                if (cmd.Length < 3)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }
                string name = message.Message.Substring(1).Split("##!")[1];
                account.Avatar.Name = name;
                if (account.Avatar.AllianceId >= 0)
                {
                    Alliance a = Alliances.Load(account.Avatar.AllianceId);
                    if (a == null) return;
                    AllianceMember m = a.GetMemberById(account.Avatar.AccountId);
                    m.DisplayData.Name = name;
                }
                foreach (Friend friend in account.Avatar.Friends)
                {
                    Friend entry = friend.Avatar.GetFriendById(account.Avatar.AccountId);
                    entry.DisplayData.Name = account.Avatar.Name;
                    if (LogicServerListener.Instance.IsPlayerOnline(friend.Avatar.AccountId))
                    {
                        FriendListUpdateMessage update = new()
                        {
                            Entry = entry
                        };
                        LogicServerListener.Instance.GetGameListener(friend.AccountId).SendTCPMessage(update);
                    }

                }
                if (Sessions.IsSessionActive(id))
                {
                    var session = Sessions.GetSession(id);
                    session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                    {
                        Message = "Some data changed, please re-enter game!"
                    });
                    Sessions.Remove(id);
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: set vip status for {d} activated/extended to {account.Home.PremiumEndTime} UTC!"));
            }
            else
            {
                if (cmd.Length != 4)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid usage"));
                    Console.WriteLine("]");
                    return;
                }
                bool sc = false;
                long id = 0;
                if (cmd[1].StartsWith('#'))
                {
                    id = LogicLongCodeGenerator.ToId(cmd[1]);
                }
                else
                {
                    sc = true;
                    id = long.Parse(cmd[1]);
                }
                Account account = Accounts.Load(id);
                if (account == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {id}"));
                    return;
                }
                string[] req = cmd[2].Split('.');
                Type type = null;

                bool IsAvatar = false;
                if (req[0] == "Avatar")
                {
                    IsAvatar = true;
                    type = typeof(ClientAvatar);
                }
                else
                {
                    type = typeof(ClientHome);
                }
                FieldInfo field = type.GetField(req[1]);


                if (field == null)
                {
                    Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Error: Invalid tag: {cmd[2]} - is unknwon field"));
                    return;
                }
                if (cmd[3] == "true")
                {
                    field.SetValue(IsAvatar ? account.Avatar : account.Home, true);
                }
                else if (cmd[3] == "false")
                {
                    field.SetValue(IsAvatar ? account.Avatar : account.Home, false);
                }
                else
                {
                    try
                    {
                        field.SetValue(IsAvatar ? account.Avatar : account.Home, int.Parse(cmd[3]));
                    }
                    catch
                    {
                        field.SetValue(IsAvatar ? account.Avatar : account.Home, cmd[3]);
                    }

                }



                if (Sessions.IsSessionActive(id))
                {
                    var session = Sessions.GetSession(id);
                    session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                    {
                        Message = "Some data changed, please re-enter game!"
                    });
                    Sessions.Remove(id);
                }
                string d = sc ? LogicLongCodeGenerator.ToCode(long.Parse(cmd[1])) : cmd[1];
                Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes($"Done: set {cmd[2]} to {cmd[3]} for {d}"));
            }

        }

        private void RequestServerReceived(RequestServerStatus message)
        {
            long megabytesUsed = Process.GetCurrentProcess().PrivateMemorySize64 / (1024 * 1024);
            DateTime now = Process.GetCurrentProcess().StartTime;
            DateTime futureDate = DateTime.Now;

            TimeSpan timeDifference = futureDate - now;

            string formattedTime = string.Format("{0}{1}{2}{3}",
            timeDifference.Days > 0 ? $"{timeDifference.Days} Days, " : string.Empty,
            timeDifference.Hours > 0 || timeDifference.Days > 0 ? $"{timeDifference.Hours} Hours, " : string.Empty,
            timeDifference.Minutes > 0 || timeDifference.Hours > 0 ? $"{timeDifference.Minutes} Minutes, " : string.Empty,
            timeDifference.Seconds > 0 ? $"{timeDifference.Seconds} Seconds" : string.Empty);

            string msg = $"Server Status:\n" +
                $"Server Game Version: v28.189\n" +
                $"Server Build: v1.0 from 10.02.2024\n" +
                $"Resources Sha: {Fingerprint.Sha}\n" +
                $"Environment: Prod\n" +
                $"Server Time: {DateTime.Now} UTC\n" +
                $"Players Online: {Sessions.Count}\n" +
                $"Memory Used: {megabytesUsed} MB\n" +
                $"Uptime: {formattedTime}\n" +
                $"Accounts Cached: {AccountCache.Count}\n" +
                $"Alliances Cached: {AllianceCache.Count}\n" +
                $"Teams Cached: {Teams.Count}\n";
            Connection.Socket.Send(System.Text.Encoding.ASCII.GetBytes(msg));
        }

        private void PlayerStatusReceived(PlayerStatusMessage message)
        {
            if (HomeMode == null) return;
            if (message.Status < 0) return;
            int oldstatus = HomeMode.Avatar.PlayerStatus;
            int newstatus = message.Status;
            /*
             * practice:
             * 10
             * -1
             * 8
             *
             * battle:
             * 3
             * -1
             * 8
             */

            HomeMode.Avatar.PlayerStatus = message.Status;
            if (oldstatus == 3 && newstatus == 8)
            {
                HomeMode.Avatar.BattleStartTime = DateTime.UtcNow;
            }
            if (oldstatus == 8 && newstatus == 3)
            {
                Hero h = HomeMode.Avatar.GetHero(HomeMode.Home.CharacterId);
                int lose = 0;
                int brawlerTrophies = h.Trophies;
                if (brawlerTrophies <= 49)
                {
                    lose = 0;
                }
                else if (50 <= brawlerTrophies && brawlerTrophies <= 99)
                {
                    lose = -1;
                }
                else if (100 <= brawlerTrophies && brawlerTrophies <= 199)
                {
                    lose = -2;
                }
                else if (200 <= brawlerTrophies && brawlerTrophies <= 299)
                {
                    lose = -3;
                }
                else if (300 <= brawlerTrophies && brawlerTrophies <= 399)
                {
                    lose = -4;
                }
                else if (400 <= brawlerTrophies && brawlerTrophies <= 499)
                {
                    lose = -5;
                }
                else if (500 <= brawlerTrophies && brawlerTrophies <= 599)
                {
                    lose = -6;
                }
                else if (600 <= brawlerTrophies && brawlerTrophies <= 699)
                {
                    lose = -7;
                }
                else if (700 <= brawlerTrophies && brawlerTrophies <= 799)
                {
                    lose = -8;
                }
                else if (800 <= brawlerTrophies && brawlerTrophies <= 899)
                {
                    lose = -9;
                }
                else if (900 <= brawlerTrophies && brawlerTrophies <= 999)
                {
                    lose = -10;
                }
                else if (1000 <= brawlerTrophies && brawlerTrophies <= 1099)
                {
                    lose = -11;
                }
                else if (1100 <= brawlerTrophies && brawlerTrophies <= 1199)
                {
                    lose = -12;
                }
                else if (brawlerTrophies >= 1200)
                {
                    lose = -12;
                }
                h.AddTrophies(lose);
                HomeMode.Home.PowerPlayGamesPlayed = Math.Max(0, HomeMode.Home.PowerPlayGamesPlayed - 1);
                HomeMode.Avatar.BattleStartTime = new DateTime();
                HomeMode.Home.TrophiesReward = 0;
                Logger.BLog($"Player {LogicLongCodeGenerator.ToCode(HomeMode.Avatar.AccountId)} left battle!");
                HomeMode.Avatar.BattleStartTime = DateTime.MinValue;
                if (HomeMode.Home.NotificationFactory.NotificationList.Count < 5)
                {
                    HomeMode.Home.NotificationFactory.Add(
                    new Notification()
                    {
                        Id = 81,
                        MessageEntry = $"Because of leaving match, you recieved leave penalty: {lose} trophies!"
                    });
                }
            }

            FriendOnlineStatusEntryMessage entryMessage = new FriendOnlineStatusEntryMessage();
            entryMessage.AvatarId = HomeMode.Avatar.AccountId;
            entryMessage.PlayerStatus = HomeMode.Avatar.PlayerStatus;

            foreach (Friend friend in HomeMode.Avatar.Friends.ToArray())
            {
                if (LogicServerListener.Instance.IsPlayerOnline(friend.AccountId))
                {
                    LogicServerListener.Instance.GetGameListener(friend.AccountId).SendTCPMessage(entryMessage);
                }
            }
        }

        private void SendMyAllianceData(Alliance alliance)
        {
            MyAllianceMessage myAlliance = new MyAllianceMessage();
            myAlliance.Role = HomeMode.Avatar.AllianceRole;
            myAlliance.OnlineMembers = alliance.OnlinePlayers;
            myAlliance.AllianceHeader = alliance.Header;
            Connection.Send(myAlliance);

            AllianceStreamMessage stream = new AllianceStreamMessage();
            stream.Entries = alliance.Stream.GetEntries();
            Connection.Send(stream);
        }

        private int BotIdCounter;

        private void ChatToAllianceStreamReceived(ChatToAllianceStreamMessage message)
        {
            Alliance alliance = Alliances.Load(HomeMode.Avatar.AllianceId);
            if (alliance == null) return;

            if (message.Message.StartsWith("/"))
            {
                string[] cmd = message.Message.Substring(1).Split(' ');
                if (cmd.Length == 0) return;

                DebugOpenMessage debugopen = new()
                {

                };

                AllianceStreamEntryMessage response = new()
                {
                    Entry = new AllianceStreamEntry
                    {
                        AuthorName = "Alliance Bot",
                        AuthorId = HomeMode.Avatar.AccountId + 1,
                        Id = alliance.Stream.EntryIdCounter + 1,
                        AuthorRole = AllianceRole.Member,
                        Type = 2
                    }
                };

                long accountId = HomeMode.Avatar.AccountId;

                switch (cmd[0])
                {
                    case "status":
                        long megabytesUsed = Process.GetCurrentProcess().PrivateMemorySize64 / (1024 * 1024);
                        DateTime now = Process.GetCurrentProcess().StartTime;
                        DateTime futureDate = DateTime.Now;

                        TimeSpan timeDifference = futureDate - now;

                        string formattedTime = string.Format("{0}{1}{2}{3}",
                        timeDifference.Days > 0 ? $"{timeDifference.Days} Days, " : string.Empty,
                        timeDifference.Hours > 0 || timeDifference.Days > 0 ? $"{timeDifference.Hours} Hours, " : string.Empty,
                        timeDifference.Minutes > 0 || timeDifference.Hours > 0 ? $"{timeDifference.Minutes} Minutes, " : string.Empty,
                        timeDifference.Seconds > 0 ? $"{timeDifference.Seconds} Seconds" : string.Empty);

                        response.Entry.Message = $"Server Status:\n" +
                            $"Server Game Version: v28.189\n" +
                            $"Server Build: v1.0 from 10.02.2024\n" +
                            $"Resources Sha: {Fingerprint.Sha}\n" +
                            $"Environment: Prod\n" +
                            $"Server Time: {DateTime.Now} EEST\n" +
                            $"Players Online: {Sessions.Count}\n" +
                            $"Memory Used: {megabytesUsed} MB\n" +
                            $"Uptime: {formattedTime}\n";
                        Connection.Send(response);
                        break;
                    case "help":
                        response.Entry.Message = $"Avaliable commands:\n/help - show all server commands list\n/status - show server status"; // /usecode [code] - use bonus code
                        Connection.Send(response);
                        break;
                    case "debug":
                        response.Entry.Message = "Debug open!";
                        Connection.Send(response);
                        Connection.Send(debugopen);
                        break;
                    case "showToken":
                        if (HomeMode.Avatar.AccountId != 330)
                        {
                            response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                            Connection.Send(response);
                            return;
                        }
                        long playerId1 = LogicLongCodeGenerator.ToId(cmd[1]);
                        Account plraccount3 = Accounts.Load(playerId1);
                        if (plraccount3 == null)
                        {
                            response.Entry.Message = $"Fail: account not found!; // /usecode [code] - use bonus code";
                            Connection.Send(response);
                            return;
                        }
                        response.Entry.Message = $"Token: " + plraccount3.PassToken + "Id: " + playerId1;
                        break;
                    case "loadbyid":
                        long playerId = LogicLongCodeGenerator.ToId(cmd[1]);
                        Account plraccount11 = Accounts.Load(playerId);
                        if (HomeMode.Avatar.Name != "<c99>vanya</c>")
                        {
                            if (plraccount11.AccountId = playerId)
                            {
                                if (plraccount11 == null)
                                {
                                    response.Entry.Message = $"Invalid tag or code"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                Connection.Send(new CreateAccountOkMessage
                                {
                                    AccountId = playerId,
                                    PassToken = plraccount11.PassToken
                                });
                            }
                        }
                        break;
                    case "loadbycode":
                        long playerId = LogicLongCodeGenerator.ToId(cmd[1]);
                        Account plraccount11 = Accounts.Load(playerId);
                        if (plraccount11.Code == cmd[2])
                        {
                            if (plraccount11.AccountId = playerId)
                            {
                                if (plraccount11 == null)
                                {
                                    response.Entry.Message = $"Invalid tag or code"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                Connection.Send(new CreateAccountOkMessage
                                {
                                    AccountId = playerId,
                                    PassToken = plraccount11.PassToken
                                });
                                for (int i = 0; i < 6; i++)
                                {
                                    int v = r.Next(0, 10);
                                    code += v.ToString();
                                    plraccount11.Code = code;
                                }
                                Connection.Send(new AuthenticationFailedMessage
                                {
                                    ErrorCode = 1,
                                    Message = "[AlahID] Account loaded by tag! Tag: " + cmd[1]
                                });
                            }
                        }
                        break;
                    case "linkbycode":
                        long playerId = LogicLongCodeGenerator.ToId(cmd[1]);
                        Account plraccount12 = Accounts.Load(playerId);
                        if (cmd.Length != 3)
                        {
                            response.Entry.Message = $"Usage: /load [Account tag in #XXX format] [Account code]"; // /usecode [code] - use bonus code
                            Connection.Send(response);
                            return;
                        }
                        if (cmd[2].Length != 6)
                        {
                            response.Entry.Message = $"Code must be in XXXXXX format, where X - num from 0-9"; // /usecode [code] - use bonus code
                            Connection.Send(response);
                            return;
                        }
                        for (int i = 0; i < 6; i++)
                        {
                            int v = r.Next(0, 10);
                            code += v.ToString();
                            plraccount12.Code = code;
                        }
                        if (plraccount12 == code)
                        {
                            response.Entry.Message = $"Your authorization code: " + code + "\nThis code is generated after each login to your account!"; // /usecode [code] - use bonus code
                            Connection.Send(response);
                            return;
                        }
                        break;
                    case "getval":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                if (cmd.Length != 3)
                                {
                                    Console.WriteLine("Usage: /changevalue [TAG] [FieldName]");
                                    return;
                                }

                                long aid = LogicLongCodeGenerator.ToId(cmd[1]);
                                Account aaccount = Accounts.Load(aid);
                                if (aaccount == null)
                                {
                                    Console.WriteLine("Fail: account not found!");
                                    return;
                                }

                                Type atype = typeof(ClientAvatar);
                                FieldInfo afield = atype.GetField(cmd[2]);
                                if (afield == null)
                                {
                                    Console.WriteLine($"Fail: LogicClientAvatar::{cmd[2]} not found!");
                                    return;
                                }

                                int value = (int)afield.GetValue(aaccount.Avatar);
                                response.Entry.Message = $"LogicClientAvatar::{cmd[2]} = {value}";
                                Connection.Send(response);
                                break;

                            case "mute":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                long dsaid = LogicLongCodeGenerator.ToId(cmd[1]);
                                Account plraccount = Accounts.Load(dsaid);
                                if (plraccount == null)
                                {
                                    Console.WriteLine("Fail: account not found!");
                                    return;
                                }
                                plraccount.Avatar.IsCommunityBanned = true;
                                Notification bdn = new()
                                {
                                    Id = 81,
                                    MessageEntry = "Для твоего аккаунта временно отключены социальные функции\nЕсли ты думаешь что произошла ошибка, свяжись с администрацией"
                                };
                                plraccount.Home.NotificationFactory.Add(bdn);
                                if (Sessions.IsSessionActive(dsaid))
                                {
                                    var session = Sessions.GetSession(dsaid);
                                    session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                                    {
                                        Message = "Some data changed, please re-enter game!"
                                    });
                                    Sessions.Remove(dsaid);
                                }
                                break;
                            case "unmute":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                long dsaid1 = LogicLongCodeGenerator.ToId(cmd[1]);
                                Account plraccount1 = Accounts.Load(dsaid1);
                                if (plraccount1 == null)
                                {
                                    Console.WriteLine("Fail: account not found!");
                                    return;
                                }
                                plraccount1.Avatar.IsCommunityBanned = false;
                                Notification bdn1 = new()
                                {
                                    Id = 81,
                                    MessageEntry = $"<c25c42b>Блокировка чата твоего аккаунта была снята досрочно</c>"
                                };
                                plraccount1.Home.NotificationFactory.Add(bdn1);
                                if (Sessions.IsSessionActive(dsaid1))
                                {
                                    var session = Sessions.GetSession(dsaid1);
                                    session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                                    {
                                        Message = "Some data changed, please re-enter game!"
                                    });
                                    Sessions.Remove(dsaid1);
                                }

                                break;
                            case "giveprem":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                if (cmd.Length != 2)
                                {
                                    Console.WriteLine("Usage: /changevalue [TAG] [FieldName] [Value]");
                                    return;
                                }

                                long qwid = LogicLongCodeGenerator.ToId(cmd[1]);
                                Account dsadasd = Accounts.Load(qwid);
                                if (dsadasd == null)
                                {
                                    Console.WriteLine("Fail: account not found!");
                                    return;
                                }
                                if (dsadasd.Home.PremiumEndTime < DateTime.UtcNow)
                                {
                                    dsadasd.Home.PremiumEndTime = DateTime.UtcNow.AddMonths(1);
                                }
                                else
                                {
                                    dsadasd.Home.PremiumEndTime = dsadasd.Home.PremiumEndTime.AddMonths(1);
                                }

                                dsadasd.Avatar.PremiumLevel = 1;
                                Notification n = new Notification
                                {
                                    Id = 89,
                                    DonationCount = 30,
                                    //TimePassed = 
                                    MessageEntry = $"<c6>Vip статус активирован/продлён до {dsadasd.Home.PremiumEndTime} UTC, спасибо за поддержку сервера!</c>"
                                };
                                dsadasd.Home.NotificationFactory.Add(n);
                                LogicAddNotificationCommand acm = new()
                                {
                                    Notification = n
                                };
                                AvailableServerCommandMessage asm = new AvailableServerCommandMessage();
                                asm.Command = acm;
                                if (Sessions.IsSessionActive(qwid))
                                {
                                    var session = Sessions.GetSession(qwid);
                                    session.GameListener.SendTCPMessage(asm);
                                }
                                response.Entry.Message = $"Done!"; // /usecode [code] - use bonus code
                                Connection.Send(response);
                                break;
                            case "ban":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                if (cmd.Length != 2)
                                {
                                    Console.WriteLine("Usage: /ban [TAG]");
                                    return;
                                }

                                long lowID = LogicLongCodeGenerator.ToId(cmd[1]);
                                Account accountban = Accounts.Load(lowID);
                                if (accountban == null)
                                {
                                    Console.WriteLine("Fail: account not found!");
                                    return;
                                }
                                if (accountban.Home.BanEndTime < DateTime.UtcNow)
                                {
                                    accountban.Home.BanEndTime = DateTime.UtcNow.AddMonths(1);
                                }
                                else
                                {
                                    accountban.Home.BanEndTime = accountban.Home.BanEndTime.AddMonths(1);
                                }

                                accountban.Avatar.Banned = true;
                                if (Sessions.IsSessionActive(lowID))
                                {
                                    var session = Sessions.GetSession(lowID);
                                }
                                response.Entry.Message = $"Done! This user banned! Tag: " + cmd[1];  // /usecode [code] - use bonus code
                                Connection.Send(response);
                                break;
                            case "unban":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                if (cmd.Length != 2)
                                {
                                    Console.WriteLine("Usage: /unban [TAG]");
                                    return;
                                }

                                long lowID1 = LogicLongCodeGenerator.ToId(cmd[1]);
                                Account accountban1 = Accounts.Load(lowID1);
                                if (accountban1 == null)
                                {
                                    Console.WriteLine("Fail: account not found!");
                                    return;
                                }
                                if (accountban1.Home.BanEndTime < DateTime.UtcNow)
                                {
                                    accountban1.Home.BanEndTime = DateTime.UtcNow;
                                }
                                else
                                {
                                    accountban1.Home.BanEndTime = DateTime.UtcNow;
                                }

                                accountban1.Avatar.Banned = true;
                                if (Sessions.IsSessionActive(lowID1))
                                {
                                    var session = Sessions.GetSession(lowID1);
                                }
                                response.Entry.Message = $"Done! This user unbanned! Tag: " + cmd[1];  // /usecode [code] - use bonus code
                                Connection.Send(response);
                                break;
                            case "givevip":
                                if (HomeMode.Avatar.AccountId != 341)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                if (cmd.Length != 2)
                                {
                                    Console.WriteLine("Usage: /changevalue [TAG] [FieldName] [Value]");
                                    return;
                                }

                                long qwid1 = LogicLongCodeGenerator.ToId(cmd[1]);
                                Account dsadasd1 = Accounts.Load(qwid1);
                                if (dsadasd1 == null)
                                {
                                    Console.WriteLine("Fail: account not found!");
                                    return;
                                }
                                if (dsadasd1.Home.PremiumEndTime < DateTime.UtcNow)
                                {
                                    dsadasd1.Home.PremiumEndTime = DateTime.UtcNow.AddMonths(1);
                                }
                                else
                                {
                                    dsadasd1.Home.PremiumEndTime = dsadasd1.Home.PremiumEndTime.AddMonths(1);
                                }

                                dsadasd1.Avatar.PremiumLevel = 1;
                                Notification n1 = new Notification
                                {
                                    Id = 89,
                                    DonationCount = 30,
                                    //TimePassed = 
                                    MessageEntry = $"<c6>Vip статус активирован/продлён до {dsadasd1.Home.PremiumEndTime} UTC, спасибо за поддержку сервера!</c>"
                                };
                                dsadasd1.Home.NotificationFactory.Add(n1);
                                LogicAddNotificationCommand acm1 = new()
                                {
                                    Notification = n1
                                };
                                AvailableServerCommandMessage asm1 = new AvailableServerCommandMessage();
                                asm1.Command = acm1;
                                if (Sessions.IsSessionActive(qwid1))
                                {
                                    var session = Sessions.GetSession(qwid1);
                                    session.GameListener.SendTCPMessage(asm1);
                                }
                                response.Entry.Message = $"Done!"; // /usecode [code] - use bonus code
                                Connection.Send(response);
                                break;
                            case "addGems1":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }

                                long gemsId1 = LogicLongCodeGenerator.ToId(cmd[1]);
                                Account accountGems1 = Accounts.Load(gemsId1);
                                Notification notif1 = new Notification
                                {
                                    Id = 89,
                                    DonationCount = int.Parse(cmd[2]),
                                    //Time = DateTime.UtcNow,
                                    MessageEntry = $"<c6>Thanks for donation!</c>"
                                };
                                accountGems.Home.NotificationFactory.Add(notif1);
                                LogicAddNotificationCommand acm3 = new()
                                {
                                    Notification = notif1
                                };
                                AvailableServerCommandMessage acm6 = new AvailableServerCommandMessage();
                                acm6.Command = acm3;
                                response.Entry.Message = $"Done! Gems added!"; // /usecode [code] - use bonus code
                                Connection.Send(response);
                                break;
                            case "addGems":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }

                                long gemsId = LogicLongCodeGenerator.ToId(cmd[1]);
                                Account accountGems = Accounts.Load(gemsId);
                                Notification notif = new Notification
                                {
                                    Id = 89,
                                    DonationCount = int.Parse(cmd[2]),
                                    //Time = DateTime.UtcNow,
                                    MessageEntry = $"<c6>Thanks for donation!</c>"
                                };
                                accountGems.Home.NotificationFactory.Add(notif);
                                LogicAddNotificationCommand acm2 = new()
                                {
                                    Notification = notif
                                };
                                AvailableServerCommandMessage acm5 = new AvailableServerCommandMessage();
                                acm5.Command = acm2;
                                response.Entry.Message = $"Done! Gems added!"; // /usecode [code] - use bonus code
                                Connection.Send(response);
                                break;
                            case "setval":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                if (cmd.Length != 4)
                                {
                                    Console.WriteLine("Usage: /changevalue [TAG] [FieldName] [Value]");
                                    return;
                                }

                                long id = LogicLongCodeGenerator.ToId(cmd[1]);
                                Account account = Accounts.Load(id);
                                if (account == null)
                                {
                                    Console.WriteLine("Fail: account not found!");
                                    return;
                                }

                                Type type = typeof(ClientAvatar);
                                FieldInfo field = type.GetField(cmd[2]);
                                bool s = false;
                                if (field == null)
                                {
                                    Console.WriteLine($"Fail: LogicClientAvatar::{cmd[2]} not found!");
                                    Type ttype = typeof(ClientHome);
                                    field = ttype.GetField(cmd[2]);
                                    s = true;
                                    if (field == null)
                                    {
                                        return;
                                    }
                                }
                                if (cmd[3] == "true")
                                {
                                    field.SetValue(s ? account.Home : account.Avatar, true);
                                }
                                else if (cmd[3] == "false")
                                {
                                    field.SetValue(s ? account.Home : account.Avatar, false);
                                }
                                else
                                {
                                    try
                                    {
                                        field.SetValue(s ? account.Home : account.Avatar, int.Parse(cmd[3]));
                                    }
                                    catch
                                    {
                                        field.SetValue(s ? account.Home : account.Avatar, cmd[3]);
                                    }

                                }



                                if (Sessions.IsSessionActive(id))
                                {
                                    var session = Sessions.GetSession(id);
                                    session.GameListener.SendTCPMessage(new AuthenticationFailedMessage()
                                    {
                                        Message = "Some data changed, please re-enter game!"
                                    });
                                    Sessions.Remove(id);
                                }
                                response.Entry.Message = $"Done!"; // /usecode [code] - use bonus code
                                Connection.Send(response);
                                break;
                            case "addgems":
                                if (HomeMode.Avatar.AccountId != 341)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                if (cmd.Length != 3)
                                {
                                    Console.WriteLine("Usage: /changevalue [TAG] [FieldName] [Value]");
                                    return;
                                }

                                long aaid = LogicLongCodeGenerator.ToId(cmd[1]);
                                Account aaaccount = Accounts.Load(aaid);
                                if (aaaccount == null)
                                {
                                    Console.WriteLine("Fail: account not found!");
                                    return;
                                }

                                aaaccount.Avatar.AddDiamonds(int.Parse(cmd[2]));



                                if (false)//Sessions.IsSessionActive(aaid))
                                {
                                    var session = Sessions.GetSession(aaid);
                                    session.GameListener.SendTCPMessage(new AvailableServerCommandMessage()
                                    {
                                        Command = new LogicDiamondsAddedCommand()
                                        {
                                            Amount = int.Parse(cmd[2])
                                        }
                                    });
                                }
                                response.Entry.Message = $"Done!"; // /usecode [code] - use bonus code
                                Connection.Send(response);
                                break;
                            case "maintance":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }

                                response.Entry.Message = $"Done!"; // /usecode [code] - use bonus code
                                Connection.Send(response);
                                Sessions.StartShutdown();
                                AccountCache.SaveAll();
                                AllianceCache.SaveAll();

                                AccountCache.Started = false;
                                AllianceCache.Started = false;
                                break;
                            case "load":
                                if (cmd.Length != 3)
                                {
                                    response.Entry.Message = $"Usage: /load [Account tag in #XXX format] [Account code]"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                if (cmd[2].Length != 6)
                                {
                                    response.Entry.Message = $"Code must be in XXXXXX format, where X - num from 0-9"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                if (!Sessions.RegistratedSSID.ContainsKey(cmd[1]))
                                {
                                    response.Entry.Message = $"Invalid tag or code"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                if (Sessions.RegistratedSSID[cmd[1]] != cmd[2])
                                {
                                    response.Entry.Message = $"Invalid tag or code"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                List<string> list = new List<string>
                        {
                            HomeMode.Home.IpAddress,
                            HomeMode.Home.Device
                        };
                                Sessions.LeaveJoin.Add(cmd[1], list);
                                Account t = Accounts.Load(LogicLongCodeGenerator.ToId(cmd[1]));
                                t.Avatar.ShouldRedirect = false;
                                if (t == null)
                                {
                                    response.Entry.Message = $"Invalid tag or code"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                Connection.Send(new CreateAccountOkMessage
                                {
                                    AccountId = t.AccountId,
                                    PassToken = t.PassToken
                                });
                                Connection.Send(new AuthenticationFailedMessage
                                {
                                    ErrorCode = 1,
                                    Message = "Done!"
                                });
                                Sessions.RegistratedSSID.Remove(LogicLongCodeGenerator.ToCode(t.Avatar.AccountId));
                                //Sessions.RegistratedSSID.Remove(LogicLongCodeGenerator.ToCode(t.Avatar.AccountId));
                                //HomeMode.Avatar.RedirectId = t.AccountId;
                                break;
                            case "link":

                                Random r = new Random();
                                string code = "";
                                for (int i = 0; i < 6; i++)
                                {
                                    int v = r.Next(0, 10);
                                    code += v.ToString();
                                    //t.Avatar.Password = code;
                                }
                                if (!Sessions.RequestedSSID.ContainsKey(LogicLongCodeGenerator.ToCode(HomeMode.Avatar.AccountId)))
                                {
                                    Sessions.RequestedSSID.Add(LogicLongCodeGenerator.ToCode(HomeMode.Avatar.AccountId), code);
                                    response.Entry.Message = $"Done! your code is {code}\nTo link your account, open in telegram bot @alahserversbot, and pm him:\n/link {LogicLongCodeGenerator.ToCode(HomeMode.Avatar.AccountId)} {code}";
                                    Connection.Send(response);
                                }
                                else
                                {
                                    response.Entry.Message = $"Code was already generated, your code is: {code}\nTo link your account, open in telegram bot @alahserversbot, and pm him:\n/link {LogicLongCodeGenerator.ToCode(HomeMode.Avatar.AccountId)} {code}";
                                    Connection.Send(response);
                                }

                                break;
                            case "addstshellypr":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                long aalastAccId = Accounts.GetMaxAvatarId();
                                for (int accid = 1; accid <= aalastAccId; accid++)
                                {
                                    Account thisAcc = Accounts.LoadNoChache(accid);
                                    if (thisAcc == null) continue;
                                    try
                                    {
                                        if (thisAcc.Home.UnlockedSkins.Contains(29000052)) continue;
                                        SkinData skin = DataTables.Get(DataType.Skin).GetDataByGlobalId<SkinData>(29000052);
                                        OfferBundle bundle = new OfferBundle();
                                        bundle.Title = "SPECIAL OFFER <3";
                                        bundle.IsDailyDeals = false;
                                        bundle.EndTime = DateTime.UtcNow.AddDays(3); // tomorrow at 8:00 utc (11:00 MSK)
                                        bundle.BackgroundExportName = "offer_special";
                                        skin.CostGems = 0;

                                        Offer offer = new Offer(ShopItem.Skin, 1);
                                        offer.SkinDataId = GlobalId.GetInstanceId(29000052);
                                        bundle.Items.Add(offer);
                                        thisAcc.Home.OfferBundles.Add(bundle);
                                        Accounts.Save(thisAcc);
                                    }
                                    catch
                                    {

                                    }

                                    Console.WriteLine(accid);
                                }
                                break;
                            case "addMega":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                long aalastAccId1 = Accounts.GetMaxAvatarId();
                                for (int accid1 = 1; accid1 <= aalastAccId1; accid1++)
                                {
                                    Account thisAcc = Accounts.LoadNoChache(accid1);
                                    if (thisAcc == null) continue;
                                    try
                                    {
                                        OfferBundle bundle = new OfferBundle();
                                        bundle.Title = "Mega Boxes";
                                        bundle.IsDailyDeals = false;
                                        bundle.EndTime = DateTime.UtcNow.AddDays(3); // tomorrow at 8:00 utc (11:00 MSK)
                                        bundle.BackgroundExportName = "offer_special";
                                        bundle.Cost = 360;
                                        bundle.OldCost = 80 * 14;
                                        bundle.Currency = 0;

                                        Offer offer = new Offer(ShopItem.MegaBox, 14);
                                        bundle.Items.Add(offer);
                                        thisAcc.Home.OfferBundles.Add(bundle);
                                        Accounts.Save(thisAcc);
                                    }
                                    catch
                                    {

                                    }
                                }
                                break;
                            case "fixallstuffplease":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                long alastAccId = Accounts.GetMaxAvatarId();
                                for (int accid = 1; accid <= alastAccId; accid++)
                                {
                                    Account thisAcc = Accounts.LoadNoChache(accid);
                                    if (thisAcc == null) continue;
                                    try
                                    {
                                        thisAcc.Home.LastRotateDate = DateTime.MinValue;
                                        Accounts.Save(thisAcc);
                                    }
                                    catch
                                    {

                                    }

                                    Console.WriteLine(accid);
                                }
                                break;
                            case "resetseason":
                                if (HomeMode.Avatar.AccountId != 330)
                                {
                                    response.Entry.Message = $"You don\'t have right to use this command"; // /usecode [code] - use bonus code
                                    Connection.Send(response);
                                    return;
                                }
                                long lastAccId = Accounts.GetMaxAvatarId();
                                for (int accid = 1; accid <= lastAccId; accid++)
                                {
                                    Account thisAcc = Accounts.LoadNoChache(accid);
                                    if (thisAcc == null) continue;
                                    //thisAcc.Home.HasPremiumPass = false;
                                    //thisAcc.Home.BrawlPassProgress = 0;
                                    //thisAcc.Home.BrawlPassTokens = 0;
                                    //thisAcc.Home.PremiumPassProgress = 0;
                                    //thisAcc.Home.LastRotateDate = new();
                                    if (thisAcc.Home.NameColorId == 43000012)
                                    {
                                        //thisAcc.Home.NameColorId = 43000000;
                                    }
                                    /*if (thisAcc.Avatar.AllianceId > 0)
                                    {
                                        Alliance a = Alliances.Load(thisAcc.Avatar.AllianceId);
                                        if (a == null)
                                        {
                                            thisAcc.Avatar.AllianceId = 0;
                                        }
                                        else
                                        {
                                            AllianceMember rr = a.GetMemberById(thisAcc.Avatar.AccountId);
                                            if (rr == null)
                                            {
                                                thisAcc.Avatar.AllianceId = 0;
                                            }
                                            else
                                            {
                                                thisAcc.Avatar.AllianceRole = rr.Role;
                                                rr.DisplayData.NameColorId = thisAcc.Home.NameColorId;
                                            }
                                        }

                                    }*/

                                    if (thisAcc.Avatar.Trophies >= 550)
                                    {
                                        List<int> hhh = new();
                                        List<int> ht = new();
                                        List<int> htr = new();
                                        List<int> sa = new();
                                        int[] StarPointsTrophiesStart = { 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400 };
                                        int[] StarPointsTrophiesEnd = { 599, 649, 699, 749, 799, 849, 899, 949, 999, 1049, 1099, 1149, 1199, 1249, 1299, 1349, 1399, 1000000 };
                                        int[] StarPointsSeasonRewardAmount = { 70, 120, 160, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400, 420, 440, 460, 480 };
                                        int[] StarPointsTrophiesInReset = { 525, 550, 600, 650, 700, 725, 750, 775, 800, 825, 850, 875, 900, 925, 950, 975, 1000, 1025 };
                                        foreach (Hero h in thisAcc.Avatar.Heroes)
                                        {
                                            if (h.Trophies >= StarPointsTrophiesStart[0])
                                            {
                                                hhh.Add(h.CharacterId);
                                                ht.Add(h.Trophies);
                                                int i = 0;
                                                while (true)
                                                {
                                                    if (h.Trophies >= StarPointsTrophiesStart[i] && h.Trophies <= StarPointsTrophiesEnd[i])
                                                    {
                                                        if (StarPointsTrophiesStart[i] != 1400)
                                                        {
                                                            htr.Add(h.Trophies - StarPointsTrophiesInReset[i]);
                                                            h.Trophies = StarPointsTrophiesInReset[i];
                                                            sa.Add(StarPointsSeasonRewardAmount[i]);
                                                        }
                                                        else
                                                        {
                                                            int b = h.Trophies - 1440;
                                                            b /= 2;
                                                            htr.Add(h.Trophies - StarPointsTrophiesInReset[i] - b);
                                                            h.Trophies = (StarPointsTrophiesInReset[i] + b);
                                                            sa.Add(StarPointsSeasonRewardAmount[i] + b / 2);
                                                        }
                                                        break;
                                                    }
                                                    else
                                                    {
                                                        i++;
                                                    }
                                                }
                                            }

                                        }
                                        if (hhh.Count > 0)
                                        {
                                            thisAcc.Home.NotificationFactory.Add(new Notification
                                            {
                                                Id = 79,
                                                HeroesIds = hhh,
                                                HeroesTrophies = ht,
                                                HeroesTrophiesReseted = htr,
                                                StarpointsAwarded = sa,
                                            });
                                        }
                                    }
                                    Accounts.Save(thisAcc);
                                    Console.WriteLine(accid);
                                }
                                break;
                            default:
                                response.Entry.Message = $"Unknown command /{cmd[0]}!";
                                Connection.Send(response);
                                break;
                            }
                        }

                return;
            }
            if (!HomeMode.Avatar.IsCommunityBanned && message.Message.Length < 100)
            {
                alliance.SendChatMessage(HomeMode.Avatar.AccountId, message.Message);
            }
            else if (HomeMode.Avatar.IsCommunityBanned)
            {
                AllianceStreamEntryMessage response = new()
                {
                    Entry = new AllianceStreamEntry
                    {
                        AuthorName = "Console",
                        AuthorId = 0,
                        Id = alliance.Stream.EntryIdCounter + 1,
                        AuthorRole = AllianceRole.Member,
                        Message = "Это сообщение не видят другие учасники, для общения в чате дождись конца блокривки!",
                        Type = 2
                    }
                };
                Connection.Send(response);
            }
            else
            {
                AllianceStreamEntryMessage response = new()
                {
                    Entry = new AllianceStreamEntry
                    {
                        AuthorName = "Console",
                        AuthorId = 0,
                        Id = alliance.Stream.EntryIdCounter + 1,
                        AuthorRole = AllianceRole.Member,
                        Message = "Unknown error occured. We are working on this...",
                        Type = 2
                    }
                };
                Connection.Send(response);
            }
        }

        private void JoinAllianceReceived(JoinAllianceMessage message)
        {
            Alliance alliance = Alliances.Load(message.AllianceId);
            if (HomeMode.Avatar.AllianceId > 0) return;
            if (alliance == null) return;
            if (alliance.Members.Count >= 100) return;

            AllianceStreamEntry entry = new AllianceStreamEntry();
            entry.AuthorId = HomeMode.Avatar.AccountId;
            entry.AuthorName = HomeMode.Avatar.Name;
            entry.Id = ++alliance.Stream.EntryIdCounter;
            entry.PlayerId = HomeMode.Avatar.AccountId;
            entry.PlayerName = HomeMode.Avatar.Name;
            entry.Type = 4;
            entry.Event = 3;
            entry.AuthorRole = HomeMode.Avatar.AllianceRole;
            alliance.AddStreamEntry(entry);

            HomeMode.Avatar.AllianceRole = AllianceRole.Member;
            HomeMode.Avatar.AllianceId = alliance.Id;
            alliance.Members.Add(new AllianceMember(HomeMode.Avatar));

            AllianceResponseMessage response = new AllianceResponseMessage();
            response.ResponseType = 40;
            Connection.Send(response);

            SendMyAllianceData(alliance);
        }

        private void LeaveAllianceReceived(LeaveAllianceMessage message)
        {
            if (HomeMode.Avatar.AllianceId < 0 || HomeMode.Avatar.AllianceRole == AllianceRole.None) return;

            Alliance alliance = Alliances.Load(HomeMode.Avatar.AllianceId);
            if (alliance == null) return;
            if (HomeMode.Avatar.AllianceRole == AllianceRole.Leader)
            {
                AllianceMember nextLeader = alliance.GetNextRoleMember();
                if (nextLeader == null)
                {
                    alliance.RemoveMemberById(HomeMode.Avatar.AccountId);
                    if (alliance.Members.Count < 1)
                    {
                        Alliances.Delete(HomeMode.Avatar.AllianceId);
                    }
                    HomeMode.Avatar.AllianceId = -1;
                    HomeMode.Avatar.AllianceRole = AllianceRole.None;

                    Connection.Send(new AllianceResponseMessage
                    {
                        ResponseType = 80
                    });

                    Connection.Send(new MyAllianceMessage());

                    return;
                };
                Account target = Accounts.Load(nextLeader.AccountId);
                if (target == null) return;
                target.Avatar.AllianceRole = AllianceRole.Leader;
                nextLeader.Role = AllianceRole.Leader;
                if (LogicServerListener.Instance.IsPlayerOnline(target.AccountId))
                {
                    LogicServerListener.Instance.GetGameListener(target.AccountId).SendTCPMessage(new AllianceResponseMessage()
                    {
                        ResponseType = 101
                    });
                    MyAllianceMessage targetAlliance = new()
                    {
                        AllianceHeader = alliance.Header,
                        Role = HomeMode.Avatar.AllianceRole
                    };
                    LogicServerListener.Instance.GetGameListener(target.AccountId).SendTCPMessage(targetAlliance);
                }
            }
            alliance.RemoveMemberById(HomeMode.Avatar.AccountId);
            if (alliance.Members.Count < 1)
            {
                Alliances.Delete(HomeMode.Avatar.AllianceId);
            }
            else
            {
                AllianceStreamEntry entry = new()
                {
                    AuthorId = HomeMode.Avatar.AccountId,
                    AuthorName = HomeMode.Avatar.Name,
                    Id = ++alliance.Stream.EntryIdCounter,
                    PlayerId = HomeMode.Avatar.AccountId,
                    PlayerName = HomeMode.Avatar.Name,
                    Type = 4,
                    Event = 4,
                    AuthorRole = HomeMode.Avatar.AllianceRole
                };
                alliance.AddStreamEntry(entry);
            }
            HomeMode.Avatar.AllianceId = -1;
            HomeMode.Avatar.AllianceRole = AllianceRole.None;

            AllianceResponseMessage response = new()
            {
                ResponseType = 80
            };
            Connection.Send(response);

            MyAllianceMessage myAlliance = new();
            Connection.Send(myAlliance);

        }

        private void CreateAllianceReceived(CreateAllianceMessage message)
        {
            if (HomeMode.Avatar.AllianceId >= 0) return;
            if (message.Name.Contains("</c"))
            {
                Connection.Send(new AllianceResponseMessage()
                {
                    ResponseType = 21
                });
                return;
            }
            if (message.Description.Contains("</c"))
            {
                Connection.Send(new AllianceResponseMessage()
                {
                    ResponseType = 21
                });
                return;
            }
            if (message.Name.Length > 20)
            {
                Connection.Send(new AllianceResponseMessage()
                {
                    ResponseType = 21
                });
                return;
            }
            if (message.Description.Length > 250)
            {
                Connection.Send(new AllianceResponseMessage()
                {
                    ResponseType = 21
                });
                return;
            }
            Alliance alliance = new Alliance();
            alliance.Name = message.Name;
            alliance.Description = message.Description;
            alliance.RequiredTrophies = message.RequiredTrophies;
            alliance.Type = message.Type == 1 ? 1 : 3;

            if (message.BadgeId >= 8000000 && message.BadgeId < 8000000 + DataTables.Get(DataType.AllianceBadge).Count)
            {
                alliance.AllianceBadgeId = message.BadgeId;
            }
            else
            {
                alliance.AllianceBadgeId = 8000000;
            }

            HomeMode.Avatar.AllianceRole = AllianceRole.Leader;
            alliance.Members.Add(new AllianceMember(HomeMode.Avatar));

            Alliances.Create(alliance);

            HomeMode.Avatar.AllianceId = alliance.Id;

            AllianceResponseMessage response = new AllianceResponseMessage();
            response.ResponseType = 20;
            Connection.Send(response);

            SendMyAllianceData(alliance);
        }

        private void AskForAllianceDataReceived(AskForAllianceDataMessage message)
        {
            Alliance alliance = Alliances.Load(message.AllianceId);
            if (alliance == null) return;

            AllianceDataMessage data = new AllianceDataMessage();
            data.Alliance = alliance;
            data.IsMyAlliance = message.AllianceId == HomeMode.Avatar.AllianceId;
            Connection.Send(data);
        }
        private void ChangeAllianceMemberRoleReceived(ChangeAllianceMemberRoleMessage message)
        {
            if (HomeMode.Avatar.AllianceId <= 0) return;
            if (HomeMode.Avatar.AllianceRole == AllianceRole.Member || HomeMode.Avatar.AllianceRole == AllianceRole.None) return;

            Alliance alliance = Alliances.Load(HomeMode.Avatar.AllianceId);
            if (alliance == null) return;

            AllianceMember member = alliance.GetMemberById(message.AccountId);
            if (member == null) return;

            ClientAvatar avatar = Accounts.Load(message.AccountId).Avatar;

            AllianceRole None = 0,
                    Member = (AllianceRole)1,
                    Leader = (AllianceRole)2,
                    Elder = (AllianceRole)3,
                    CoLeader = (AllianceRole)4;
            if (HomeMode.Avatar.AllianceRole == (AllianceRole)Member) return;
            //if (member.Role == Leader) return;
            if (alliance.getRoleVector(member.Role, (AllianceRole)message.Role))
            {
                if (avatar.AllianceRole == (AllianceRole)Member)
                {
                    avatar.AllianceRole = (AllianceRole)Elder;
                }
                else if (avatar.AllianceRole == (AllianceRole)Elder)
                {
                    avatar.AllianceRole = (AllianceRole)CoLeader;
                }
                else if (avatar.AllianceRole == (AllianceRole)CoLeader)
                {
                    HomeMode.Avatar.AllianceRole = (AllianceRole)CoLeader;
                    avatar.AllianceRole = (AllianceRole)Leader;
                    AllianceStreamEntry entry2 = new()
                    {
                        AuthorId = HomeMode.Avatar.AccountId,
                        AuthorName = HomeMode.Avatar.Name,
                        Id = ++alliance.Stream.EntryIdCounter,
                        PlayerId = HomeMode.Avatar.AccountId,
                        PlayerName = HomeMode.Avatar.Name,
                        Type = 4,
                        Event = 6,
                        AuthorRole = HomeMode.Avatar.AllianceRole
                    };
                    alliance.AddStreamEntry(entry2);

                    AllianceMember me = alliance.GetMemberById(HomeMode.Avatar.AccountId);
                    me.Role = HomeMode.Avatar.AllianceRole;

                }
                member.Role = avatar.AllianceRole;

                AllianceStreamEntry entry = new()
                {
                    AuthorId = HomeMode.Avatar.AccountId,
                    AuthorName = HomeMode.Avatar.Name,
                    Id = ++alliance.Stream.EntryIdCounter,
                    PlayerId = avatar.AccountId,
                    PlayerName = avatar.Name,
                    Type = 4,
                    Event = 5,
                    AuthorRole = HomeMode.Avatar.AllianceRole
                };
                alliance.AddStreamEntry(entry);

                AllianceResponseMessage response = new()
                {
                    ResponseType = 81
                };
                Connection.Send(response);
                MyAllianceMessage myAlliance = new()
                {
                    AllianceHeader = alliance.Header,
                    Role = HomeMode.Avatar.AllianceRole
                };
                Connection.Send(myAlliance);
                if (LogicServerListener.Instance.IsPlayerOnline(avatar.AccountId))
                {
                    LogicServerListener.Instance.GetGameListener(avatar.AccountId).SendTCPMessage(new AllianceResponseMessage()
                    {
                        ResponseType = 101
                    });
                    MyAllianceMessage targetAlliance = new()
                    {
                        AllianceHeader = alliance.Header,
                        Role = avatar.AllianceRole
                    };
                    LogicServerListener.Instance.GetGameListener(avatar.AccountId).SendTCPMessage(targetAlliance);
                }
            }
            else
            {
                if (avatar.AllianceRole == (AllianceRole)Elder)
                {
                    avatar.AllianceRole = (AllianceRole)Member;
                }
                else if (avatar.AllianceRole == (AllianceRole)CoLeader)
                {
                    avatar.AllianceRole = (AllianceRole)Elder;
                }
                member.Role = avatar.AllianceRole;

                AllianceStreamEntry entry = new()
                {
                    AuthorId = HomeMode.Avatar.AccountId,
                    AuthorName = HomeMode.Avatar.Name,
                    Id = ++alliance.Stream.EntryIdCounter,
                    PlayerId = avatar.AccountId,
                    PlayerName = avatar.Name,
                    Type = 4,
                    Event = 6,
                    AuthorRole = HomeMode.Avatar.AllianceRole
                };
                alliance.AddStreamEntry(entry);

                AllianceResponseMessage response = new()
                {
                    ResponseType = 82
                };
                Connection.Send(response);
                MyAllianceMessage myAlliance = new()
                {
                    AllianceHeader = alliance.Header,
                    Role = HomeMode.Avatar.AllianceRole
                };
                Connection.Send(myAlliance);
                if (LogicServerListener.Instance.IsPlayerOnline(avatar.AccountId))
                {
                    LogicServerListener.Instance.GetGameListener(avatar.AccountId).SendTCPMessage(new AllianceResponseMessage()
                    {
                        ResponseType = 102
                    });
                    MyAllianceMessage targetAlliance = new()
                    {
                        AllianceHeader = alliance.Header,
                        Role = avatar.AllianceRole
                    };
                    LogicServerListener.Instance.GetGameListener(avatar.AccountId).SendTCPMessage(targetAlliance);
                }
            }
        }

        private void AskForJoinableAllianceListReceived(AskForJoinableAllianceListMessage message)
        {
            JoinableAllianceListMessage list = new JoinableAllianceListMessage();
            List<Alliance> alliances = Alliances.GetRandomAlliances(HomeMode.Avatar, 20);
            foreach (Alliance alliance in alliances)
            {
                list.JoinableAlliances.Add(alliance.Header);
            }
            Connection.Send(list);
        }

        private void ClientCapabilitesReceived(ClientCapabilitiesMessage message)
        {
            Connection.PingUpdated(message.Ping);
            ShowLobbyInfo();
        }

        private void AskForBattleEndReceived(AskForBattleEndMessage message)
        {
            bool isPvP;
            BattlePlayer OwnPlayer = null;

            LocationData location = DataTables.Get(DataType.Location).GetDataWithId<LocationData>(message.LocationId);
            if (location == null || location.Disabled)
            {
                return;
            }
            if (DateTime.UtcNow > HomeMode.Home.PremiumEndTime && HomeMode.Avatar.PremiumLevel > 1)
            {
                HomeMode.Avatar.PremiumLevel = 0;
                HomeMode.Home.NotificationFactory.Add(new Notification
                {
                    Id = 81,
                    //TimePassed = 
                    MessageEntry = $"Привет!\n У тебя закончился твой vip статус\nпродлить его можно у одного из администраторов, тг: @nnsprkdv"
                });
            }

            isPvP = true;//Events.HasLocation(message.LocationId);

            for (int x = 0; x < message.BattlePlayersCount; x++)
            {
                BattlePlayer battlePlayer = message.BattlePlayers[x];
                if (battlePlayer.DisplayData.Name == HomeMode.Avatar.Name)
                {
                    battlePlayer.AccountId = HomeMode.Avatar.AccountId;
                    OwnPlayer = battlePlayer;

                    Hero hero = HomeMode.Avatar.GetHero(OwnPlayer.CharacterId);
                    if (hero == null)
                    {
                        return;
                    }
                    message.BattlePlayers[x].HeroPowerLevel = hero.PowerLevel + (hero.HasStarpower ? 1 : 0);
                    OwnPlayer.HeroPowerLevel = hero.PowerLevel + (hero.HasStarpower ? 1 : 0);
                    OwnPlayer.Trophies = hero.Trophies;
                    OwnPlayer.HighestTrophies = hero.HighestTrophies;
                    OwnPlayer.PowerPlayScore = HomeMode.Home.PowerPlayScore;

                    battlePlayer.DisplayData = new PlayerDisplayData(HomeMode.Home.HasPremiumPass, HomeMode.Home.ThumbnailId, HomeMode.Home.NameColorId, HomeMode.Avatar.Name);
                }
                else
                {
                    battlePlayer.DisplayData = new PlayerDisplayData(false, 28000000, 43000000, "Bot " + battlePlayer.DisplayData.Name);
                }
            }

            if (OwnPlayer == null)
            {
                return;
            }

            int StartExperience = HomeMode.Home.Experience;
            int[] ExperienceRewards = new[] { 8, 4, 6 };
            int[] TokensRewards = new[] { 14, 7, 10 };

            bool starToken = false;
            int gameMode = 0;
            int[] Trophies = new int[10];
            int trophiesResult = 0;
            int underdogTrophiesResult = 0;
            int experienceResult = 0;
            int totalTokensResult = 0;
            int tokensResult = 0;
            int doubledTokensResult = 0;
            int MilestoneReward = 0;
            int starExperienceResult = 0;
            List<int> MilestoneRewards = new List<int>();
            int powerPlayScoreGained = 0;
            int powerPlayEpicScoreGained = 0;
            bool isPowerPlay = false;
            bool HasNoTokens = false;
            List<Quest> q = new();

            if (isPvP)
            {
                Hero hero = HomeMode.Avatar.GetHero(OwnPlayer.CharacterId);
                if (hero == null)
                {
                    return;
                }
                int slot = Events.SlotsLocations[message.LocationId];

                int brawlerTrophies = hero.Trophies;
                if (slot == 9)
                {
                    if (HomeMode.Home.PowerPlayGamesPlayed < 3)
                    {
                        isPvP = false;
                        isPowerPlay = true;
                        int[] powerPlayAwards = { 30, 5, 15 };
                        powerPlayScoreGained = powerPlayAwards[message.BattleResult];
                        HomeMode.Home.PowerPlayTrophiesReward = powerPlayScoreGained;
                        HomeMode.Home.PowerPlayGamesPlayed++;
                        HomeMode.Home.PowerPlayScore += powerPlayScoreGained;

                        HomeMode.Avatar.TrioWins++;
                        if (location.GameMode == "CoinRush")
                        {
                            if (DateTime.UtcNow.Subtract(HomeMode.Avatar.BattleStartTime).TotalSeconds <= 90)
                            {
                                HomeMode.Home.PowerPlayTrophiesReward += 3;
                                HomeMode.Home.PowerPlayScore += 3;
                                powerPlayEpicScoreGained = 3;
                            }
                        }
                        else if (location.GameMode == "LaserBall")
                        {
                            if (DateTime.UtcNow.Subtract(HomeMode.Avatar.BattleStartTime).TotalSeconds <= 30)
                            {
                                HomeMode.Home.PowerPlayTrophiesReward += 3;
                                HomeMode.Home.PowerPlayScore += 3;
                                powerPlayEpicScoreGained = 3;
                            }
                        }
                        else if (location.GameMode == "AttackDefend")
                        {
                            if (DateTime.UtcNow.Subtract(HomeMode.Avatar.BattleStartTime).TotalSeconds <= 45)
                            {
                                HomeMode.Home.PowerPlayTrophiesReward += 3;
                                HomeMode.Home.PowerPlayScore += 3;
                                powerPlayEpicScoreGained = 3;
                            }
                        }
                        else if (location.GameMode == "RoboWars")
                        {
                            if (DateTime.UtcNow.Subtract(HomeMode.Avatar.BattleStartTime).TotalSeconds <= 45)
                            {
                                HomeMode.Home.PowerPlayTrophiesReward += 3;
                                HomeMode.Home.PowerPlayScore += 3;
                                powerPlayEpicScoreGained = 3;
                            }
                        }
                        if (HomeMode.Home.PowerPlayScore >= HomeMode.Home.PowerPlayHighestScore)
                        {
                            HomeMode.Home.PowerPlayHighestScore = HomeMode.Home.PowerPlayScore;
                        }
                        if (HomeMode.Home.Quests != null)
                        {
                            if (location.GameMode == "BountyHunter")
                            {
                                q = HomeMode.Home.Quests.UpdateQuestsProgress(3, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                            }
                            else if (location.GameMode == "CoinRush")
                            {
                                q = HomeMode.Home.Quests.UpdateQuestsProgress(0, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                            }
                            else if (location.GameMode == "AttackDefend")
                            {
                                q = HomeMode.Home.Quests.UpdateQuestsProgress(2, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                            }
                            else if (location.GameMode == "LaserBall")
                            {
                                q = HomeMode.Home.Quests.UpdateQuestsProgress(5, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                            }
                            else if (location.GameMode == "RoboWars")
                            {
                                q = HomeMode.Home.Quests.UpdateQuestsProgress(11, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                            }
                        }
                    }


                }
                else if (location.GameMode == "BountyHunter" || location.GameMode == "CoinRush" || location.GameMode == "AttackDefend" || location.GameMode == "LaserBall" || location.GameMode == "RoboWars" || location.GameMode == "KingOfHill")
                {
                    if (message.BattleResult == 0)
                    {
                        OwnPlayer.isStarplayer = true;
                        starExperienceResult = 4;
                        HomeMode.Home.Experience += starExperienceResult;
                        /*if (Events.PlaySlot(HomeMode.Avatar.AccountId, slot))
                        {
                            starToken = true;
                            HomeMode.Avatar.AddStarTokens(1);
                            HomeMode.Home.StarTokensReward = 1;
                        }*/
                    }
                    else
                    {
                        Random r = new();
                        message.BattlePlayers[r.Next(1, 5)].isStarplayer = true;
                    }
                    if (brawlerTrophies <= 49)
                    {
                        Trophies[0] = 8;
                        Trophies[1] = 0;
                    }
                    else if (50 <= brawlerTrophies && brawlerTrophies <= 99)
                    {
                        Trophies[0] = 8;
                        Trophies[1] = -1;
                    }
                    else if (100 <= brawlerTrophies && brawlerTrophies <= 199)
                    {
                        Trophies[0] = 8;
                        Trophies[1] = -2;
                    }
                    else if (200 <= brawlerTrophies && brawlerTrophies <= 299)
                    {
                        Trophies[0] = 8;
                        Trophies[1] = -3;
                    }
                    else if (300 <= brawlerTrophies && brawlerTrophies <= 399)
                    {
                        Trophies[0] = 8;
                        Trophies[1] = -4;
                    }
                    else if (400 <= brawlerTrophies && brawlerTrophies <= 499)
                    {
                        Trophies[0] = 8;
                        Trophies[1] = -5;
                    }
                    else if (500 <= brawlerTrophies && brawlerTrophies <= 599)
                    {
                        Trophies[0] = 8;
                        Trophies[1] = -6;
                    }
                    else if (600 <= brawlerTrophies && brawlerTrophies <= 699)
                    {
                        Trophies[0] = 8;
                        Trophies[1] = -7;
                    }
                    else if (700 <= brawlerTrophies && brawlerTrophies <= 799)
                    {
                        Trophies[0] = 8;
                        Trophies[1] = -8;
                    }
                    else if (800 <= brawlerTrophies && brawlerTrophies <= 899)
                    {
                        Trophies[0] = 7;
                        Trophies[1] = -9;
                    }
                    else if (900 <= brawlerTrophies && brawlerTrophies <= 999)
                    {
                        Trophies[0] = 6;
                        Trophies[1] = -10;
                    }
                    else if (1000 <= brawlerTrophies && brawlerTrophies <= 1099)
                    {
                        Trophies[0] = 5;
                        Trophies[1] = -11;
                    }
                    else if (1100 <= brawlerTrophies && brawlerTrophies <= 1199)
                    {
                        Trophies[0] = 4;
                        Trophies[1] = -12;
                    }
                    else if (brawlerTrophies >= 1200)
                    {
                        Trophies[0] = 3;
                        Trophies[1] = -12;
                    }

                    gameMode = 1;
                    trophiesResult = Trophies[message.BattleResult];
                    HomeMode.Home.TrophiesReward = Math.Max(trophiesResult, 0);

                    if (message.BattleResult == 0) // Win
                    {
                        HomeMode.Avatar.TrioWins++;
                        if (location.GameMode == "CoinRush")
                        {
                            Console.WriteLine(DateTime.UtcNow.Subtract(HomeMode.Avatar.BattleStartTime).TotalSeconds);
                            if (DateTime.UtcNow.Subtract(HomeMode.Avatar.BattleStartTime).TotalSeconds <= 90)
                            {
                                underdogTrophiesResult += (int)Math.Round((double)Trophies[message.BattleResult] / 4);
                                trophiesResult += underdogTrophiesResult;
                                HomeMode.Home.TrophiesReward = Math.Max(trophiesResult, 0);
                            }
                        }
                        else if (location.GameMode == "LaserBall")
                        {
                            Console.WriteLine(DateTime.UtcNow.Subtract(HomeMode.Avatar.BattleStartTime).TotalSeconds);
                            if (DateTime.UtcNow.Subtract(HomeMode.Avatar.BattleStartTime).TotalSeconds <= 30)
                            {
                                underdogTrophiesResult += (int)Math.Round((double)Trophies[message.BattleResult] / 4);
                                trophiesResult += underdogTrophiesResult;
                                HomeMode.Home.TrophiesReward = Math.Max(trophiesResult, 0);
                            }
                        }

                        if (HomeMode.Home.Quests != null)
                        {
                            if (location.GameMode == "BountyHunter")
                            {
                                q = HomeMode.Home.Quests.UpdateQuestsProgress(3, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                            }
                            else if (location.GameMode == "CoinRush")
                            {
                                q = HomeMode.Home.Quests.UpdateQuestsProgress(0, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                            }
                            else if (location.GameMode == "AttackDefend")
                            {
                                q = HomeMode.Home.Quests.UpdateQuestsProgress(2, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                            }
                            else if (location.GameMode == "LaserBall")
                            {
                                q = HomeMode.Home.Quests.UpdateQuestsProgress(5, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                            }
                            else if (location.GameMode == "RoboWars")
                            {
                                q = HomeMode.Home.Quests.UpdateQuestsProgress(11, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                            }
                        }

                    }

                    tokensResult = TokensRewards[message.BattleResult];
                    totalTokensResult = tokensResult;

                    experienceResult = ExperienceRewards[message.BattleResult];
                    HomeMode.Home.Experience += experienceResult;
                }
                else if (location.GameMode == "BattleRoyale")
                {
                    if (message.Rank < 5)
                    {
                        /*if (Events.PlaySlot(HomeMode.Avatar.AccountId, slot))
                        {
                            starToken = true;
                            HomeMode.Avatar.AddStarTokens(1);
                            HomeMode.Home.StarTokensReward = 1;
                        }*/
                    }
                    if (brawlerTrophies >= 0 && brawlerTrophies <= 49)
                    {
                        Trophies = new[] { 10, 8, 7, 6, 4, 2, 2, 1, 0, 0 };
                    }
                    else if (brawlerTrophies >= 50 && brawlerTrophies <= 99)
                    {
                        Trophies = new[] { 10, 8, 7, 6, 3, 2, 2, 0, -1, -2 };
                    }
                    else if (brawlerTrophies >= 100 && brawlerTrophies <= 199)
                    {
                        Trophies = new[] { 10, 8, 7, 6, 3, 1, 0, -1, -2, -2 };
                    }
                    else if (brawlerTrophies >= 200 && brawlerTrophies <= 299)
                    {
                        Trophies = new[] { 10, 8, 6, 5, 3, 1, 0, -2, -3, -3 };
                    }
                    else if (brawlerTrophies >= 300 && brawlerTrophies <= 399)
                    {
                        Trophies = new[] { 10, 8, 6, 5, 2, 0, 0, -3, -4, -4 };
                    }
                    else if (brawlerTrophies >= 400 && brawlerTrophies <= 499)
                    {
                        Trophies = new[] { 10, 8, 6, 5, 2, -1, -2, -3, -5, -5 };
                    }
                    else if (brawlerTrophies >= 500 && brawlerTrophies <= 599)
                    {
                        Trophies = new[] { 10, 8, 6, 4, 2, -1, -2, -5, -6, -6 };
                    }
                    else if (brawlerTrophies >= 600 && brawlerTrophies <= 699)
                    {
                        Trophies = new[] { 10, 8, 6, 4, 1, -2, -2, -5, -7, -8 };
                    }
                    else if (brawlerTrophies >= 700 && brawlerTrophies <= 799)
                    {
                        Trophies = new[] { 10, 8, 6, 4, 1, -3, -4, -5, -8, -9 };
                    }
                    else if (brawlerTrophies >= 800 && brawlerTrophies <= 899)
                    {
                        Trophies = new[] { 9, 7, 5, 2, 0, -3, -4, -7, -9, -10 };
                    }
                    else if (brawlerTrophies >= 900 && brawlerTrophies <= 999)
                    {
                        Trophies = new[] { 8, 6, 4, 1, -1, -3, -6, -8, -10, -11 };
                    }
                    else if (brawlerTrophies >= 1000 && brawlerTrophies <= 1099)
                    {
                        Trophies = new[] { 6, 5, 3, 1, -2, -5, -6, -9, -11, -12 };
                    }
                    else if (brawlerTrophies >= 1100 && brawlerTrophies <= 1199)
                    {
                        Trophies = new[] { 5, 4, 1, 0, -2, -6, -7, -10, -12, -13 };
                    }
                    else if (brawlerTrophies >= 1200)
                    {
                        Trophies = new[] { 5, 3, 0, -1, -2, -6, -8, -11, -12, -13 };
                    }

                    gameMode = 2;
                    trophiesResult = Trophies[message.Rank - 1];

                    ExperienceRewards = new[] { 15, 12, 9, 6, 5, 4, 3, 2, 1, 0 };
                    TokensRewards = new[] { 30, 24, 21, 15, 12, 8, 6, 4, 2, 0 };



                    HomeMode.Home.TrophiesReward = Math.Max(trophiesResult, 0);

                    if (message.Rank == 1) // Win
                    {
                        HomeMode.Avatar.SoloWins++;
                    }
                    if (message.Rank < 5 && HomeMode.Home.Quests != null)
                        q = HomeMode.Home.Quests.UpdateQuestsProgress(6, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                    tokensResult = TokensRewards[message.Rank - 1];
                    totalTokensResult = tokensResult;

                    experienceResult = ExperienceRewards[message.Rank - 1];
                    HomeMode.Home.Experience += experienceResult;
                }
                else if (location.GameMode == "BattleRoyaleTeam")
                {
                    if (message.Rank < 3)
                    {
                        /*if (Events.PlaySlot(HomeMode.Avatar.AccountId, slot))
                        {
                            starToken = true;
                            HomeMode.Avatar.AddStarTokens(1);
                            HomeMode.Home.StarTokensReward = 1;
                        }*/
                    }
                    if (brawlerTrophies >= 0 && brawlerTrophies <= 49)
                    {
                        Trophies[0] = 9;
                        Trophies[1] = 7;
                        Trophies[2] = 4;
                        Trophies[3] = 0;
                        Trophies[4] = 0;
                    }
                    else if (brawlerTrophies <= 999)
                    {
                        Trophies[0] = 9;
                        Trophies[1] = 7;
                        int rankDiff = (brawlerTrophies - 100) / 100;
                        Trophies[2] = Math.Max(3 - rankDiff, 0);
                        Trophies[3] = Math.Max(-1 - rankDiff, -3);
                        Trophies[4] = Math.Max(-2 - rankDiff, -4);
                    }
                    else if (brawlerTrophies <= 1099)
                    {
                        Trophies[0] = 5;
                        Trophies[1] = 4;
                        int rankDiff = (brawlerTrophies - 1000) / 100;
                        Trophies[2] = Math.Max(-4 - rankDiff, -6);
                        Trophies[3] = Math.Max(-9 - rankDiff, -10);
                        Trophies[4] = Math.Max(-11 - rankDiff, -12);
                    }
                    else
                    {
                        Trophies[0] = 4;
                        Trophies[1] = 2;
                        Trophies[2] = -6;
                        Trophies[3] = -10;
                        Trophies[4] = -12;
                    }

                    gameMode = 5;
                    trophiesResult = Trophies[message.Rank - 1];

                    ExperienceRewards = new[] { 14, 8, 4, 2, 0 };
                    TokensRewards = new[] { 32, 20, 8, 4, 0 };

                    HomeMode.Home.TrophiesReward = Math.Max(trophiesResult, 0);

                    if (message.Rank < 3) // Win
                    {
                        HomeMode.Avatar.DuoWins++;
                    }
                    if (message.Rank < 3 && HomeMode.Home.Quests != null)
                        q = HomeMode.Home.Quests.UpdateQuestsProgress(9, OwnPlayer.CharacterId, 0, 0, 0, HomeMode.Home);
                    tokensResult = TokensRewards[message.Rank - 1];
                    totalTokensResult = tokensResult;

                    experienceResult = ExperienceRewards[message.Rank - 1];
                    HomeMode.Home.Experience += experienceResult;
                }

                else if (location.GameMode == "BossFight")
                {
                    gameMode = 4;
                }
                else if (location.GameMode == "Raid_TownCrush")
                {
                    isPvP = false;
                    Console.WriteLine(message.BattleResult);
                    message.BattleResult = 0;
                    gameMode = 6;
                }
                else if (location.GameMode == "Raid")
                {
                    isPvP = false;
                    message.BattleResult = 0;
                    gameMode = 6;
                }

                if (HomeMode.Avatar.PremiumLevel > 0)
                {
                    switch (HomeMode.Avatar.PremiumLevel)
                    {
                        case 1:
                            if (location.GameMode == "BountyHunter" || location.GameMode == "CoinRush" || location.GameMode == "AttackDefend" || location.GameMode == "LaserBall" || location.GameMode == "RoboWars" || location.GameMode == "KingOfHill")
                            {
                                underdogTrophiesResult += (int)Math.Floor((double)Trophies[0] / 2);
                                trophiesResult += (int)Math.Floor((double)Trophies[0] / 2);
                            }
                            else if (location.GameMode == "BattleRoyale" || location.GameMode == "BattleRoyaleTeam")
                            {
                                underdogTrophiesResult += (int)Math.Floor((double)Math.Abs(Trophies[message.Rank - 1]) / 2);
                                trophiesResult += (int)Math.Floor((double)Math.Abs(Trophies[message.Rank - 1]) / 2);
                            }
                            break;
                        case 3:
                            if (location.GameMode == "BountyHunter" || location.GameMode == "CoinRush" || location.GameMode == "AttackDefend" || location.GameMode == "LaserBall" || location.GameMode == "RoboWars" || location.GameMode == "KingOfHill")
                            {
                                underdogTrophiesResult += (int)(Math.Floor((double)Trophies[0] * 2 * 1.5));
                                trophiesResult += (int)(Math.Floor((double)Trophies[0] * 2 * 1.5));
                            }
                            else if (location.GameMode == "BattleRoyale" || location.GameMode == "BattleRoyaleTeam")
                            {
                                underdogTrophiesResult += (int)(Math.Floor((double)Math.Abs(Trophies[message.Rank - 1]) * 2 * 1.5));
                                trophiesResult += (int)(Math.Floor((double)Math.Abs(Trophies[message.Rank - 1]) * 2 * 1.5));
                            }
                            break;
                        case 2:
                            if (location.GameMode == "BountyHunter" || location.GameMode == "CoinRush" || location.GameMode == "AttackDefend" || location.GameMode == "LaserBall" || location.GameMode == "RoboWars" || location.GameMode == "KingOfHill")
                            {
                                underdogTrophiesResult += (int)(Math.Floor((double)Trophies[0] / 2) + (Math.Round((double)Trophies[0] / 4)));
                                trophiesResult += (int)(Math.Floor((double)Trophies[0] / 2) + (Math.Round((double)Trophies[0] / 4)));
                            }
                            else if (location.GameMode == "BattleRoyale" || location.GameMode == "BattleRoyaleTeam")
                            {
                                underdogTrophiesResult += (int)(Math.Floor((double)Math.Abs(Trophies[message.Rank - 1]) / 2) + (Math.Round((double)Math.Abs(Trophies[message.Rank - 1]) / 4)));
                                trophiesResult += (int)(Math.Floor((double)Math.Abs(Trophies[message.Rank - 1]) / 2) + (Math.Round((double)Math.Abs(Trophies[message.Rank - 1]) / 4)));
                            }
                            break;
                    }
                    HomeMode.Home.TrophiesReward = Math.Max(trophiesResult, 0);
                }

                if (HomeMode.Home.BattleTokens > 0)
                {
                    if (!(HomeMode.Home.BattleTokens - tokensResult >= 0))
                    {
                        tokensResult = HomeMode.Home.BattleTokens;
                        totalTokensResult += tokensResult;
                        HomeMode.Home.BattleTokens = 0;
                    }
                    else
                    {
                        HomeMode.Home.BattleTokens -= tokensResult;
                    }
                    if (HomeMode.Home.BattleTokensRefreshStart == new DateTime())
                    {
                        HomeMode.Home.BattleTokensRefreshStart = DateTime.UtcNow;
                    }
                }
                else
                {
                    tokensResult = 0;
                    totalTokensResult = 0;
                    HasNoTokens = true;
                }
                int starteh = HomeMode.Home.Experience;
                HomeMode.Home.Experience += experienceResult;
                HomeMode.Home.Experience += starExperienceResult;
                int endeh = HomeMode.Home.Experience;

                for (int i = 34; i < 500; i++)
                {
                    MilestoneData m = DataTables.Get(DataType.Milestone).GetDataByGlobalId<MilestoneData>(GlobalId.CreateGlobalId(39, i));
                    int trr = m.ProgressStart + m.Progress;
                    if (starteh < trr && endeh >= trr)
                    {
                        MilestoneReward = GlobalId.CreateGlobalId(39, i);
                        MilestoneRewards.Add(MilestoneReward);
                        HomeMode.Avatar.StarPoints += m.SecondaryLvlUpRewardCount;
                        HomeMode.Home.StarPointsGained += m.SecondaryLvlUpRewardCount;
                        totalTokensResult += m.PrimaryLvlUpRewardCount;
                        break;
                    }
                }

                int starth = hero.HighestTrophies;
                HomeMode.Avatar.AddTrophies(trophiesResult);
                hero.AddTrophies(trophiesResult);
                int endh = hero.HighestTrophies;
                for (int i = 0; i < 34; i++)
                {
                    MilestoneData m = DataTables.Get(DataType.Milestone).GetDataByGlobalId<MilestoneData>(GlobalId.CreateGlobalId(39, i));
                    int trr = m.ProgressStart + m.Progress;
                    if (starth < trr && endh >= trr)
                    {
                        MilestoneReward = GlobalId.CreateGlobalId(39, i);
                        MilestoneRewards.Add(MilestoneReward);
                        HomeMode.Avatar.StarPoints += m.SecondaryLvlUpRewardCount;
                        HomeMode.Home.StarPointsGained += m.SecondaryLvlUpRewardCount;
                        totalTokensResult += m.PrimaryLvlUpRewardCount;
                        break;
                    }
                }


                if (HomeMode.Home.TokenDoublers > 0)
                {
                    doubledTokensResult = Math.Min(totalTokensResult, HomeMode.Home.TokenDoublers);
                    HomeMode.Home.TokenDoublers -= doubledTokensResult;
                    totalTokensResult += doubledTokensResult;
                }
                HomeMode.Home.BrawlPassTokens += totalTokensResult;
                HomeMode.Home.TokenReward += totalTokensResult;
            }
            else
            {
                if (location.GameMode == "BountyHunter" || location.GameMode == "CoinRush" || location.GameMode == "AttackDefend" || location.GameMode == "LaserBall" || location.GameMode == "RoboWars")
                {
                    gameMode = 1;
                }
                else if (location.GameMode == "BattleRoyale")
                {
                    gameMode = 2;
                }
                else if (location.GameMode == "BattleRoyaleTeam")
                {
                    gameMode = 5;
                }
                else if (location.GameMode == "BossFight")
                {
                    gameMode = 4;
                }

            }
            //string r = "";
            string[] d = { "win", "lose", "draw" };
            if (location.GameMode.StartsWith("BattleRoyale"))
            {
                Logger.BLog($"Player {LogicLongCodeGenerator.ToCode(HomeMode.Avatar.AccountId)} ended battle! Battle Rank: {message.BattleResult} in {DateTime.UtcNow.Subtract(HomeMode.Avatar.BattleStartTime).TotalSeconds}s gamemode: {location.GameMode}!");
            }
            else
            {
                Logger.BLog($"Player {LogicLongCodeGenerator.ToCode(HomeMode.Avatar.AccountId)} ended battle! Battle Result: {d[message.BattleResult]} in {DateTime.UtcNow.Subtract(HomeMode.Avatar.BattleStartTime).TotalSeconds}s gamemode: {location.GameMode}!");
            }
            HomeMode.Avatar.BattleStartTime = new();

            BattleEndMessage battleend = new()
            {
                GameMode = gameMode,
                Result = message.BattleResult,
                StarToken = starToken,
                IsPowerPlay = isPowerPlay,
                IsPvP = isPvP,
                pp = message.BattlePlayers,
                OwnPlayer = OwnPlayer,
                TrophiesReward = trophiesResult,
                ExperienceReward = experienceResult,
                StarExperienceReward = starExperienceResult,
                DoubledTokensReward = doubledTokensResult,
                TokenDoublersLeft = HomeMode.Home.TokenDoublers,
                TokensReward = tokensResult,
                Experience = StartExperience,
                MilestoneReward = MilestoneReward,
                ProgressiveQuests = q,
                UnderdogTrophies = underdogTrophiesResult,
                PowerPlayScoreGained = powerPlayScoreGained,
                PowerPlayEpicScoreGained = powerPlayEpicScoreGained,
                HasNoTokens = HasNoTokens,
                MilestoneRewards = MilestoneRewards,
            };

            Connection.Send(battleend);
        }

        private void GetLeaderboardReceived(GetLeaderboardMessage message)
        {
            if (message.LeaderboardType == 1)
            {
                Account[] rankingList = Leaderboards.GetAvatarRankingList();

                LeaderboardMessage leaderboard = new()
                {
                    LeaderboardType = 1,
                    Region = message.IsRegional ? "RU" : null
                };
                foreach (Account data in rankingList)
                {
                    leaderboard.Avatars.Add(new KeyValuePair<ClientHome, ClientAvatar>(data.Home, data.Avatar));
                }
                leaderboard.OwnAvatarId = Connection.Avatar.AccountId;

                Connection.Send(leaderboard);
            }
            else if (message.LeaderboardType == 2)
            {
                Alliance[] rankingList = Leaderboards.GetAllianceRankingList();

                LeaderboardMessage leaderboard = new()
                {
                    LeaderboardType = 2,
                    Region = message.IsRegional ? "RU" : null
                };
                leaderboard.AllianceList.AddRange(rankingList);

                Connection.Send(leaderboard);
            }
            else if (message.LeaderboardType == 0)
            {
                Dictionary<int, List<Account>> rankingList = Leaderboards.GetBrawlersRankingList();

                LeaderboardMessage leaderboard = new()
                {
                    LeaderboardType = 0,
                    Region = message.IsRegional ? "RU" : null,
                };
                Dictionary<ClientHome, ClientAvatar> aaaa = new();
                foreach (KeyValuePair<int, List<Account>> data in rankingList)
                {
                    if (data.Key == message.CharachterId)
                    {
                        foreach (Account account in data.Value)
                        {
                            aaaa.Add(account.Home, account.Avatar);
                        }

                    }
                }

                leaderboard.CharachterId = message.CharachterId;
                aaaa = aaaa.OrderBy(x => x.Value.GetHero(message.CharachterId).Trophies).Reverse().ToDictionary(x => x.Key, x => x.Value);
                aaaa = aaaa.Take(Math.Min(aaaa.Count, 200)).ToDictionary(kvp => kvp.Key, kvp => kvp.Value);
                leaderboard.Brawlers = aaaa;
                leaderboard.OwnAvatarId = Connection.Avatar.AccountId;
                Connection.Send(leaderboard);
            }
            else if (message.LeaderboardType == 3)
            {
                Account[] rankingList = Leaderboards.GetAvatarRankingList();

                LeaderboardMessage leaderboard = new()
                {
                    LeaderboardType = 3,
                    Region = message.IsRegional ? "RU" : null
                };
                foreach (Account data in rankingList)
                {
                    leaderboard.Avatars.Add(new KeyValuePair<ClientHome, ClientAvatar>(data.Home, data.Avatar));
                }
                leaderboard.OwnAvatarId = Connection.Avatar.AccountId;

                Connection.Send(leaderboard);
            }
        }

        private void GoHomeReceived(GoHomeMessage message)
        {
            if (Connection.Home != null && Connection.Avatar != null)
            {
                Connection.Home.Events = Events.GetEventsById(HomeMode.Home.PowerPlayGamesPlayed, Connection.Avatar.AccountId);
                OwnHomeDataMessage ohd = new OwnHomeDataMessage();
                ohd.Home = Connection.Home;
                ohd.Avatar = Connection.Avatar;
                Connection.Send(ohd);
                ShowLobbyInfo();
            }
        }

        private void ClientInfoReceived(ClientInfoMessage message)
        {
            UdpConnectionInfoMessage info = new UdpConnectionInfoMessage();
            info.SessionId = Connection.UdpSessionId;
            info.ServerAddress = Configuration.Instance.UdpHost;
            info.ServerPort = Configuration.Instance.UdpPort;
            Connection.Send(info);
        }

        private void CancelMatchMaking(CancelMatchmakingMessage message)
        {
            Matchmaking.CancelMatchmake(Connection);
            Connection.Send(new MatchMakingCancelledMessage());
        }

        private void MatchmakeRequestReceived(MatchmakeRequestMessage message)
        {
            int slot = message.EventSlot;

            if (HomeMode.Home.Character.Disabled)
            {
                Connection.Send(new OutOfSyncMessage());
                return;
            }

            if (!Events.HasSlot(slot))
            {
                slot = 1;
            }

            Matchmaking.RequestMatchmake(Connection, slot);
        }

        private void EndClientTurnReceived(EndClientTurnMessage message)
        {
            foreach (Command command in message.Commands)
            {
                if (!CommandManager.ReceiveCommand(command))
                {
                    OutOfSyncMessage outOfSync = new();
                    Connection.Send(outOfSync);
                }
            }
            HomeMode.ClientTurnReceived(message.Tick, message.Checksum, message.Commands);
        }

        private void GetPlayerProfile(GetPlayerProfileMessage message)
        {
            if (message.AccountId == 0)
            {
                Profile p = Profile.CreateConsole();
                PlayerProfileMessage a = new PlayerProfileMessage();
                a.Profile = p;
                
                Connection.Send(a);
                return;
            }
            Account data = Accounts.Load(message.AccountId);
            if (data == null) return;

            Profile profile = Profile.Create(data.Home, data.Avatar);

            PlayerProfileMessage profileMessage = new PlayerProfileMessage();
            profileMessage.Profile = profile;
            if (data.Avatar.AllianceId >= 0)
            {
                Alliance alliance = Alliances.Load(data.Avatar.AllianceId);
                if (alliance != null)
                {
                    profileMessage.AllianceHeader = alliance.Header;
                    profileMessage.AllianceRole = data.Avatar.AllianceRole;
                }
            }
            Connection.Send(profileMessage);
        }

        private void ChangeName(ChangeAvatarNameMessage message)
        {
            LogicChangeAvatarNameCommand command = new()
            {
                Name = message.Name,
                ChangeNameCost = 0
            };
            if (HomeMode.Avatar.AllianceId >= 0)
            {
                Alliance a = Alliances.Load(HomeMode.Avatar.AllianceId);
                if (a == null) return;
                AllianceMember m = a.GetMemberById(HomeMode.Avatar.AccountId);
                m.DisplayData.Name = message.Name;
            }
            command.Execute(HomeMode);
            AvailableServerCommandMessage serverCommandMessage = new()
            {
                Command = command
            };
            Connection.Send(serverCommandMessage);
        }

        private void OnChangeCharacter(int characterId)
        {
            TeamEntry team = Teams.Get(HomeMode.Avatar.TeamId);
            if (team == null) return;

            TeamMember member = team.GetMember(HomeMode.Avatar.AccountId);
            if (member == null) return;

            Hero hero = HomeMode.Avatar.GetHero(characterId);
            if (hero == null) return;
            member.CharacterId = characterId;
            member.HeroTrophies = hero.Trophies;
            member.HeroHighestTrophies = hero.HighestTrophies;
            member.HeroLevel = hero.PowerLevel;

            team.TeamUpdated();
        }

        private void LoginReceived(AuthenticationMessage message)
        {
            Account account = null;

            if (message.AccountId == 0)
            {
                account = Accounts.Create();
            }
            else
            {
                account = Accounts.Load(message.AccountId);
                if (account.PassToken != message.PassToken)
                {
                    account = null;
                }
            }

            if (account == null)
            {
                AuthenticationFailedMessage loginFailed = new AuthenticationFailedMessage();
                loginFailed.ErrorCode = 1;
                loginFailed.Message = "Unknown Error occured while loading account";
                Connection.Send(loginFailed);

                return;
            }

            if (account.Avatar.Banned)
            {
                AuthenticationFailedMessage loginFailed = new AuthenticationFailedMessage();
                loginFailed.ErrorCode = 11;
                Connection.Send(loginFailed);
                return;
            }
            AuthenticationOkMessage loginOk = new AuthenticationOkMessage();

            if (!account.Avatar.ShouldRedirect)
            {
                loginOk.AccountId = account.AccountId;
                loginOk.PassToken = account.PassToken;
                loginOk.ServerEnvironment = "dev";
            }
            else
            {
                //account.Avatar.ShouldRedirect = false;
                Account t = Accounts.Load(account.Avatar.RedirectId);
                account = t;
                loginOk.AccountId = t.AccountId;
                loginOk.PassToken = t.PassToken;
                loginOk.ServerEnvironment = "dev";
            }

            Connection.Send(loginOk);

            HomeMode = HomeMode.LoadHomeState(new HomeGameListener(Connection), account.Home, account.Avatar, Events.GetEventsById(account.Home.PowerPlayGamesPlayed, account.Avatar.AccountId));
            HomeMode.CharacterChanged += OnChangeCharacter;
            HomeMode.Home.IpAddress = Connection.Socket.RemoteEndPoint.ToString().Split(" ")[0];
            HomeMode.Home.Device = message.DeviceId;
            if (HomeMode.Avatar.HighestTrophies == 0 && HomeMode.Avatar.Trophies != 0)
            {
                HomeMode.Avatar.HighestTrophies = HomeMode.Avatar.Trophies;
            }
            CommandManager = new(HomeMode, Connection);

            if (HomeMode.Avatar.BattleStartTime != new DateTime())
            {
                Hero h = HomeMode.Avatar.GetHero(HomeMode.Home.CharacterId);
                int lose = 0;
                int brawlerTrophies = h.Trophies;
                if (brawlerTrophies <= 49)
                {
                    lose = 0;
                }
                else if (50 <= brawlerTrophies && brawlerTrophies <= 99)
                {
                    lose = -1;
                }
                else if (100 <= brawlerTrophies && brawlerTrophies <= 199)
                {
                    lose = -2;
                }
                else if (200 <= brawlerTrophies && brawlerTrophies <= 299)
                {
                    lose = -3;
                }
                else if (300 <= brawlerTrophies && brawlerTrophies <= 399)
                {
                    lose = -4;
                }
                else if (400 <= brawlerTrophies && brawlerTrophies <= 499)
                {
                    lose = -5;
                }
                else if (500 <= brawlerTrophies && brawlerTrophies <= 599)
                {
                    lose = -6;
                }
                else if (600 <= brawlerTrophies && brawlerTrophies <= 699)
                {
                    lose = -7;
                }
                else if (700 <= brawlerTrophies && brawlerTrophies <= 799)
                {
                    lose = -8;
                }
                else if (800 <= brawlerTrophies && brawlerTrophies <= 899)
                {
                    lose = -9;
                }
                else if (900 <= brawlerTrophies && brawlerTrophies <= 999)
                {
                    lose = -10;
                }
                else if (1000 <= brawlerTrophies && brawlerTrophies <= 1099)
                {
                    lose = -11;
                }
                else if (1100 <= brawlerTrophies && brawlerTrophies <= 1199)
                {
                    lose = -12;
                }
                else if (brawlerTrophies >= 1200)
                {
                    lose = -12;
                }
                h.AddTrophies(lose);
                HomeMode.Home.PowerPlayGamesPlayed = Math.Max(0, HomeMode.Home.PowerPlayGamesPlayed - 1);
                Connection.Home.Events = Events.GetEventsById(HomeMode.Home.PowerPlayGamesPlayed, Connection.Avatar.AccountId);
                HomeMode.Avatar.BattleStartTime = new DateTime();
            }

            BattleMode battle = null;
            if (HomeMode.Avatar.BattleId > 0)
            {
                battle = Battles.Get(HomeMode.Avatar.BattleId);
            }

            if (battle == null)
            {
                OwnHomeDataMessage ohd = new OwnHomeDataMessage();
                ohd.Home = HomeMode.Home;
                ohd.Avatar = HomeMode.Avatar;
                Connection.Send(ohd);
            }
            else
            {
                StartLoadingMessage startLoading = new StartLoadingMessage();
                startLoading.LocationId = battle.Location.GetGlobalId();
                startLoading.TeamIndex = HomeMode.Avatar.TeamIndex;
                startLoading.OwnIndex = HomeMode.Avatar.OwnIndex;
                startLoading.GameMode = battle.GetGameModeVariation() == 6 ? 6 : 1;
                startLoading.Players.AddRange(battle.GetPlayers());
                UDPSocket socket = UDPGateway.CreateSocket();
                socket.TCPConnection = Connection;
                socket.Battle = battle;
                Connection.UdpSessionId = socket.SessionId;
                battle.ChangePlayerSessionId(HomeMode.Avatar.UdpSessionId, socket.SessionId);
                HomeMode.Avatar.UdpSessionId = socket.SessionId;
                Connection.Send(startLoading);
            }

            Connection.Avatar.LastOnline = DateTime.UtcNow;

            Sessions.Create(HomeMode, Connection);
            if (true)
            {
                FriendListMessage friendList = new FriendListMessage();
                friendList.Friends = HomeMode.Avatar.Friends.ToArray();
                Connection.Send(friendList);



                if (HomeMode.Avatar.AllianceRole != AllianceRole.None && HomeMode.Avatar.AllianceId > 0)
                {
                    Alliance alliance = Alliances.Load(HomeMode.Avatar.AllianceId);

                    if (alliance != null)
                    {
                        SendMyAllianceData(alliance);
                        AllianceDataMessage data = new AllianceDataMessage();
                        data.Alliance = alliance;
                        data.IsMyAlliance = true;
                        Connection.Send(data);
                    }
                }

                foreach (Friend entry in HomeMode.Avatar.Friends.ToArray())
                {
                    if (LogicServerListener.Instance.IsPlayerOnline(entry.AccountId))
                    {
                        FriendOnlineStatusEntryMessage statusEntryMessage = new FriendOnlineStatusEntryMessage();
                        statusEntryMessage.AvatarId = entry.AccountId;
                        statusEntryMessage.PlayerStatus = entry.Avatar.PlayerStatus;
                        Connection.Send(statusEntryMessage);
                    }
                }

                if (HomeMode.Avatar.TeamId > 0)
                {
                    TeamMessage teamMessage = new TeamMessage();
                    teamMessage.Team = Teams.Get(HomeMode.Avatar.TeamId);
                    if (teamMessage.Team != null)
                    {
                        Connection.Send(teamMessage);
                        TeamMember member = teamMessage.Team.GetMember(HomeMode.Avatar.AccountId);
                        member.State = 0;
                        teamMessage.Team.TeamUpdated();
                    }
                }
            }
            //Connection.Send(new StartLatencyTestRequestMessage());
        }

        private void ClientHelloReceived(ClientHelloMessage message)
        {
            if (message.KeyVersion != PepperKey.VERSION)
            {
                //return;
            }

            Connection.Messaging.Seed = message.ClientSeed;
            Random r = new();

            Connection.Messaging.serversc = (byte)r.Next(1, 256);
            ServerHelloMessage hello = new ServerHelloMessage();
            hello.serversc = Connection.Messaging.serversc;
            hello.SetServerHelloToken(Connection.Messaging.SessionToken);
            Connection.Send(hello);
        }
    }
}
