namespace Supercell.Laser.Logic.Command.Home
{
    using Supercell.Laser.Logic.Home;
    using Supercell.Laser.Logic.Home.Gatcha;
    using Supercell.Laser.Titan.DataStream;

    public class LogicGiveDeliveryItemsCommand : Command
    {
        public readonly List<DeliveryUnit> DeliveryUnits;

        public ForcedDrops ForcedDrops { get; set; }
        public int RewardTrackType { get; set; }
        public int RewardForRank { get; set; }
        public int RewardMilestoneIdx { get; set; }
        public int BrawlPassSeason { get; set; }

        public LogicGiveDeliveryItemsCommand() : base()
        {
            DeliveryUnits = new List<DeliveryUnit>();
        }

        public override void Encode(ByteStream stream)
        {
            stream.WriteVInt(0); // Unknown

            stream.WriteVInt(DeliveryUnits.Count);
            foreach (DeliveryUnit unit in DeliveryUnits)
            {
                unit.Encode(stream);
            }

            stream.WriteVInt(0); // Forced Drops

            stream.WriteVInt(RewardTrackType); // track
            stream.WriteVInt(RewardForRank); // idx
            stream.WriteVInt(BrawlPassSeason); // Unknown (Brawl Pass Related?)

            stream.WriteVInt(1); // Unknown (Unused)
            base.Encode(stream);
        }

        public override int Execute(HomeMode homeMode)
        {
            foreach (DeliveryUnit unit in DeliveryUnits)
            {
                foreach (GatchaDrop drop in unit.GetDrops())
                {
                    if (!drop.IsExecuted)
                    {
                        drop.DoDrop(homeMode);
                        drop.IsExecuted = true;
                    }
                    
                }
            }

            return 0;
        }

        public override int GetCommandType()
        {
            return 203;
        }
    }
}
