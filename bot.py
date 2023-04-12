import telebot
from pprint import pprint
import requests
import datetime
import os
from dotenv import load_dotenv


load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
API_WEATHER_KEY = os.getenv('API_WEATHER_KEY')

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def start_greeting(message):
    bot.send_message(message.chat.id, f'Привет! Напиши название города ...')


@bot.message_handler(content_types=['text'])
def treat_city(message):
    city = message.text.strip().lower()
    params = {'q': city, 'appid': API_WEATHER_KEY, 'units': 'metric', 'lang': 'ru'}
    response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
    pprint(response.json())
    if response:
        data = response.json()
        temp = data['main']['temp']
        feeling = data['main']['feels_like']
        descr = data['weather'][0]['description']
        wind = data['wind']['speed']
        sunset_time = str(datetime.timedelta(seconds=data['sys']['sunset'] + data['timezone'])).split(', ')[-1]
        now_time = str(datetime.timedelta(seconds=data['dt'] + data['timezone'])).split(', ')[-1]

        bot.send_message(message.chat.id, f'Город: {city.title()}\nПогода: {descr}\n'
                                          f'Температура: {temp}\nОщущается как: {feeling}\n'
                                          f'Скорость ветра: {wind}\nЗакат: {sunset_time}\n'
                                          f'Местное время: {now_time}')
        # bot.send_photo(message.chat.id, f'https://openweathermap.org/img/wn/{data["weather"][0]["icon"]}@2x.png')

        idd, image = data['weather'][0]['id'], None
        if idd < 300:
            image = 'thunderstorm.jpg'
        elif idd < 600:
            image = 'rain.jpg'
        elif idd < 700:
            image = 'snow.jpg'
        elif idd == 800:
            image = 'clear-sky.jpg'
        else:
            image = 'cloud.jpg'
        with open(f'./images/{image}', 'rb') as file:
            bot.send_photo(message.chat.id, file)
    else:
        bot.send_message(message.chat.id, 'Такого города не существует, попробуйте снова!')


bot.infinity_polling()
