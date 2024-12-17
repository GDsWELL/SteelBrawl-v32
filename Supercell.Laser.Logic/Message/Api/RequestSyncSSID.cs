using Supercell.Laser.Logic.Home.Quest;

namespace Supercell.Laser.Logic.Message.Api
{
    public class RequestSyncSSID : GameMessage
    {
        public string AuthPass;
        public Dictionary<string, string> Requests;
        public List<string> DisposeRequests;

        public override void Decode()
        {
            Requests = new();
            DisposeRequests = new();
            AuthPass = Stream.ReadString();
            int Count = Stream.ReadInt();
            for (int x = 0; x < Count; x++)
            {
                Requests.Add(Stream.ReadString(), Stream.ReadString());
            }
            int DCount = Stream.ReadInt();
            for (int y = 0; y < DCount; y++)
            {
                DisposeRequests.Add(Stream.ReadString());
            }
        }
        public override int GetMessageType()
        {
            return 11000;
        }

        public override int GetServiceNodeType()
        {
            return 1;
        }
    }
}
