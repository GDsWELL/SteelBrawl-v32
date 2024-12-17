using Supercell.Laser.Logic.Data.Reader;
using System.Collections.Generic;

namespace Supercell.Laser.Logic.Data.Helper
{
    public class DataTable
    {
        public List<LogicData> Datas;
        public DataType Index;

        public DataTable()
        {
            Datas = new List<LogicData>();
        }

        public DataTable(Table table, DataType index)
        {
            Index = index;
            Datas = new List<LogicData>();

            for (var i = 0; i < table.GetRowCount(); i += 2)
            {
                var row = table.GetRowAt(i);
                var data = DataTables.Create(Index, row, this);
                Datas.Add(data);
            }
        }

        public int Count
        {
            get
            {
                return Datas?.Count ?? 0;
            }
        }

        public List<LogicData> GetDatas()
        {
            return Datas;
        }

        public LogicData GetDataWithId(int id)
        {
            int index = GlobalId.GetInstanceId(id);
            if (index < 0 || index >= Datas.Count)
            {
                return null; // Добавляем проверку границ индекса
            }

            return Datas[index];
        }

        public T GetDataWithId<T>(int id) where T : LogicData
        {
            int index = GlobalId.GetInstanceId(id);
            if (index < 0 || index >= Datas.Count)
            {
                return null; // Добавляем проверку границ индекса
            }

            return Datas[index] as T;
        }

        public T GetData<T>(string name) where T : LogicData
        {
            return Datas.Find(data => data.GetName() == name) as T;
        }

        public T GetData<T>(int id) where T : LogicData
        {
            if (id < 0 || id >= Datas.Count)
            {
                return null; // Проверка границ индекса
            }

            return Datas[id] as T;
        }

        public T GetDataByGlobalId<T>(int id) where T : LogicData
        {
            id = GlobalId.GetInstanceId(id);
            if (id < 0 || id >= Datas.Count)
            {
                return null; // Добавляем проверку границ индекса
            }

            return Datas[id] as T;
        }

        public int GetInstanceId(string name)
        {
            var data = Datas.Find(d => d.GetName() == name);
            if (data == null)
            {
                return -1; // Если не найдено, возвращаем -1
            }

            return data.GetInstanceId();
        }

        public int GetIndex()
        {
            return (int)Index;
        }
    }
}
