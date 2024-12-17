namespace Supercell.Laser.Logic.Util
{
    using Supercell.Laser.Titan.Debug;
    using Supercell.Laser.Titan.Math;
    using System.Numerics;

    public static class LogicBitHelper
    {
        public static bool Get(BigInteger value, int index)
        {
            // Здвигаємо біт вправо до потрібної позиції та витягуємо його
            return ((value >> index) & BigInteger.One) == BigInteger.One;
        }

        public static BigInteger Set(BigInteger value, int index, bool data)
        {
            // Знімаємо біт за вказаним індексом
            value &= ~(BigInteger.One << index);

            // Встановлюємо новий біт, якщо data == true
            if (data)
                value |= (BigInteger.One << index);

            return value;
        }
    }
}
