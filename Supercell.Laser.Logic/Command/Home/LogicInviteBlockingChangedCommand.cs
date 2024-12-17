namespace Supercell.Laser.Logic.Command.Home
{
    using Supercell.Laser.Logic.Home;
    using Supercell.Laser.Logic.Notification;
    using Supercell.Laser.Titan.DataStream;

    public class LogicInviteBlockingChangedCommand : Command
    {
        public bool State;

        public override void Encode(ByteStream stream)
        {
            stream.WriteBoolean(State);
            base.Encode(stream);
        }

        public override int Execute(HomeMode homeMode)
        {
            return 0;
        }

        public override int GetCommandType()
        {
            return 213;
        }
    }
}
