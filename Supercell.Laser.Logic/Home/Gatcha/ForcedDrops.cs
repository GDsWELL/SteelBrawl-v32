namespace Supercell.Laser.Logic.Home.Gatcha
{
    using Supercell.Laser.Logic.Avatar;
    using Supercell.Laser.Logic.Data;
    using Supercell.Laser.Logic.Helper;
    using Supercell.Laser.Logic.Home.Structures;
    using Supercell.Laser.Titan.DataStream;

    public class ForcedDrops
    {

        public void Encode(ByteStream stream)
        {
            stream.WriteBoolean(false);
        }
    }
}
