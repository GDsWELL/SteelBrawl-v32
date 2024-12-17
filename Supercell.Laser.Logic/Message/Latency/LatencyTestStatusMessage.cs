namespace Supercell.Laser.Logic.Message.Latency
{
    public class LatencyTestStatusMessage : GameMessage
    {
        public int Ping;

        public override void Encode()
        {
            Stream.WriteVInt(1);
            for (int i = 0; i < 1; i++)
            {
                Stream.WriteVInt(0); // R (Server Type(Number?))
                Stream.WriteVInt(Ping); // Ping
                Stream.WriteVInt(0); // Q
                Stream.WriteVInt(0); // C
                Stream.WriteInt(2); // Unk
                Stream.WriteInt(1);
                Stream.WriteInt(0);
                Stream.WriteString("localhost");
                Stream.WriteInt(1);
                Stream.WriteVInt(1);
            }

        }

        public override int GetMessageType()
        {
            return 29003;
        }

        public override int GetServiceNodeType()
        {
            return 1;
        }
    }
}
