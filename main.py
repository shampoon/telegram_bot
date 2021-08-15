import requests
import telebot
import json
from secure import TELEGRAM_TOKEN, weather_appid

citys_dict = {'уфе': 'Ufa', 'москве': 'Moscow'}
bot = telebot.TeleBot(TELEGRAM_TOKEN)


def get_info_db():
    import sqlite3

    try:
        sqlite_connection = sqlite3.connect('sqlite_python.db')
        cursor = sqlite_connection.cursor()
        print("База данных создана и успешно подключена к SQLite")

        sqlite_select_query = "select sqlite_version();"
        cursor.execute(sqlite_select_query)
        record = cursor.fetchall()
        print("Версия базы данных SQLite: ", record)
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    f_name = message.chat.first_name
    if message.text[1:] == "ривет":
        bot.send_message(message.from_user.id, f"Привет {f_name}, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши привет \nИли спроси про погоду")
    elif 'погода' in message.text.lower():
        words = message.text.lower().split(' ')
        city = None
        for w in words:
            if citys_dict.get(w):
                city = citys_dict.get(w)
        if city:
            res = requests.get("http://api.openweathermap.org/data/2.5/find",
                               params={'q': city, 'type': 'like', 'units': 'metric', 'APPID': weather_appid})
            w_js = json.loads(res.content)['list'][0]
            city = w_js['name']
            temp = w_js['main']['temp']
            feels_like = w_js['main']['feels_like']
            temp_min = w_js['main']['temp_min']
            temp_max = w_js['main']['temp_max']
            pressure = w_js['main']['pressure']
            humidity = w_js['main']['humidity']
            wind_speed = w_js['wind']['speed']
            rain = w_js['rain']
            snow = w_js['snow']
            clouds = w_js['clouds']['all']
            weather_desc = w_js['weather'][0]['main']

            weather = f'Погода в {city}:\n' \
                      f'сейчас {weather_desc} {temp} °C \n' \
                      f'ощущается как {feels_like} °C     облачность {clouds}%\n' \
                      f'давление {pressure} кПа влажность {humidity}%\n' \
                      f'скорость ветра до {wind_speed}\n' \
                      f'дождь начнется через {rain} ' \
                      f'снег начнется через {snow}'

            bot.send_message(message.from_user.id, weather)
        else:
            print([c for c in citys_dict.keys()])
            bot.send_message(message.from_user.id, "Неизвестный для меня город \n" +
                             "Я знаю погоду в " + ' '.join(list(citys_dict)))
    else:
        bot.send_message(message.from_user.id, f"{f_name}, я тебя не понимаю. Напиши /help.")


# get_info_db()
bot.polling(none_stop=True, interval=0)
