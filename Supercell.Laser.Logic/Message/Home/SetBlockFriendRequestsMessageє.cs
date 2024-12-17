namespace Supercell.Laser.Logic.Message.Home
{
    public class SetBlockFriendRequestsMessage : GameMessage
    {
        public bool State { get; set; }

        public override void Decode()
        {
            State = Stream.ReadBoolean();
        }

        public override int GetMessageType()
        {
            return 10576;
        }

        public override int GetServiceNodeType()
        {
            return 9;
        }
    }
}
