
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '7560908602:AAHqHUYPcpoZF7Xfu-Ef6J1yGA5_0_nx2kg'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Каталог ігрової валюти
catalog = {
    "Standoff 2": [
        {"amount": 100, "price": 40},
        {"amount": 500, "price": 200},
        {"amount": 1000, "price":400}
    ],
    "Brawl Stars": [
        {"amount": аккаунт , "price": 90},
        {"amount": аккаунт, "price": 180},
        {"amount": аккаунт, "price": 320}
    ],
    "Black Russia": [
        {"amount": 1000000, "price": 30},
        {"amount": 5000000, "price": 150},
        {"amount": 10000000, "price":300}
    ]
}


menu_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton("Повернутися до меню", callback_data="back_to_menu"))


class Order(StatesGroup):
    waiting_for_game = State()
    waiting_for_package = State()
    waiting_for_nickname = State()
    waiting_for_platform = State()
    waiting_for_contact = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    for game in catalog:
        keyboard.add(InlineKeyboardButton(game, callback_data=f"game_{game}"))
    keyboard.add(InlineKeyboardButton("Мої замовлення", callback_data="my_orders"))
    keyboard.add(InlineKeyboardButton("Відгуки та підтримка", callback_data="support"))
    await message.answer("Оберіть гру:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('game_'))
async def game_selected(callback_query: types.CallbackQuery, state: FSMContext):
    game = callback_query.data.split("_", 1)[1]
    await state.update_data(game=game)
    keyboard = InlineKeyboardMarkup()
    for i, item in enumerate(catalog[game]):
        keyboard.add(InlineKeyboardButton(f"{item['amount']} - {item['price']}₴", callback_data=f"pack_{i}"))
    await bot.send_message(callback_query.from_user.id, f"Ви обрали {game}. Виберіть пакет:", reply_markup=keyboard)
    await Order.waiting_for_package.set()

@dp.callback_query_handler(lambda c: c.data.startswith('pack_'), state=Order.waiting_for_package)
async def package_selected(callback_query: types.CallbackQuery, state: FSMContext):
    index = int(callback_query.data.split("_")[1])
    data = await state.get_data()
    game = data['game']
    package = catalog[game][index]
    await state.update_data(package=package)
    await bot.send_message(callback_query.from_user.id, "Введіть ваш нікнейм у грі:")
    await Order.waiting_for_nickname.set()

@dp.message_handler(state=Order.waiting_for_nickname)
async def nickname_entered(message: types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await message.answer("Вкажіть вашу платформу (наприклад, Android, iOS, ПК):")
    await Order.waiting_for_platform.set()

@dp.message_handler(state=Order.waiting_for_platform)
async def platform_entered(message: types.Message, state: FSMContext):
    await state.update_data(platform=message.text)
    await message.answer("Залиште контакт для зв'язку (телеграм або номер телефону):")
    await Order.waiting_for_contact.set()

@dp.message_handler(state=Order.waiting_for_contact)
async def contact_entered(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    text = (
        f"Новe замовлення!
"
        f"Гра: {data['game']}
"
        f"Пакет: {data['package']['amount']} за {data['package']['price']}₴
"
        f"Нік: {data['nickname']}
"
        f"Платформа: {data['platform']}
"
        f"Контакт: {data['contact']}"
    )
    admin_id = 8093052891 # Замінити на ID адміністратора
    await bot.send_message(admin_id, text)
    await message.answer("""
Дякуємо! Ваше замовлення прийняте.

Щоб завершити покупку, здійсніть оплату на карту:
🔹 *Монобанк*: карту взнати у @nazark100

Після оплати надішліть скріншот квитанції у відповідь на це повідомлення.
""", parse_mode="Markdown", reply_markup=menu_keyboard)
    
    # Зберігаємо замовлення у файл
    try:
        with open(r"/mnt/data/orders.json", "r", encoding="utf-8") as f:
            all_orders = json.load(f)
    except:
        all_orders = {}

    user_id = str(message.from_user.id)
    if user_id not in all_orders:
        all_orders[user_id] = []

    all_orders[user_id].append({
        "гра": data['game'],
        "пакет": f"{data['package']['amount']} за {data['package']['price']}₴",
        "нік": data['nickname'],
        "платформа": data['platform'],
        "контакт": data['contact']
    })

    with open(r"/mnt/data/orders.json", "w", encoding="utf-8") as f:
        json.dump(all_orders, f, ensure_ascii=False, indent=2)

    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "support")
async def support_callback(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Якщо у вас виникли питання або ви хочете залишити відгук — напишіть нам:
@your_support_username")



@dp.callback_query_handler(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    for game in catalog:
        keyboard.add(InlineKeyboardButton(game, callback_data=f"game_{game}"))
    keyboard.add(InlineKeyboardButton("Мої замовлення", callback_data="my_orders"))
    keyboard.add(InlineKeyboardButton("Відгуки та підтримка", callback_data="support"))
    await bot.send_message(callback_query.from_user.id, "Оберіть гру:", reply_markup=keyboard)



@dp.callback_query_handler(lambda c: c.data == "my_orders")
async def my_orders(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    try:
        with open(r"/mnt/data/orders.json", "r", encoding="utf-8") as f:
            all_orders = json.load(f)
    except:
        all_orders = {}

    orders = all_orders.get(user_id, [])
    if not orders:
        await bot.send_message(callback_query.from_user.id, "У вас ще немає замовлень.")
    else:
        text = "Ваші замовлення:\n\n"
        for i, order in enumerate(orders, 1):
            text += (
                f"#{i}\n"
                f"Гра: {order['гра']}\n"
                f"Пакет: {order['пакет']}\n"
                f"Нік: {order['нік']}\n"
                f"Платформа: {order['платформа']}\n"
                f"Контакт: {order['контакт']}\n\n"
            )
        await bot.send_message(callback_query.from_user.id, text)



@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id != 123456789:
        await message.reply("У вас немає доступу до адмін-панелі.")
        return

    try:
        with open(r"/mnt/data/orders.json", "r", encoding="utf-8") as f:
            all_orders = json.load(f)
    except:
        all_orders = {}

    if not all_orders:
        await message.reply("Немає жодного замовлення.")
        return

    text = "Усі замовлення користувачів:\n\n"
    for user_id, orders in all_orders.items():
        text += f"Користувач: {user_id}\n"
        for i, order in enumerate(orders, 1):
            text += (
                f"  #{i}\n"
                f"  Гра: {order['гра']}\n"
                f"  Пакет: {order['пакет']}\n"
                f"  Нік: {order['нік']}\n"
                f"  Платформа: {order['платформа']}\n"
                f"  Контакт: {order['контакт']}\n"
            )
        text += "\n"

    await message.reply(text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
