import psycopg2
import datetime
from PostgreSQL import host, user, password, db_name
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, Text
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

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
    if res.status != 'left':
        return True
    return False


async def fetch_movie_info(message: Message):
    code: str = message.text.replace('/', '').strip()
    query = "SELECT title, description, rating, show_link FROM codes WHERE code = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    if result:
        title, description, rating, show_link = result
        show_button: InlineKeyboardButton = InlineKeyboardButton(text='Посмотреть фильм', url=f'{show_link}')
        keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[show_button]])
        await message.answer(f"Вот! Нашёл! Держи инфу!\n\nНазвание: {title}\n\nОписание: {description}\n\n"
                             f"Рейтинг: {rating}", reply_markup=keyboard)
        return True
    return False


async def send_inline_button(message: Message):
    channel_button: InlineKeyboardButton = InlineKeyboardButton(text="Подписаться на канал",
                                                                url="https://t.me/Kino_Hub_Studio")
    check_button: InlineKeyboardButton = InlineKeyboardButton(text=" ✅ Проверить подписку",
                                                              callback_data='check')
    inline_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[channel_button],
                                                                                  [check_button]])
    await message.answer("Не так быстро! Сначала подпишись на наш тг канал и кайфуй с просмотром нового фильма)",
                         reply_markup=inline_keyboard)
    await message.answer('После подписки нажми на ✅ Проверить подписку и эта кнопка чекнет, правда ли ты '
                         'подписался). Если при нажатии ничего не произошло-ты хотел смухлевать, та не вышло)')


@dp.callback_query(Text(text='check'))
async def process_check_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await check_sub(user_id):
        message_id = callback.message.message_id
        messages_ids = [message_id+1, message_id]
        for m_i in messages_ids:
            await bot.delete_message(chat_id=user_id, message_id=m_i)
        await callback.message.answer('Благодарю за подписку, однако, тепепрь, ты не сможешь выйти из '
                                      'этого тг канала))) если кнш не хочешь допустить той ситуации, когда не можешь '
                                      'подобрать сериальчик или фильмец под хавчик)) Выбор за тобой, друг мой!')
    else:
        await callback.answer()


@dp.message(Command(commands=['start']))
async def process_start(message: Message):
    if not(await check_sub(message.from_user.id)):
        await send_inline_button(message)
    else:
        await message.answer('Здарова, бро! Предплоагаю, ты за названием фильмеца пришёл) ну чтож, заходи!')


@dp.message()
async def send_message(message: Message):
    print(f'{message.from_user.full_name} написал это сообщение: "{message.text}", {datetime.datetime.now()}')
    if await check_sub(message.from_user.id):
        res: str | bool = await fetch_movie_info(message)
        if not(res):
            await message.answer('Погодь, такой команды или кода нет, введи существующий плиз...')
    else:
        await send_inline_button(message)


if __name__ == '__main__':
    dp.run_polling(bot)

cursor.close()
conn.close()
