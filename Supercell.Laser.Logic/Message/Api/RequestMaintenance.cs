namespace Supercell.Laser.Logic.Message.Api
{
    public class RequestMaintenance : GameMessage
    {
        public string AuthPass;

        public override void Decode()
        {
            AuthPass = Stream.ReadString();
        }
        public override int GetMessageType()
        {
            return 19996;
        }

        public override int GetServiceNodeType()
        {
            return 1;
        }
    }
}
