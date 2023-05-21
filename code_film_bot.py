from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

with open('ideas_for_bot') as file:
    bot_token: str = file.readline().strip()

api_ur: str = 'https://api.telegram.org/bot'
bot: Bot = Bot(bot_token)
dp: Dispatcher = Dispatcher(token=bot)
code_dict: dict = {
    '001': 'Чёрный лотос',
    '002': 'Человек-паук'
}


@dp.message(Command(commands=['start']))
async def process_start(message: Message):
    await message.answer('Лучшие кинофильмы здесь. Введите код, и я пришлю Вам название кинофильма')


@dp.message(Command(commands=['help']))
async def process_help(message: Message):
    await message.answer('Введите код, и я пришлю Вам название кинофильма')


@dp.message()
async def send_message(message: Message):
    print(message.text)
    if message.text not in code_dict:
        await message.answer('Я не знаю такой команды, введите, пожалуйста, код')
    else:
        await message.answer(f'Название фильма: {code_dict[message.text]}')


if __name__ == '__main__':
    dp.run_polling(bot)
