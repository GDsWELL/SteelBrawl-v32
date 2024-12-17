namespace Supercell.Laser.Logic.Message.Account.Auth
{
    public class CreateAccountOkMessage : GameMessage
    {
        public long AccountId;
        public string PassToken;


        public override void Encode()
        {
            Stream.WriteStringReference(PassToken);
            Stream.WriteLong(AccountId);
            
        }

        public override int GetMessageType()
        {
            return 26007;
        }

        public override int GetServiceNodeType()
        {
            return 1;
        }
    }
}
