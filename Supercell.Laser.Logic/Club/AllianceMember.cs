namespace Supercell.Laser.Logic.Club
{
    using Newtonsoft.Json;
    using Supercell.Laser.Logic.Avatar;
    using Supercell.Laser.Logic.Avatar.Structures;
    using Supercell.Laser.Logic.Data.Helper;
    using Supercell.Laser.Logic.Listener;
    using Supercell.Laser.Titan.DataStream;

    public class AllianceMember
    {
        [JsonProperty("displayData")] public PlayerDisplayData DisplayData { get; set; }
        [JsonProperty("accountId")] public long AccountId { get; set; }
        [JsonProperty("trophies")] public int Trophies { get; set; }
        [JsonProperty("DoNotDisturb")] public bool DoNotDisturb { get; set; }
        [JsonProperty("role")] public AllianceRole Role { get; set; }

        [JsonIgnore] public ClientAvatar Avatar
        {
            get
            {
                return LogicServerListener.Instance.GetAvatar(AccountId);
            }
        }

        [JsonIgnore]
        public bool IsOnline
        {
            get
            {
                return LogicServerListener.Instance.IsPlayerOnline(AccountId);
            }
        }

        public AllianceMember()
        {
            // For json...
        }

        public AllianceMember(ClientAvatar avatar)
        {
            DisplayData = new PlayerDisplayData(avatar.HomeMode.Home.HasPremiumPass, avatar.HomeMode.Home.ThumbnailId, avatar.HomeMode.Home.NameColorId, avatar.Name);
            AccountId = avatar.AccountId;
            Trophies = avatar.Trophies;
            Role = avatar.AllianceRole;
            DoNotDisturb = avatar.DoNotDisturb;
        }

        public void Encode(ByteStream stream)
        {
            ClientAvatar avatar = Avatar;

            stream.WriteLong(AccountId);
            stream.WriteVInt((int)Role);
            stream.WriteVInt(avatar.Trophies);

            stream.WriteVInt(IsOnline ? avatar.PlayerStatus : 0); // PlayerStatus
            stream.WriteVInt(IsOnline ? -1 : (int)(DateTime.UtcNow - avatar.LastOnline).TotalSeconds);

            stream.WriteBoolean(DoNotDisturb); // ??
            
            DisplayData.Encode(stream);
        }
    }
}
