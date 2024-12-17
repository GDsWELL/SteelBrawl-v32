namespace Supercell.Laser.Logic.Message.Team
{
    public class TeamErrorMessage : GameMessage
    {
        public int Reason;

        public override void Encode()
        {
            Stream.WriteInt(Reason);
        }

        public override int GetMessageType()
        {
            return 24129;
        }

        public override int GetServiceNodeType()
        {
            return 9;
        }
    }
}
