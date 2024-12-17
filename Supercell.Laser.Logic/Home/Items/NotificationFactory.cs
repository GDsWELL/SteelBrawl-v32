namespace Supercell.Laser.Logic.Home.Items
{
    using Newtonsoft.Json;
    using Supercell.Laser.Logic.Helper;
    using Supercell.Laser.Titan.DataStream;

    public class NotificationFactory
    {
        [JsonProperty("notification_list")]
        public List<Notification> NotificationList;

        public NotificationFactory()
        {
            NotificationList = new List<Notification>();
        }

        public void Add(Notification notification)
        {
            notification.Index = GetIndex();
            NotificationList.Add(notification);
        }

        public int GetIndex()
        {
            return NotificationList.Count;
        }

        public void Encode(ByteStream stream)
        {
            stream.WriteVInt(NotificationList.Count);
            foreach (Notification notification in NotificationList)
            {
                notification.Encode(stream);
            }

        }
    }
}
