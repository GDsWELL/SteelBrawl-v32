namespace Supercell.Laser.Logic.Message.Home
{
    public class LobbyInfoMessage : GameMessage
    {
        public int PlayersCount;
        public string LobbyData;

        public override void Encode()
        {
            Stream.WriteVInt(PlayersCount);
            Stream.WriteString(LobbyData);
            Stream.WriteVInt(0);
        }

        public override int GetMessageType()
        {
            return 23457;
        }

        public override int GetServiceNodeType()
        {
            return 9;
        }
    }
}
