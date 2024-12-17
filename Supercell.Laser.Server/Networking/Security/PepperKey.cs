﻿using Supercell.Laser.Titan.Library;

namespace Supercell.Laser.Server.Networking.Security
{
    public static class PepperKey
    {
        public const int VERSION = 13;
        
        public static readonly byte[] CLIENT_SK = { 0xB2, 0x88, 0xB7, 0x05, 0xC0, 0xA5, 0x0E, 0xF9, 0x13, 0x81, 0xAB, 0x09, 0x8B, 0xF7, 0x22, 0x92, 0x4E, 0x6C, 0x8D, 0x6F, 0xD0, 0x84, 0x4A, 0x3E, 0x20, 0x10, 0xDB, 0x3E, 0xD8, 0x93, 0x9B, 0x48 };
        public static readonly byte[] CLIENT_PK = TweetNaCl.CryptoScalarmultBase(CLIENT_SK);

        public static readonly byte[] SERVER_PK = { 0xC4, 0x1C, 0x48, 0x2E, 0xA2, 0xBB, 0xB5, 0x12, 0x19, 0xDD, 0x1A, 0x26, 0x70, 0x96, 0x0F, 0x47, 0x09, 0x46, 0x2E, 0xC4, 0xFD, 0xB6, 0xE7, 0xB6, 0x65, 0x21, 0xDD, 0x55, 0xF3, 0x37, 0xE6, 0x39 };
        //public static readonky 
        //public static readonly byte[] SERVER_PK = new byte[32];
        //public static readonly byte[] SERVER_PK = { 0xff, 0x1f, 0x00, 0x00, 0xff, 0x07, 0x00, 0x00, 0xff, 0x01, 0x00, 0x00, 0x7f, 0x00, 0x00, 0x00, 0xff, 0x1f, 0x00, 0x00, 0xff, 0x07, 0x00, 0x00, 0xff, 0x01, 0x00, 0x00, 0x7f, 0x00, 0x00, 0x00 };
    }
}