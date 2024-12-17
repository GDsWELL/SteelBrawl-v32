using System.Text;

namespace Supercell.Laser.Logic.Message.Security
{
    public class ServerHelloMessage : GameMessage
    {
        private byte[] _serverHelloToken;
        public byte serversc;

        public ServerHelloMessage() : base()
        {
            _serverHelloToken = new byte[24];
        }

        public override void Encode()
        {
            Stream.WriteByte(_serverHelloToken[23]);
            Stream.WriteByte(serversc);
            Stream.WriteBytes(_serverHelloToken, 22);
            Stream.WriteBytes(Encoding.ASCII.GetBytes("Hi :)"), 5);
        }

        public void SetServerHelloToken(byte[] token)
        {
            _serverHelloToken = token;
        }

        public byte[] RemoveServerHelloToken()
        {
            byte[] token = _serverHelloToken;
            _serverHelloToken = null;
            return token;
        }

        public override int GetMessageType()
        {
            return 20100;
        }

        public override int GetServiceNodeType()
        {
            return 1;
        }
    }
}
