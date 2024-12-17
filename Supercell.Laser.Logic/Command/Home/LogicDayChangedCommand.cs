namespace Supercell.Laser.Logic.Command.Home
{
    using Supercell.Laser.Logic.Home;
    using Supercell.Laser.Logic.Notification;
    using Supercell.Laser.Titan.DataStream;

    public class LogicDayChangedCommand : Command
    {
        public ClientHome Home;

        public override void Encode(ByteStream stream)
        {
            DateTime utcNow = DateTime.UtcNow;
            stream.WriteVInt(1);
            Home.LogicConfData(stream, utcNow);
            base.Encode(stream);
        }

        public override int Execute(HomeMode homeMode)
        {
            return 0;
        }

        public override int GetCommandType()
        {
            return 204;
        }
    }
}
