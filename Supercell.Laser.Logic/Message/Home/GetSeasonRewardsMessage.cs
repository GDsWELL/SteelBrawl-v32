namespace Supercell.Laser.Logic.Message.Home
{
    public class GetSeasonRewardsMessage : GameMessage
    {
        public override int GetMessageType()
        {
            return 14277;
        }

        public override int GetServiceNodeType()
        {
            return 9;
        }
    }
}
