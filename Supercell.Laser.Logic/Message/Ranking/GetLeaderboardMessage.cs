namespace Supercell.Laser.Logic.Message.Ranking
{
    using Supercell.Laser.Logic.Helper;
    public class GetLeaderboardMessage : GameMessage
    {

        public bool IsRegional { get; set; }
        public int LeaderboardType { get; set; }

        public int CharachterId { get; set; }

        public override void Decode()
        {
            base.Decode();

            IsRegional = Stream.ReadBoolean();
            LeaderboardType = Stream.ReadVInt();
            CharachterId = ByteStreamHelper.ReadDataReference(Stream);
        }

        public override int GetMessageType()
        {
            return 14403;
        }

        public override int GetServiceNodeType()
        {
            return 9;
        }
    }
}
