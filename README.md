### Telegram-bot

```
Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.
Присылает сообщения в телегу, когда статус изменен: 
- "Работа проверена: ревьюеру всё понравилось. Ура!"
- "Работа взята на проверку ревьюером."
- "Работа проверена: у ревьюера есть замечания."
```

### Используемые технологии:
- Python 3.9
- python-dotenv 0.19.0
- python-telegram-bot 13.7

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Saborrr/homework_bot.git
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение (на Win):

```
python -m venv env
```

```
source venv/scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Занести в переменные окружения (файл .env) свои данные:
- токен профиля на Яндекс.Практикуме
- токен телеграм-бота
- свой ID в телеграме


Запустить проект:

```
python homework.py
```
### Автор

[Saborrr](https://github.com/Saborrr)
