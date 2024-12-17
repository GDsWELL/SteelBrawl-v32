namespace Supercell.Laser.Logic.Message.Friends
{
    using Supercell.Laser.Logic.Friends;

    public class AddFriendFailedMessage : GameMessage
    {
        public int Reason;

        public override void Encode()
        {
            Stream.WriteInt(Reason);
        }

        public override int GetMessageType()
        {
            return 20112;
        }

        public override int GetServiceNodeType()
        {
            return 3;
        }
    }
}
