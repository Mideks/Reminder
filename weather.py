# from aiogram import Bot, Dispatcher, types, F
# from aiogram.filters.command import Command
# import asyncio
# import requests
#
# TOKEN ='7092825221:AAHuCHpYJ990hCvLuoGf4x19tPGh71el4LQ'
# bot = Bot(TOKEN)
# dp = Dispatcher()
#
# @dp.message(Command('!Погода'))
# async def start_command(message: types.Message):
#     await message.answer('Привет. Чтобы получить покоду, укажи название города:')
#
# @dp.message(F.text)
# async def get_weather(message: types.Message, weather_data=None):
#     city = message.text
#     try:
#         url=f'https://api.openweathermap/org/data/3/weather?g={city}&unitc&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
#         weather_data = requests.get(url).json()
#         temperature=weather_data['main']['temp']
#         temperature_feels=weather_data['main']['feels_like']
#         wind_speed=weather_data['wind']['speed']
#         cloud_cover=weather_data['weather'][0['description']
#         humiditi=weather_data['main']['humidity']
#         await message.answer(f'Температура воздуха: {temperature}\n'
#                              f'Ощущается как:{temperature_feels}\n'
#                              f'Скорость ветра:{wind_speed} м/с\n'
#                              f'Облачность: {cloud_cover}\n'
#                              f'Влажность: {humiditi}%S')
#
#     except KeyError:
#         await message.answer(f'Не удалось определить город: {city}')
#
#
#
#
# async def main():
#     await bot.delete_webhook(drop_pending_updates=True)
#     await dp.start_polling(bot)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())