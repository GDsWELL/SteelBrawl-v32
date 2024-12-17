namespace Supercell.Laser.Logic.Message.Account.Auth
{
    public class AuthenticationOkMessage : GameMessage
    {
        public long AccountId;
        public string PassToken;
        public string ServerEnvironment;

        public int Major;
        public int Minor;
        public int Build;

        public AuthenticationOkMessage() : base()
        {
            ;
        }

        public override void Encode()
        {
            Stream.WriteLong(AccountId);
            Stream.WriteLong(AccountId);

            Stream.WriteString(PassToken);
            Stream.WriteString(null);
            Stream.WriteString(null);

            Stream.WriteInt(Major);
            Stream.WriteInt(Build);
            Stream.WriteInt(Minor);

            Stream.WriteString(ServerEnvironment);

            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteInt(0);
            Stream.WriteString("103121310241222"); // Facebook Application ID
        Stream.WriteString(""); // Server Time
        Stream.WriteString(""); // Account Created Date
        Stream.WriteInt(0); // Startup Cooldown
        Stream.WriteString(null); // Google Service ID
        Stream.WriteString("BR"); // Login Country
        Stream.WriteString(null); // Kunlun ID 
        Stream.WriteInt(2); // Tier
            Stream.WriteString("");
        Stream.WriteInt(2); // Url Entry Array Count
            Stream.WriteString("https://game-assets.brawlstarsgame.com");
            Stream.WriteString("http://a678dbc1c015a893c9fd-4e8cc3b1ad3a3c940c504815caefa967.r87.cf2.rackcdn.com");
        Stream.WriteInt(2); // Url Entry Array Count
        Stream.WriteString("https://raw.githubusercontent.com/IsaaSooBarr/Project-LaserScratch/main/Files/EventAssets/"); // Event Assets
            Stream.WriteString("https://24b999e6da07674e22b0-8209975788a0f2469e68e84405ae4fcf.ssl.cf2.rackcdn.com/event-assets");
        }

        public override int GetMessageType()
        {
            return 20104;
        }

        public override int GetServiceNodeType()
        {
            return 1;
        }
    }
}
