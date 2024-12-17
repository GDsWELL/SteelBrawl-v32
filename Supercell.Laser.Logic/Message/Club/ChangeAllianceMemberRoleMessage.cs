namespace Supercell.Laser.Logic.Message.Club
{

    public class ChangeAllianceMemberRoleMessage : GameMessage
    {
        public long AccountId;
        public int Role;

        public override void Decode()
        {
            AccountId = Stream.ReadLong();
            Role = Stream.ReadVInt();
        }

        public override int GetMessageType()
        {
            return 14306;
        }

        public override int GetServiceNodeType()
        {
            return 11;
        }
    }
}
