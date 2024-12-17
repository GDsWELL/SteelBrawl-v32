namespace Supercell.Laser.Logic.Home.Gatcha
{
    using Supercell.Laser.Logic.Avatar;
    using Supercell.Laser.Logic.Data;
    using Supercell.Laser.Logic.Helper;
    using Supercell.Laser.Logic.Home.Structures;
    using Supercell.Laser.Titan.DataStream;

    public class GatchaDrop
    {
        public int Count;
        public int DataGlobalId;
        public int SkinGlobalId;
        public int CardGlobalId;
        public int PinGlobalId;
        public int Type;

        public bool IsExecuted;

        public GatchaDrop(int type)
        {
            Type = type;
        }

        public void DoDrop(HomeMode homeMode)
        {
            ClientAvatar avatar = homeMode.Avatar;

            switch (Type)
            {
                case 1: // Unlock a hero
                    CharacterData characterData = DataTables.Get(16).GetDataByGlobalId<CharacterData>(DataGlobalId);
                    if (characterData == null) return;

                    CardData cardData = DataTables.Get(23).GetData<CardData>(characterData.Name + "_unlock");
                    if (cardData == null && characterData.Name == "PowerLeveler") cardData = DataTables.Get(23).GetDataByGlobalId<CardData>(23000279);
                    if (cardData == null && characterData.Name == "Percenter") cardData = DataTables.Get(23).GetDataByGlobalId<CardData>(23000296);
                    if (cardData == null) return;

                    avatar.UnlockHero(characterData.GetGlobalId(), cardData.GetGlobalId());
                    break;
                case 2:
                    homeMode.Home.TokenDoublers += Count;
                    break;
                case 4:
                    avatar.Starpowers.Add(CardGlobalId);
                    break;
                case 6: // Add power points
                    Hero hero = avatar.GetHero(DataGlobalId);
                    if (hero == null) return;

                    hero.PowerPoints += Count;
                    break;
                case 7: // Add gold
                    avatar.AddGold(Count);
                    break;
                case 8: // Add Gems (Bonus)
                    avatar.AddDiamonds(Count);
                    break;
                case 9: // Add Gems (Bonus)
                    homeMode.Home.UnlockedSkins.Add(SkinGlobalId);
                    break;
                case 10:
                    homeMode.Home.UnlockedEmotes.Add(DataGlobalId);
                    break;
                case 11:
                    homeMode.Home.UnlockedEmotes.Add(DataGlobalId);
                    break;
            }
        }

        public void Encode(ByteStream stream)
        {
            stream.WriteVInt(Count);
            ByteStreamHelper.WriteDataReference(stream, DataGlobalId);
            stream.WriteVInt(Type);

            ByteStreamHelper.WriteDataReference(stream, SkinGlobalId);
            ByteStreamHelper.WriteDataReference(stream, PinGlobalId);
            ByteStreamHelper.WriteDataReference(stream, CardGlobalId);
            stream.WriteVInt(0);
        }
    }
}
