namespace Supercell.Laser.Logic.Message.Api
{
    public class SyncSSIDResponce : GameMessage
    {
        public Dictionary<string, string> Requests;
        public Dictionary<string, List<string>> RecAccs;


        public override void Encode()
        {
            Stream.WriteInt(Requests.Count);
            foreach (KeyValuePair<string, string> r in Requests)
            {
                Stream.WriteString(r.Key);
                Stream.WriteString(r.Value);
            }
            Stream.WriteInt(RecAccs.Count);
            foreach (KeyValuePair<string, List<string>> r in RecAccs)
            {
                Stream.WriteString(r.Key);
                Stream.WriteString(r.Value[0]);
                Stream.WriteString(r.Value[1]);
            }
        }
        public override int GetMessageType()
        {
            return 21000;
        }

        public override int GetServiceNodeType()
        {
            return 1;
        }
    }
}
