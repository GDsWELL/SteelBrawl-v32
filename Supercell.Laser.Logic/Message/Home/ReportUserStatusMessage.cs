namespace Supercell.Laser.Logic.Message.Home
{
    public class ReportUserStatusMessage : GameMessage
    {
        public int Status;

        public override void Encode()
        {
            Stream.WriteInt(Status);
        }

        public override int GetMessageType()
        {
            return 20117;
        }

        public override int GetServiceNodeType()
        {
            return 9;
        }
    }
}
