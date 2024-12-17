namespace Supercell.Laser.Logic.Message.Latency
{
    public class StartLatencyTestRequestMessage : GameMessage
    {

        public override void Encode()
        {
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteVInt(1); Stream.WriteInt(0); Stream.WriteInt(0); Stream.WriteInt(0); Stream.WriteInt(0); Stream.WriteInt(0); Stream.WriteInt(0); Stream.WriteInt(0); Stream.WriteInt(0); Stream.WriteInt(0);
        }

        public override int GetMessageType()
        {
            return 29001;
        }

        public override int GetServiceNodeType()
        {
            return 1;
        }
    }
}
