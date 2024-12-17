namespace Supercell.Laser.Logic.Command.Home
{
    using Supercell.Laser.Logic.Helper;
    using Supercell.Laser.Logic.Home;
    using Supercell.Laser.Logic.Home.Structures;
    using Supercell.Laser.Titan.DataStream;

    public class LogicClaimDailyRewardCommand : Command
    {
        public int Slot;

        public override void Decode(ByteStream stream)
        {
            base.Decode(stream);
            Slot = stream.ReadVInt();
        }

        public override int Execute(HomeMode homeMode)
        {
            return 0;
        }

        public override int GetCommandType()
        {
            return 503;
        }
    }
}
