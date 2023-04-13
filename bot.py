import telebot
from telebot import types
from pprint import pprint
import requests
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
API_WEATHER_KEY = os.getenv('API_WEATHER_KEY')
link = 'https://api.openweathermap.org/data/2.5/weather'

bot = telebot.TeleBot(API_TOKEN)
markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
btn = types.KeyboardButton('Отправить геолокацию', request_location=True)
markup.add(btn)


@bot.message_handler(commands=['start'])
def start_greeting(message):
    text = 'Привет! Напиши название <u><i>города</i></u> или узнай погоду по <u><i>геолокации</i></u>'
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='html')


@bot.message_handler(content_types=['location'])
def location(message):
    lat, lon = message.location.latitude, message.location.longitude
    params = {'lat': lat,
              'lon': lon,
              'appid': API_WEATHER_KEY,
              'units': 'metric',
              'lang': 'ru'}
    response = requests.get(link, params=params)
    if response:
        send_weather_info(message, response.json())
    else:
        bot.send_message(message.chat.id, 'Извините, ошибка, попробуйте снова!', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def treat_city(message):
    city = message.text.strip().lower()
    params = {'q': city,
              'appid': API_WEATHER_KEY,
              'units': 'metric',
              'lang': 'ru'}
    response = requests.get(link, params=params)
    if response:
        send_weather_info(message, response.json())
    else:
        bot.send_message(message.chat.id, 'Такого города не существует, попробуйте снова!', reply_markup=markup)


def send_weather_info(message, data: dict):
    city = data['name']
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

    w_id = data['weather'][0]['id']
    image = 'thunderstorm.jpg' if w_id < 300 else 'rain.jpg' if w_id < 600 else 'snow.jpg' if w_id < 700 \
        else 'clear-sky.jpg' if w_id == 800 else 'cloud.jpg'
    with open(f'./images/{image}', 'rb') as file:
        bot.send_photo(message.chat.id, file, reply_markup=markup)


bot.infinity_polling()
