namespace Supercell.Laser.Server.Networking
{
    public class Login{
        public string IPAddress;
        public int LastLogin;
        public int BadLogins;
        public bool IPBanned = false;

        public Login()
        {
            IPBanned = false;
        }
    }
}