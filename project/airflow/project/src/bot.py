# bot.py
import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# -----------------------
# Config
# -----------------------
# Лучше хранить токен в переменной окружения.
# Если переменная окружения не задана, будет использован встроенный токен (замени при необходимости).
TOKEN = os.environ.get(
    "TELEGRAM_BOT_TOKEN",
    "8410984726:AAHlUg4lsa85c9Zc_-rRFFNBz-JAth_MTMQ"
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# -----------------------
# Sample data (in-memory)
# -----------------------
# Простейший каталог — можно потом перенести в БД.
CATALOG = [
    {
        "id": 1,
        "name": "Red Party Dress",
        "category": "dresses",
        "color": "red",
        "price": "19990 KZT",
        "photo": "https://via.placeholder.com/400x600.png?text=Red+Dress",
        "description": "Красное платье для вечеринки",
        "available": True,
    },
    {
        "id": 2,
        "name": "Blue Casual Dress",
        "category": "dresses",
        "color": "blue",
        "price": "14990 KZT",
        "photo": "https://via.placeholder.com/400x600.png?text=Blue+Dress",
        "description": "Повседневное синее платье",
        "available": True,
    },
    {
        "id": 3,
        "name": "Black Heels",
        "category": "shoes",
        "color": "black",
        "price": "15500 KZT",
        "photo": "https://via.placeholder.com/400x300.png?text=Black+Heels",
        "description": "Чёрные туфли-лодочки",
        "available": True,
    },
    {
        "id": 4,
        "name": "Beige Handbag",
        "category": "accessories",
        "color": "beige",
        "price": "12500 KZT",
        "photo": "https://via.placeholder.com/400x300.png?text=Beige+Bag",
        "description": "Бежевая сумка-тоут",
        "available": True,
    },
    {
        "id": 5,
        "name": "White Sneakers",
        "category": "shoes",
        "color": "white",
        "price": "17990 KZT",
        "photo": "https://via.placeholder.com/400x300.png?text=White+Sneakers",
        "description": "Белые кроссовки",
        "available": True,
    },
]

# Примеры заранее подготовленных образов (looks)
LOOKS = {
    "party": [
        {"id": 1},  # Red Party Dress
        {"id": 3},  # Black Heels
        {"id": 4},  # Beige Handbag (можно заменить)
    ],
    "casual": [
        {"id": 2},  # Blue Casual Dress
        {"id": 5},  # White Sneakers
        {"id": 4},  # Beige Handbag
    ],
    "work": [
        {"id": 2},
        {"id": 3},
    ],
}

# Простые заказы (дemo)
ORDERS = {
    "1001": {"status": "Processing", "eta": "3 days", "items": [1, 4]},
    "1002": {"status": "Shipped", "eta": "1 day", "items": [2]},
}

# FAQ
FAQ = {
    "payment": "Мы принимаем карты и онлайн-оплату.",
    "return": "Возврат товара возможен в течение 14 дней при сохранении чеков и бирки.",
    "shipping": "Доставка по городу — 2-5 рабочих дней, международная — 7-14 дней.",
}


# -----------------------
# Helpers
# -----------------------
def find_by_category(category: str):
    return [p for p in CATALOG if p["category"] == category]


def find_by_color(color: str):
    return [p for p in CATALOG if p["color"] == color]


def find_by_name(name: str):
    name = name.lower()
    return [p for p in CATALOG if name in p["name"].lower()]


def get_product_by_id(pid: int):
    for p in CATALOG:
        if p["id"] == pid:
            return p
    return None


# -----------------------
# Handlers
# -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "Hello! 👋\n"
        "I am D-Mode bot. I can help you with the catalog, colors, looks and orders.\n\n"
        "Use /catalog - see catalogue\n"
        "Use /categories - see categories\n"
        "Use /search <name> - find product by name\n"
        "Use /color - choose color\n"
        "Use /look - choose an outfit (party, casual, work)\n"
        "Use /order <order_id> - check order status\n"
        "Use /faq - common questions\n"
    )
    await update.message.reply_text(txt)


async def catalog_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Show first N products (simple)
    media = []
    for p in CATALOG[:6]:
        caption = f"{p['name']}\nCategory: {p['category']}\nColor: {p['color']}\nPrice: {p['price']}"
        # We'll send as separate messages with photo
        await update.message.reply_photo(photo=p["photo"], caption=caption)
    if not CATALOG:
        await update.message.reply_text("Catalog is empty.")


async def categories_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("Dresses", callback_data="cat:dresses")],
        [InlineKeyboardButton("Shoes", callback_data="cat:shoes")],
        [InlineKeyboardButton("Accessories", callback_data="cat:accessories")],
    ]
    await update.message.reply_text("Choose a category:", reply_markup=InlineKeyboardMarkup(kb))


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # like 'cat:dresses'
    _, cat = data.split(":", 1)
    products = find_by_category(cat)
    if not products:
        await query.edit_message_text(f"No items in category: {cat}")
        return

    # Send products in category
    for p in products:
        caption = f"{p['name']}\nColor: {p['color']}\nPrice: {p['price']}\n{p['description']}"
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=p["photo"], caption=caption)
    await query.edit_message_text(f"Shown {len(products)} items in {cat}.")


async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Please type product name after /search. Example: /search red dress")
        return
    name = " ".join(args)
    results = find_by_name(name)
    if not results:
        await update.message.reply_text("No products found.")
        return
    for p in results:
        caption = f"{p['name']}\nCategory: {p['category']}\nColor: {p['color']}\nPrice: {p['price']}"
        await update.message.reply_photo(photo=p["photo"], caption=caption)


async def color_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Show color buttons
    colors = ["red", "blue", "black", "white", "beige"]
    kb = [[InlineKeyboardButton(c.capitalize(), callback_data=f"color:{c}") for c in colors[:3]],
          [InlineKeyboardButton(c.capitalize(), callback_data=f"color:{c}") for c in colors[3:]]]
    await update.message.reply_text("Choose a color:", reply_markup=InlineKeyboardMarkup(kb))


async def color_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, color = query.data.split(":", 1)
    products = find_by_color(color)
    if not products:
        await query.edit_message_text(f"No products in color: {color}")
        return
    for p in products:
        caption = f"{p['name']}\nCategory: {p['category']}\nPrice: {p['price']}"
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=p["photo"], caption=caption)
    await query.edit_message_text(f"Shown items with color: {color}")


async def look_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("Party 🎉", callback_data="look:party")],
        [InlineKeyboardButton("Casual 🚶‍♀️", callback_data="look:casual")],
        [InlineKeyboardButton("Work 💼", callback_data="look:work")],
    ]
    await update.message.reply_text("Choose look type:", reply_markup=InlineKeyboardMarkup(kb))


async def look_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, look_type = query.data.split(":", 1)
    if look_type not in LOOKS:
        await query.edit_message_text("Look not found.")
        return
    product_entries = LOOKS[look_type]
    # Send the look as list + photos
    await query.edit_message_text(f"Look: {look_type.capitalize()}")
    media = []
    for entry in product_entries:
        product = get_product_by_id(entry["id"])
        if product:
            caption = f"{product['name']}\n{product['price']}"
            await context.bot.send_photo(chat_id=query.message.chat_id, photo=product["photo"], caption=caption)
    await context.bot.send_message(chat_id=query.message.chat_id, text="This is a ready outfit. You can order items from the catalog.")


async def order_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Please send order id. Example: /order 1001")
        return
    order_id = args[0]
    order = ORDERS.get(order_id)
    if not order:
        await update.message.reply_text("Order not found.")
        return
    items_txt = []
    for i in order["items"]:
        p = get_product_by_id(i)
        if p:
            items_txt.append(f"- {p['name']} ({p['price']})")
    text = f"Order {order_id}\nStatus: {order['status']}\nETA: {order['eta']}\nItems:\n" + "\n".join(items_txt)
    await update.message.reply_text(text)


async def faq_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("Payment", callback_data="faq:payment")],
        [InlineKeyboardButton("Return", callback_data="faq:return")],
        [InlineKeyboardButton("Shipping", callback_data="faq:shipping")],
    ]
    await update.message.reply_text("Choose question:", reply_markup=InlineKeyboardMarkup(kb))


async def faq_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, key = query.data.split(":", 1)
    answer = FAQ.get(key, "Answer not found.")
    await query.edit_message_text(answer)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Пока реализуем простой ответ: поиск по фото не реализован в демо.
    Можно интегрировать сервисы распознавания изображений или ML позже.
    """
    await update.message.reply_text(
        "Thanks for the photo! 🔍\n"
        "Photo search is not implemented in this demo.\n"
        "Please send product name with /search command."
    )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Простая обработка входящего текста (fallback).
    text = update.message.text.lower()
    if text in ["hi", "hello", "привет", "hey"]:
        await update.message.reply_text("Hello! You can use /catalog or /help.")
        return
    # If user sends just a word that matches color, show color results
    colors = {"red", "blue", "black", "white", "beige"}
    if text in colors:
        products = find_by_color(text)
        if products:
            for p in products:
                caption = f"{p['name']}\n{p['price']}"
                await update.message.reply_photo(photo=p["photo"], caption=caption)
            return
    # Otherwise suggest commands
    await update.message.reply_text(
        "I don't understand. Try these commands:\n"
        "/catalog /categories /search /color /look /order /faq"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    # Notify user
    try:
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text("Sorry, an error occurred. Please try again later.")
    except Exception as e:
        logger.error("Failed to send error message: %s", e)


# -----------------------
# Main
# -----------------------
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("catalog", catalog_cmd))
    app.add_handler(CommandHandler("categories", categories_cmd))
    app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(CommandHandler("color", color_cmd))
    app.add_handler(CommandHandler("look", look_cmd))
    app.add_handler(CommandHandler("order", order_cmd))
    app.add_handler(CommandHandler("faq", faq_cmd))

    # CallbackQuery (for buttons)
    app.add_handler(CallbackQueryHandler(category_callback, pattern=r"^cat:"))
    app.add_handler(CallbackQueryHandler(color_callback, pattern=r"^color:"))
    app.add_handler(CallbackQueryHandler(look_callback, pattern=r"^look:"))
    app.add_handler(CallbackQueryHandler(faq_callback, pattern=r"^faq:"))

    # Messages: photos and text
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # Error handler
    app.add_error_handler(error_handler)

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
