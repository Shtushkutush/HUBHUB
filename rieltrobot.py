
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from collections import deque

TOKEN = '7650248275:AAENraZscm76SYS0gMiF0bBDFEgAQHW3O0g'
MANAGERS = deque(["AlexPisr", "Sergey_Likhutin", "ledi_rieltor"])  # Менеджеры
ADMIN = '47588188'  # Администратор

bot = Bot(token=TOKEN)
dp = Dispatcher()

questions = [
    {"question": "Скольки комнатная квартира вам нужна?", "answers": ["1-комнатная", "2-комнатная", "3-комнатная", "4-комнатная и больше"]},
    {"question": "В каком районе вы ищете квартиру?", "answers": ["Авиастроительный", "Вахитовский", "Кировский", "Московский", "Ново-Савиновский", "Приволжский", "Советский", "Пригород"]},
    {"question": "Форма оплаты", "answers": ["За наличку", "За семейную ипотеку", "За айти ипотеку", "За субсидированную ставку", "В рассрочку"]},
    {"question": "Есть ли первоначальный взнос?", "answers": ["Есть", "Частично", "Нужны варианты без ПВ"]},
    {"question": "В пределах какой суммы ищете?", "answers": ["До 6 млн", "До 8 млн", "До 10 млн", "До 15 млн", "От 15 и больше"]},
    {"question": "Срок сдачи важен?", "answers": ["Надо в сданном", "Чем раньше, тем лучше", "Могу подождать, если так выгоднее"]},
    {"question": "Если нет квартир, предлагать ли частные дома?", "answers": ["Да", "Нет"]},
    {"question": "Цель покупки квартиры:", "answers": ["Для перепродажи", "Для жизни", "Для сдачи в аренду", "Для детей", "У меня хитрый план"]},
]

user_data = {}


async def start_conversation(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"answers": [], "current_question": 0}
    await message.answer("Здравствуйте! Я бот-риэлтор и я помогу вам подобрать квартиру! Просто ответьте на ряд вопросов (можно выбирать несколько ответов) и я вам скину подборку наиболее подходящих для вас вариантов!")
    await send_question(user_id)

from aiogram.filters import Command

dp.message.register(start_conversation, Command(commands=['start']))

async def send_question(user_id):
    data = user_data[user_id]
    question_index = data["current_question"]

    if question_index >= len(questions):
        await bot.send_message(user_id, "Спасибо за ответы! Сейчас начну работу по подбору! Вам напишу или я, или если не справлюсь - мои живые коллеги. Буду рад оказаться полезным! \n\nКстати! Порекомендуйте меня своим знакомым! Плачу 100 баксов за каждого, кто купит квартиру, обратившись ко мне по вашей наводке!")
        await send_to_manager(user_id)
        return

    question = questions[question_index]
    markup = InlineKeyboardMarkup(inline_keyboard=[])

    for answer in question["answers"]:
        markup.inline_keyboard.append([InlineKeyboardButton(text=answer, callback_data=f"ans_{question_index}_{question['answers'].index(answer)}")])

    markup.inline_keyboard.append([InlineKeyboardButton(text="✅ Дальше", callback_data=f"nxt_{question_index}")])
    markup.inline_keyboard.append([InlineKeyboardButton(text="❌ Пропустить", callback_data=f"skp_{question_index}")])

    await bot.send_message(user_id, question["question"], reply_markup=markup)


async def handle_answer(call: types.CallbackQuery):
    user_id = call.from_user.id
    _, question_index, answer_index = call.data.split("_", 2)
    question_index = int(question_index)
    answer_index = int(answer_index)
    answer_text = questions[question_index]["answers"][answer_index]
    question_index = int(question_index)

    user_data[user_id]["answers"].append((questions[question_index]["question"], answer_text))
    await call.answer("Ответ сохранен!")

dp.callback_query.register(handle_answer, lambda call: call.data.startswith("ans_"))


async def handle_next(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data[user_id]["current_question"] += 1
    await send_question(user_id)
    await call.answer()

dp.callback_query.register(handle_next, lambda call: call.data.startswith("nxt_"))


async def handle_skip(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data[user_id]["current_question"] += 1
    await send_question(user_id)
    await call.answer()

dp.callback_query.register(handle_skip, lambda call: call.data.startswith("skp_"))

async def send_to_manager(user_id):
    answers = user_data[user_id]["answers"]
    username = (await bot.get_chat(user_id)).username
    message_text = f"Ответы от @{username}:\n"
    message_text += "\n".join([f"{q}: {a}" for q, a in answers])

    manager = MANAGERS.popleft()
    if not isinstance(manager, (int, str)):
        await bot.send_message(ADMIN, f"Некорректный идентификатор менеджера: {manager}")
        return
    MANAGERS.append(manager)

    try:
                await bot.send_message(manager, message_text)
    except Exception as e:
        await bot.send_message(ADMIN, f"Ошибка отправки сообщения менеджеру {manager}: {str(e)}")
    except Exception as e:
        await bot.send_message(ADMIN, f"Ошибка отправки сообщения менеджеру @{manager}: {str(e)}")
    await bot.send_message(ADMIN, f"Ответы от @{username} направлены менеджеру @{manager}:\n{message_text}")

import asyncio

if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
