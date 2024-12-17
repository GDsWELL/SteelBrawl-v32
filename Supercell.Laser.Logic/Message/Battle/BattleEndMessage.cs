namespace Supercell.Laser.Logic.Message.Battle
{
    using Supercell.Laser.Logic.Battle.Structures;
    using Supercell.Laser.Logic.Helper;
    using Supercell.Laser.Logic.Home.Quest;

    public class BattleEndMessage : GameMessage
    {
        public BattleEndMessage() : base()
        {
            ProgressiveQuests = new List<Quest>();
        }

        public int Result;
        public int TokensReward;
        public int TrophiesReward;
        public int DoubledTokensReward;
        public int TokenDoublersLeft;
        public int ExperienceReward;
        public int Experience;
        public int MilestoneReward;
        public int StarExperienceReward;
        public List<BattlePlayer> Players;
        public BattlePlayer[] pp;
        public List<Quest> ProgressiveQuests;
        public BattlePlayer OwnPlayer;
        public bool StarToken;
        public int UnderdogTrophies;
        public int PowerPlayScoreGained;
        public int PowerPlayEpicScoreGained;
        public List<int> MilestoneRewards;

        public int GameMode;

        public bool HasNoTokens;
        public bool IsPvP;
        public bool IsPowerPlay;

        public override void Encode()
        {
            Stream.WriteVInt(GameMode); // game mode
            Stream.WriteVInt(Result);

            Stream.WriteVInt(TokensReward); // tokens reward
            Stream.WriteVInt(TrophiesReward); // trophies reward
            Stream.WriteVInt(PowerPlayScoreGained);
            Stream.WriteVInt(DoubledTokensReward);
            Stream.WriteVInt(0);
            Stream.WriteVInt(TokenDoublersLeft);
            Stream.WriteVInt(0);
            Stream.WriteVInt(PowerPlayEpicScoreGained);
            Stream.WriteVInt(0);
            Stream.WriteVInt(0);
            Stream.WriteVInt(0);
            Stream.WriteVInt(0);
            Stream.WriteVInt(0);
            Stream.WriteVInt(0);
            Stream.WriteVInt(UnderdogTrophies);

            Stream.WriteBoolean(false);
            Stream.WriteBoolean(false); // no experience
            Stream.WriteBoolean(HasNoTokens); // no tokens left
            Stream.WriteBoolean(false);
            Stream.WriteBoolean(IsPvP); // is PvP
            Stream.WriteBoolean(false);
            Stream.WriteBoolean(IsPowerPlay);

            Stream.WriteVInt(-1);
            Stream.WriteBoolean(false);

            Stream.WriteVInt(pp.Length);
            foreach (BattlePlayer player in pp)
            {
                Stream.WriteBoolean(player.AccountId == OwnPlayer.AccountId); // is own player
                Stream.WriteBoolean(player.TeamIndex != OwnPlayer.TeamIndex); // is enemy
                Stream.WriteBoolean(player.isStarplayer); // Star player

                ByteStreamHelper.WriteDataReference(Stream, player.CharacterId);
                ByteStreamHelper.WriteDataReference(Stream, player.SkinId);

                Stream.WriteVInt(player.Trophies); // trophies
                Stream.WriteVInt(player.PowerPlayScore);
                Stream.WriteVInt(player.HeroPowerLevel + 1); // power level
                bool isOwn = player.AccountId == OwnPlayer.AccountId;
                Stream.WriteBoolean(isOwn);
                if (isOwn)
                {
                    Stream.WriteLong(player.AccountId);
                }

                player.DisplayData.Encode(Stream);
            }

            Stream.WriteVInt(2);
            {
                Stream.WriteVInt(0);
                Stream.WriteVInt(ExperienceReward);

                Stream.WriteVInt(8);
                Stream.WriteVInt(StarExperienceReward);
            }

            Stream.WriteVInt(MilestoneRewards.Count);
            foreach (int award in MilestoneRewards)
            {
                ByteStreamHelper.WriteDataReference(Stream, award);
            }

            Stream.WriteVInt(2);
            {
                Stream.WriteVInt(1);
                Stream.WriteVInt(OwnPlayer.Trophies); // Trophies
                Stream.WriteVInt(OwnPlayer.HighestTrophies); // Highest Trophies

                Stream.WriteVInt(5);
                Stream.WriteVInt(Experience);
                Stream.WriteVInt(Experience);
            }

            ByteStreamHelper.WriteDataReference(Stream, 28000000);

            Stream.WriteBoolean(false);

            if (Stream.WriteBoolean(ProgressiveQuests.Count > 0))
            {
                Stream.WriteVInt(ProgressiveQuests.Count);
                foreach (Quest quest in ProgressiveQuests)
                {
                    quest.Encode(Stream);
                }
            }
        }

        public override int GetMessageType()
        {
            return 23456;
        }

        public override int GetServiceNodeType()
        {
            return 27;
        }
    }
}
