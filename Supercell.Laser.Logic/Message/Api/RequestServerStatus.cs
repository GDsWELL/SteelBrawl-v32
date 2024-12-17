namespace Supercell.Laser.Logic.Message.Api
{
    public class RequestServerStatus : GameMessage
    {
        public override int GetMessageType()
        {
            return 19999;
        }

        public override int GetServiceNodeType()
        {
            return 1;
        }
    }
}
