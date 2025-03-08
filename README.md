# Инструкция по использованию бота

## Запуск локально

Установка необходимых зависимостей

`pip install -r requirements.txt`

`python bot.py`

## Запуск на сервере (Linux)

```
mkdir /path/to/weatherbot

git clone https://github.com/timurrsamm/weatherbot

pip install -r requirements.txt

```

### Запуск скрипта как системного сервиса

- Создаем новый конфиг файл в папке /etc/systemd/system
```
cd /etc/systemd/system
sudo nano weatherbot.service
```

- Записываем конфигурацию сервиса в файл weatherbot.service

```
[Unit]
Description=Python Weather Bot
After=syslog.target network.target

[Service]
Type=simple
WorkingDirectory=/path/to/weatherbot/
ExecStart=/usr/bin/python3 /path/to/weatherbot/bot.py

Restart=always
RestartSec=120

[Install]
WantedBy=multi-user.target
```

- Обновляем список доступных сервисов  

```
sudo sysemctl daemon-reload
```

- Запускаем сервис

```
sudo systemctl start weatherbot.service
```

- Настраиваем, чтобы сервис запускался при запуске/перезагрузке ОС

```
sudo systemctl enable weatherbot.service 
```

- Посмотреть статус сервиса

```
sudo systemctl status weatherbot.service
```

- Перезапустить сервис

```
sudo systemctl start weatherbot.service
```