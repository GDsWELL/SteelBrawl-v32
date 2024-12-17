namespace Supercell.Laser.Logic.Message.Api
{
    public class RequestSaveAll : GameMessage
    {
        public string AuthPass;

        public override void Decode()
        {
            AuthPass = Stream.ReadString();
        }
        public override int GetMessageType()
        {
            return 19997;
        }

        public override int GetServiceNodeType()
        {
            return 1;
        }
    }
}
