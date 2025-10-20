from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

import datetime

import os
from dotenv import load_dotenv

from db import admin_add_pairs, add_attender, get_pairs

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


load_dotenv()
TOKEN = os.getenv('TG_BOT_TOKEN')
THE_ID = os.getenv('ADMIN_ID')
bot = Bot(token=TOKEN)
dp = Dispatcher()


class Form(StatesGroup):
    waiting_for_input = State()
    waiting_for_att = State()
    waiting_for_name = State()


@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("Хэй! Как тебя зовут?")
    await state.set_state(Form.waiting_for_name)


@dp.message(Form.waiting_for_name)
async def get_name(message: types.Message, state: FSMContext):
    user_name = message.text.strip()
    await state.update_data(name=user_name)  # сохранение имение
    await message.answer(f"Найс ту мит ю, {user_name}")
    await state.reset_state(with_data=False)  


@dp.message(Command("my_name"))
async def add_the_pair(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    if name:
        await message.answer(f"Снова здарова, {name}!")
    else:
        await message.answer("Я тебя пока не знаю. Напиши /start, чтобы я тебя запомнил.")


@dp.message(Command("add_pair"))
async def add_the_pair(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id == int(THE_ID):        # админский айдишник
        sent = await message.answer("Введи пары через пробел")
        await state.update_data(reply_to_id=sent.message_id)
        await state.set_state(Form.waiting_for_input)
    else:
        await message.answer("Кретин.")


@dp.message()
async def handle_reply(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    msg_text = message.text
    user_pairs = list(set(msg_text.strip().split()))
    already_in = []
    for el in get_pairs():
        if el in user_pairs:
            already_in.append(el)
    if current_state == Form.waiting_for_input:
        if not (already_in):
            admin_add_pairs(user_pairs)
            await message.answer("Добавил", reply_to_message_id=message.message_id)
        else:
            for el in already_in:
                user_pairs.remove(el)
            admin_add_pairs(user_pairs)
            await message.answer(f"Не добавлял {', '.join(already_in)}, потому что уже есть, остальные (если остались) занёс", reply_to_message_id=message.message_id)
        await state.clear()


@dp.message(Command("attend"))
async def add_the_pair(message: types.Message, state: FSMContext):
    sent = await message.answer(f"Выбери пару, на которой присутствуешь сегодня ({datetime.datetime.now()})")
    await state.update_data(reply_to_id=sent.message_id)
    await state.set_state(Form.waiting_for_att)


@dp.message()
async def handle_reply(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    msg_text = message.text
    if current_state == Form.waiting_for_att:
        add_attender()
        await state.clear()


async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
