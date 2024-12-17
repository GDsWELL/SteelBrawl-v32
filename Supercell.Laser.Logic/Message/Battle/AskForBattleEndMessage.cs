namespace Supercell.Laser.Logic.Message.Battle
{
    using Supercell.Laser.Logic.Battle.Input;
    using Supercell.Laser.Logic.Helper;
    using Supercell.Laser.Logic.Message;
    using Supercell.Laser.Titan.DataStream;
    using Supercell.Laser.Logic.Battle.Structures;
    using Supercell.Laser.Logic.Home;

    public class AskForBattleEndMessage : GameMessage
    {
        public int BattleResult;
        public int Rank;
        public int LocationId;
        public int BattlePlayersCount;
        public BattlePlayer[] BattlePlayers;
        public override void Decode()
        {
            BattleResult = Stream.ReadVInt();
            Stream.ReadVInt(); // Unknown
            Rank = Stream.ReadVInt();
            LocationId = ByteStreamHelper.ReadDataReference(Stream);
            BattlePlayersCount = Stream.ReadVInt();
            BattlePlayers = new BattlePlayer[BattlePlayersCount];
            for (int x = 0; x < BattlePlayersCount; x++)
            {
                BattlePlayers[x] = new BattlePlayer();
                BattlePlayers[x].Decode(Stream);
            }
        }

        public override int GetMessageType()
        {
            return 14110;
        }

        public override int GetServiceNodeType()
        {
            return 27;
        }
    }
}
