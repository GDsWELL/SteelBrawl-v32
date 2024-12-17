namespace Supercell.Laser.Logic.Message.Home
{
    public class SetInvitesBlockedMessage : GameMessage
    {
        public bool State { get; set; }

        public override void Decode()
        {
            State = Stream.ReadBoolean();
        }

        public override int GetMessageType()
        {
            return 14777;
        }

        public override int GetServiceNodeType()
        {
            return 9;
        }
    }
}
