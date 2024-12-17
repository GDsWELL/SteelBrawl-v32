namespace Supercell.Laser.Logic.Home.Items
{
    using Supercell.Laser.Logic.Data;
    using Supercell.Laser.Logic.Helper;
    using Supercell.Laser.Titan.DataStream;

    public class EventData
    {
        public bool IsBonusCollected;
        public int Slot;
        public int[] Modifiers;
        public int LocationId;
        public int PowerPlayGamesPlayed;
        public DateTime EndTime;
        public bool IsSecondary;
        public LocationData Location => DataTables.Get(DataType.Location).GetDataByGlobalId<LocationData>(LocationId);

        public void Encode(ByteStream encoder)
        {
            encoder.WriteVInt(0);
            encoder.WriteVInt(Slot);
            encoder.WriteVInt(IsSecondary ? (int)(EndTime - DateTime.Now).TotalSeconds : 0);
            encoder.WriteVInt((int)(EndTime - DateTime.Now).TotalSeconds);
            encoder.WriteVInt(10);

            ByteStreamHelper.WriteDataReference(encoder, Location);

            encoder.WriteBoolean(false); // Unk
            encoder.WriteBoolean(IsBonusCollected);
            encoder.WriteString(null); // 0xacecac
            encoder.WriteVInt(0); // 0xacecc0
            encoder.WriteVInt(PowerPlayGamesPlayed); // 0xacecd4
            encoder.WriteVInt(3); // 0xacece8

            encoder.WriteVInt(Modifiers.Length); // 0xacecfc
            foreach (int modifier in Modifiers)
            {
                encoder.WriteVInt(modifier);
            }

            encoder.WriteVInt(12); // 0xacee58
            encoder.WriteVInt(0); // 0xacee6c
        }
    }
}
