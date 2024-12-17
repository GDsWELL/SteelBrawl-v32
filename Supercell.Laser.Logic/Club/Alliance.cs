namespace Supercell.Laser.Logic.Club
{
    using Newtonsoft.Json;
    using Supercell.Laser.Logic.Avatar;
    using Supercell.Laser.Logic.Data.Helper;
    using Supercell.Laser.Logic.Listener;
    using Supercell.Laser.Logic.Message;
    using Supercell.Laser.Logic.Message.Club;
    using Supercell.Laser.Logic.Stream;
    using Supercell.Laser.Logic.Stream.Entry;
    using Supercell.Laser.Titan.DataStream;

    public class Alliance
    {
        [JsonProperty("id")] public long Id;

        [JsonProperty("name")] public string Name { get; set; }
        [JsonProperty("desc")] public string Description { get; set; }

        [JsonProperty("members")] public List<AllianceMember> Members { get; set; }

        [JsonProperty("badge")] public int AllianceBadgeId { get; set; }
        [JsonProperty("required_trophies")] public int RequiredTrophies { get; set; }

        [JsonProperty("type")] public int Type { get; set; }

        [JsonProperty("stream")] public AllianceStream Stream { get; set; }

        public Alliance()
        {
            Name = "Alliance";
            Description = string.Empty;
            Members = new List<AllianceMember>();
            AllianceBadgeId = GlobalId.CreateGlobalId(8, 0);
            Stream = new AllianceStream();
            Type = 1;
        }

        public int OnlinePlayers
        {
            get
            {
                int result = 0;

                foreach (AllianceMember entry in Members.ToArray())
                {
                    if (LogicServerListener.Instance.IsPlayerOnline(entry.AccountId)) result++;
                }

                return result;
            }
        }

        public void SendToAlliance(GameMessage Message)
        {
            foreach (AllianceMember member in Members.ToArray())
            {
                if (LogicServerListener.Instance.IsPlayerOnline(member.AccountId))
                {
                    LogicGameListener listener = LogicServerListener.Instance.GetGameListener(member.AccountId);
                    listener.SendTCPMessage(Message);
                }
            }
        }

        public bool getRoleVector(AllianceRole v1, AllianceRole v2)
        {
            AllianceRole None = 0,
                    Member = (AllianceRole)1,
                    Leader = (AllianceRole)2,
                    Elder = (AllianceRole)3,
                    CoLeader = (AllianceRole)4;
            return (v1 == Member && v2 == Elder) || (v1 == Elder && v2 == CoLeader) || (v1 == CoLeader && v2 == Leader);
        }

        public AllianceMember GetNextRoleMember()
        {
            AllianceMember coleader = Members.Find(member => member.Role == AllianceRole.CoLeader);
            if (coleader != null) return coleader;

            AllianceMember elder = Members.Find(member => member.Role == AllianceRole.Elder);
            if (elder != null) return elder;

            AllianceMember member = Members.Find(member => member.Role == AllianceRole.Member);
            if (member != null) return member;

            return null;
        }

        public void AddStreamEntry(AllianceStreamEntry entry)
        {
            Stream.AddEntry(entry);
            SendAllianceStreamEntryToAll(entry);
        }

        public void SendChatMessage(long id, string message)
        {
            AllianceMember member = GetMemberById(id);
            if (member == null) return;
            AllianceStreamEntry entry = Stream.SendChatMessage(member, message);

            SendAllianceStreamEntryToAll(entry);
        }

        public void SendAllianceStreamEntryToAll(AllianceStreamEntry entry)
        {
            AllianceStreamEntryMessage message = new AllianceStreamEntryMessage();
            message.Entry = entry;

            foreach (AllianceMember member in Members.ToArray())
            {
                if (LogicServerListener.Instance.IsPlayerOnline(member.AccountId))
                {
                    LogicGameListener listener = LogicServerListener.Instance.GetGameListener(member.AccountId);
                    listener.SendTCPMessage(message);
                }
            }
        }

        public AllianceMember GetMemberById(long id)
        {
            return Members.Find(member => member.AccountId == id);
        }

        public void RemoveMemberById(long id)
        {
            AllianceMember member = Members.Find(member => member.AccountId == id);
            Members.Remove(member);
        }

        public int Trophies
        {
            get
            {
                int result = 0;
                foreach (AllianceMember member in Members)
                {
                    result += member.Avatar.Trophies;
                }
                return result;
            }
        }

        public AllianceHeader Header
        {
            get
            {
                return new AllianceHeader(Id, Name, AllianceBadgeId, Members.Count, Trophies, RequiredTrophies, Type);
            }
        }

        public void Encode(ByteStream stream)
        {
            Header.Encode(stream);
            stream.WriteString(Description);

            AllianceMember[] members = Members.ToArray();
            stream.WriteVInt(members.Length);
            foreach (AllianceMember member in members)
            {
                member.Encode(stream);
            }
        }
    }
}
