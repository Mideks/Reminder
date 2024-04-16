from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
import asyncio
import requests
from os import getenv
import logging
import sys


# код работает но его нужно связать с основной частью
TOKEN = getenv("BOT_TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer('Привет. Чтобы получить покоду, укажи название города:')

@dp.message(F.text)
async def get_weather(message: types.Message):
    city = message.text
    url= f'http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&units=metric&appid=наш_токен'
    weather_data = requests.get(url).json()
    temperature=weather_data['main']['temp']
    temperature_feels=weather_data['main']['feels_like']
    wind_speed=weather_data['wind']['speed']
    cloud_cover=weather_data['weather'][0]['description']
    humiditi=weather_data['main']['humidity']


    await message.answer(f'Температура воздуха: {temperature}\n'
                         f'Ощущается как:{temperature_feels}\n'
                         f'Скорость ветра:{wind_speed} м/с\n'
                         f'Облачность: {cloud_cover}\n'
                         f'Влажность: {humiditi}%S')


async def main():
    #await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
