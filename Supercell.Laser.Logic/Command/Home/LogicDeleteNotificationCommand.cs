namespace Supercell.Laser.Logic.Command.Home
{
    using Supercell.Laser.Logic.Home;
    using Supercell.Laser.Logic.Home.Items;
    using Supercell.Laser.Titan.DataStream;

    public class LogicDeleteNotificationCommand : Command
    {
        public int NotificationIndex;
        public override void Decode(ByteStream stream)
        {
            base.Decode(stream);
            NotificationIndex = stream.ReadVInt();
        }

        public override int Execute(HomeMode h)
        {
            return 0;
        }

        public override int GetCommandType()
        {
            return 514;
        }
    }
}
