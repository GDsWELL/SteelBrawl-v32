namespace Supercell.Laser.Logic.Message.Home
{
    public class ReportAllianceStreamMessage : GameMessage
    {
        public long MessageIndex;

        public override void Decode()
        {
            MessageIndex = Stream.ReadLong();
        }

        public override int GetMessageType()
        {
            return 10119;
        }

        public override int GetServiceNodeType()
        {
            return 11;
        }
    }
}
