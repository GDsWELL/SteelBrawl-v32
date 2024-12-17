namespace Supercell.Laser.Logic.Message.Latency
{
    public class LatencyTestResultMessage : GameMessage
    {
        public override int GetMessageType()
        {
            return 19001;
        }

        public override int GetServiceNodeType()
        {
            return 9;
        }
    }
}
