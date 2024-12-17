# SteelBrawl-v32

![Screenshot](https://github.com/GDsWELL/SteelBrawl-v32/blob/main/screen.jpg)

# Как запустить?

  # 1. Скачайте dotnet 6.0 на свой VPS:
  `wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb`
  
  `sudo dpkg -i packages-microsoft-prod.deb`
  
  `rm packages-microsoft-prod.deb`
  
  `sudo apt-get update && \
    sudo apt-get install -y dotnet-sdk-6.0`
  
  # 2. Скачайте на ваш VPS MySQL и phpmyadmin:
  
  Мне лень тут чёт писать, сами в инете найдите
  
  `Use Google`
  
  # 3. Импортируйте файл `database.sql` из репозитрия в вашу базу
     
  # 4. Откройте папку Supercell.Laser.Server:
     cd Supercell.Laser.Server
  
  # 5. Запустите файл Program.cs:
     dotnet run Program.cs
     
  # 6. Ну тут вроде всё должно запуститься и работать

   



