namespace Supercell.Laser.Logic.Message.Account
{
	using System;
	using System.Collections.Generic;
	using System.Linq;
	using System.Text;
	using System.Threading.Tasks;

	public class DebugOpenMessage : GameMessage
	{
		public override int GetMessageType()
		{
			return 20500;
		}

		public override int GetServiceNodeType()
		{
			return 1;
		}
	}
}
