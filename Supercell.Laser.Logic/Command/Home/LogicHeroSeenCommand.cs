namespace Supercell.Laser.Logic.Command.Home
{
    using Supercell.Laser.Logic.Helper;
    using Supercell.Laser.Logic.Home;
    using Supercell.Laser.Logic.Home.Items;
    using Supercell.Laser.Titan.DataStream;

    public class LogicHeroSeenCommand : Command
    {
        public int CharacterId;
        public override void Decode(ByteStream stream)
        {
            base.Decode(stream);
            CharacterId = ByteStreamHelper.ReadDataReference(stream);
        }
        public override int Execute(HomeMode homeMode)
        {
            return 0;
        }

        public override int GetCommandType()
        {
            return 522;
        }
    }
}
