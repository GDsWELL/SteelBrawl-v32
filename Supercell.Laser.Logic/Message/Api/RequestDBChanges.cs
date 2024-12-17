namespace Supercell.Laser.Logic.Message.Api
{
    public class RequestDBChanges : GameMessage
    {
        public string AuthPass;
        public string Message;

        public override void Decode()
        {
            AuthPass = Stream.ReadString();
            Message = Stream.ReadString();
        }
        public override int GetMessageType()
        {
            return 19998;
        }

        public override int GetServiceNodeType()
        {
            return 1;
        }
    }
}
