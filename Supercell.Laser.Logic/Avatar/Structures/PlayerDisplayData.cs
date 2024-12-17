namespace Supercell.Laser.Logic.Avatar.Structures
{
    using Supercell.Laser.Titan.DataStream;
    using Newtonsoft.Json;
    using Supercell.Laser.Logic.Avatar;
    using Supercell.Laser.Logic.Avatar.Structures;
    using Supercell.Laser.Logic.Listener;
    using Supercell.Laser.Titan.DataStream;

    public class PlayerDisplayData
    {
        public int ThumbnailId;
        public int NameColorId;
        public int HighNameColorId;
        public string Name;
        //[JsonIgnore] public ClientAvatar Avatar => LogicServerListener.Instance.GetAvatar(AccountId);

        public PlayerDisplayData()
        {
            ;
        }

        public PlayerDisplayData(bool hasPremiumPass, int thumbnail, int namecolor, string name)
        {
            ThumbnailId = thumbnail;
            NameColorId = namecolor;
            HighNameColorId = hasPremiumPass ? namecolor : 0;
            Name = name;
        }

        public void Encode(ByteStream stream)
        {
            stream.WriteString(Name);
            stream.WriteVInt(100);
            stream.WriteVInt(ThumbnailId);
            stream.WriteVInt(NameColorId);
            stream.WriteVInt(HighNameColorId);
        }
    }
}
