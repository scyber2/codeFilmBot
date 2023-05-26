import asyncio
import psycopg2
from PostgreSQL import host, user, password, db_name
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

with open('ideas_for_bot') as token:
    bot_token: str = token.readline().strip()

bot: Bot = Bot(bot_token)
dp: Dispatcher = Dispatcher(token=bot)

conn = psycopg2.connect(
    host=host,
    database=db_name,
    user=user,
    password=password
)
cursor = conn.cursor()


async def check_sub(user_id):
    res = await bot.get_chat_member(-1001868182096, user_id)
    print(res.status)
    if res.status != 'left':
        return True
    return False


async def fetch_movie_info(code):
    query = "SELECT title, description, rating FROM codes WHERE code = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    if result:
        title, description, rating = result
        return f"Информация о фильме\n\nНазвание: {title}\n\nОписание: {description}\n\nРейтинг: {rating}"
    return False


async def send_inline_button(message: Message):
    channel_button: InlineKeyboardButton = InlineKeyboardButton(text="Ссылка на канал", url="https://t.me/Kino_Hub_Studio")
    inline_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[channel_button]])
    await message.answer("Чтобы пользоваться ботом, подпишитесь, пожалуйста, на канал, нажав на кнопку ниже",
                         reply_markup=inline_keyboard)


@dp.message(Command(commands=['start']))
async def process_start(message: Message):
    await message.answer('Здравствуйте! Я - бот code film. Вы можете прислать мне существующий код фильма, '
                         'а я дам Вам его название')
    if not(await check_sub(message.from_user.id)):
        await asyncio.sleep(1)
        await send_inline_button(message)


@dp.message()
async def send_message(message: Message):
    print(message.text)
    if await check_sub(message.from_user.id):
        code: str = message.text.strip()
        res: str | bool = await fetch_movie_info(code)
        if res:
            await message.answer(res)
        else:
            await message.answer('Введите, пожалуйства, сущетсвующий код или команду')
    else:
        await send_inline_button(message)


if __name__ == '__main__':
    dp.run_polling(bot)

cursor.close()
conn.close()
