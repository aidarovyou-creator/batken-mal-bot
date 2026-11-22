import telebot, json, os, requests
from flask import Flask
import threading

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8115276999

ANIMALS = ["🐑 Кой", "🐄 Уй", "🐎 Ат", "🐐 Эчки", "🐔 Тоок", "🐫 Төө", "🐖 Чочко", "🐶 Ит", "🐱 Мышык"]
FEEDS = ["🌾 Чөп", "🌾 Арпа", "🌾 Буудай", "🌾 Жүгөрү", "🥕 Жем", "🧂 Туз", "📦 Комбикорм", "📦 Башка"]

users = {}

def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"mal": [], "feed": [], "users": [], "prices": {"Кой": "12000", "Уй": "80000", "Ат": "150000", "Эчки": "8000", "Эт 1кг": "550", "Чөп 1 тюк": "350"}}

def save_data(data):
    try:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

def bottom_kb():
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add("🐑 Мал сатуу")
    m.add("🔍 Мал издөө")
    m.add("🌾 Жем сатуу")
    m.add("💰 Бүгүнкү баалар")
    m.add("🏠 Башкы меню")
    m.add("🔙 Артка")
    return m

def main_inline():
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    m.add(telebot.types.InlineKeyboardButton("🐑 Мал сатуу", callback_data="sell_mal"))
    m.add(telebot.types.InlineKeyboardButton("🔍 Мал издөө", callback_data="search_mal"))
    m.add(telebot.types.InlineKeyboardButton("🌾 Жем сатуу", callback_data="sell_feed"))
    m.add(telebot.types.InlineKeyboardButton("🌾 Жем издөө", callback_data="search_feed"))
    m.add(telebot.types.InlineKeyboardButton("💰 Бүгүнкү баалар", callback_data="prices"))
    m.add(telebot.types.InlineKeyboardButton("🗑 Менин жарыяларым", callback_data="my"))
    m.add(telebot.types.InlineKeyboardButton("🏠 Башкы меню", callback_data="home"))
    return m

def animals_kb(prefix):
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    for a in ANIMALS:
        m.add(telebot.types.InlineKeyboardButton(a, callback_data=f"{prefix}_{a}"))
    m.add(telebot.types.InlineKeyboardButton("🔙 Артка", callback_data="home"))
    m.add(telebot.types.InlineKeyboardButton("🏠 Башкы меню", callback_data="home"))
    return m

def feeds_kb(prefix):
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    for f in FEEDS:
        m.add(telebot.types.InlineKeyboardButton(f, callback_data=f"{prefix}_{f}"))
    m.add(telebot.types.InlineKeyboardButton("🔙 Артка", callback_data="home"))
    m.add(telebot.types.InlineKeyboardButton("🏠 Башкы меню", callback_data="home"))
    return m

def nav_kb():
    m = telebot.types.InlineKeyboardMarkup(row_width=1)
    m.add(telebot.types.InlineKeyboardButton("🔙 Артка", callback_data="home"))
    m.add(telebot.types.InlineKeyboardButton("🏠 Башкы меню", callback_data="home"))
    return m

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    users.pop(chat_id, None)
    d = load_data()
    all_users = d.get("users", [])
    if chat_id not in [u["id"] for u in all_users]:
        all_users.append({"id": chat_id, "name": message.from_user.first_name, "username": message.from_user.username})
        d["users"] = all_users
        save_data(d)
    bot.send_message(chat_id, "👋 <b>Салам! Мен - Баткен Мал Чарба Ботумун!</b>\n\n🐑 Мал сат, сатып ал\n🌾 Жем сат\n💰 Бүгүнкү бааны бил\n\nАстындагы кнопкалардан танда 👇\nБаткен үчүн! 🇰🇬", reply_markup=bottom_kb(), parse_mode="HTML")
    bot.send_message(chat_id, "Танда 👇", reply_markup=main_inline())

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id != ADMIN_ID:
        return
    d = load_data()
    bot.send_message(message.chat.id, f"📊 <b>СТАТИСТИКА</b>\n\n👥 Адам: {len(d.get('users', []))}\n🐑 Мал жарыя: {len(d.get('mal', []))}\n🌾 Жем жарыя: {len(d.get('feed', []))}", parse_mode="HTML", reply_markup=bottom_kb())

@bot.message_handler(func=lambda m: m.text in ["🐑 Мал сатуу", "🔍 Мал издөө", "🌾 Жем сатуу", "🌾 Жем издөө", "💰 Бүгүнкү баалар", "🏠 Башкы меню", "🔙 Артка"])
def bottom_buttons(message):
    chat_id = message.chat.id
    txt = message.text
    if txt in ["🏠 Башкы меню", "🔙 Артка"]:
        start(message)
        return
    if txt == "🐑 Мал сатуу":
        users[chat_id] = {"step": "mal_type"}
        bot.send_message(chat_id, "🐑 <b>Кайсы малды сатасың?</b>\n\nБирөөнү бас 👇", reply_markup=animals_kb("sellmal"), parse_mode="HTML")
        return
    if txt == "🔍 Мал издөө":
        users[chat_id] = {"step": "search_mal_type"}
        bot.send_message(chat_id, "🔍 <b>Кайсы малды издейсиң?</b>", reply_markup=animals_kb("searchmal"), parse_mode="HTML")
        return
    if txt == "🌾 Жем сатуу":
        users[chat_id] = {"step": "feed_type"}
        bot.send_message(chat_id, "🌾 <b>Кайсы жемди сатасың?</b>", reply_markup=feeds_kb("sellfeed"), parse_mode="HTML")
        return
    if txt == "🌾 Жем издөө":
        users[chat_id] = {"step": "search_feed_type"}
        bot.send_message(chat_id, "🌾 <b>Кайсы жемди издейсиң?</b>", reply_markup=feeds_kb("searchfeed"), parse_mode="HTML")
        return
    if txt == "💰 Бүгүнкү баалар":
        d = load_data()
        prices = d.get("prices", {})
        text = "💰 <b>БҮГҮНКҮ БААЛАР - Баткен</b>\n\n"
        for k, v in prices.items():
            text += f"• {k}: <b>{v} сом</b>\n"
        bot.send_message(chat_id, text, reply_markup=bottom_kb(), parse_mode="HTML")
        return

@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)
    if data == "home":
        users.pop(chat_id, None)
        bot.edit_message_text("🏠 <b>Башкы меню</b>\n\nТанда 👇", chat_id, call.message.message_id, reply_markup=main_inline(), parse_mode="HTML")
        return
    if data == "sell_mal":
        users[chat_id] = {"step": "mal_type"}
        bot.edit_message_text("🐑 <b>Кайсы малды сатасың?</b>", chat_id, call.message.message_id, reply_markup=animals_kb("sellmal"), parse_mode="HTML")
        return
    if data == "search_mal":
        users[chat_id] = {"step": "search_mal_type"}
        bot.edit_message_text("🔍 <b>Кайсы малды издейсиң?</b>", chat_id, call.message.message_id, reply_markup=animals_kb("searchmal"), parse_mode="HTML")
        return
    if data == "sell_feed":
        users[chat_id] = {"step": "feed_type"}
        bot.edit_message_text("🌾 <b>Кайсы жемди сатасың?</b>", chat_id, call.message.message_id, reply_markup=feeds_kb("sellfeed"), parse_mode="HTML")
        return
    if data == "search_feed":
        users[chat_id] = {"step": "search_feed_type"}
        bot.edit_message_text("🌾 <b>Кайсы жемди издейсиң?</b>", chat_id, call.message.message_id, reply_markup=feeds_kb("searchfeed"), parse_mode="HTML")
        return
    if data == "prices":
        d = load_data()
        prices = d.get("prices", {})
        text = "💰 <b>БҮГҮНКҮ БААЛАР - Баткен</b>\n\n"
        for k, v in prices.items():
            text += f"• {k}: <b>{v} сом</b>\n"
        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=nav_kb(), parse_mode="HTML")
        return
    if data == "my":
        d = load_data()
        my_mal = [v for v in d.get("mal", []) if v["user_id"] == chat_id]
        my_feed = [v for v in d.get("feed", []) if v["user_id"] == chat_id]
        if not my_mal and not my_feed:
            bot.edit_message_text("😔 Сенин азырынча жарыяң жок.", chat_id, call.message.message_id, reply_markup=nav_kb())
            return
        text = "🗑 <b>Сенин жарыяларың:</b>\n\n"
        for v in my_mal:
            text += f"🐑 {v['type']} - {v['price']} сом - {v['village']}\n"
        for v in my_feed:
            text += f"🌾 {v['type']} - {v['price']} сом - {v['village']}\n"
        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=nav_kb(), parse_mode="HTML")
        return
    if data.startswith("sellmal_"):
        typ = data.replace("sellmal_", "")
        users[chat_id] = {"step": "mal_price", "type": typ, "kind": "mal"}
        bot.send_message(chat_id, f"🐑 {typ}\n\n💰 <b>Баасы канча сом?</b>\nМисалы: 15000", parse_mode="HTML", reply_markup=bottom_kb())
        return
    if data.startswith("searchmal_"):
        typ = data.replace("searchmal_", "")
        d = load_data()
        found = [v for v in d.get("mal", []) if v["type"] == typ]
        if not found:
            bot.edit_message_text(f"😔 {typ} боюнча азырынча жарыя жок.", chat_id, call.message.message_id, reply_markup=nav_kb())
            return
        bot.edit_message_text(f"✅ {typ} боюнча {len(found)} жарыя табылды 👇", chat_id, call.message.message_id, reply_markup=nav_kb())
        for v in found:
            bot.send_message(chat_id, f"🐑 <b>{v['type']}</b>\n\n💰 Баасы: <b>{v['price']} сом</b>\n📍 Айыл: {v['village']}\n📝 {v['desc']}\n📞 Байланыш: <code>{v['phone']}</code>", parse_mode="HTML", reply_markup=bottom_kb())
        users.pop(chat_id, None)
        return
    if data.startswith("sellfeed_"):
        typ = data.replace("sellfeed_", "")
        users[chat_id] = {"step": "feed_price", "type": typ, "kind": "feed"}
        bot.send_message(chat_id, f"🌾 {typ}\n\n💰 <b>Баасы канча сом?</b>", parse_mode="HTML", reply_markup=bottom_kb())
        return
    if data.startswith("searchfeed_"):
        typ = data.replace("searchfeed_", "")
        d = load_data()
        found = [v for v in d.get("feed", []) if v["type"] == typ]
        if not found:
            bot.edit_message_text(f"😔 {typ} боюнча азырынча жарыя жок.", chat_id, call.message.message_id, reply_markup=nav_kb())
            return
        bot.edit_message_text(f"✅ {typ} боюнча {len(found)} жарыя табылды 👇", chat_id, call.message.message_id, reply_markup=nav_kb())
        for v in found:
            bot.send_message(chat_id, f"🌾 <b>{v['type']}</b>\n\n💰 Баасы: <b>{v['price']} сом</b>\n📍 Айыл: {v['village']}\n📝 {v['desc']}\n📞 Байланыш: <code>{v['phone']}</code>", parse_mode="HTML", reply_markup=bottom_kb())
        users.pop(chat_id, None)
        return

@bot.message_handler(func=lambda m: True)
def texts(message):
    chat_id = message.chat.id
    st = users.get(chat_id)
    if not st:
        bot.send_message(chat_id, "Астындагы кнопкадан танда 👇", reply_markup=bottom_kb())
        return
    step = st.get("step")
    txt = message.text or ""
    if step == "mal_price":
        st["price"] = txt
        st["step"] = "mal_village"
        bot.send_message(chat_id, "📍 <b>Кайсы айылда?</b>\nМисалы: Самаркандек, Исфана, Баткен", parse_mode="HTML", reply_markup=bottom_kb())
        return
    if step == "feed_price":
        st["price"] = txt
        st["step"] = "feed_village"
        bot.send_message(chat_id, "📍 <b>Кайсы айылда?</b>", parse_mode="HTML", reply_markup=bottom_kb())
        return
    if step == "mal_village":
        st["village"] = txt
        st["step"] = "mal_phone"
        bot.send_message(chat_id, "📞 <b>Телефонуңду жаз:</b>", parse_mode="HTML", reply_markup=bottom_kb())
        return
    if step == "feed_village":
        st["village"] = txt
        st["step"] = "feed_phone"
        bot.send_message(chat_id, "📞 <b>Телефонуңду жаз:</b>", parse_mode="HTML", reply_markup=bottom_kb())
        return
    if step == "mal_phone":
        st["phone"] = txt
        st["step"] = "mal_desc"
        bot.send_message(chat_id, "📝 <b>Мал жөнүндө кыскача жаз:</b>\nМисалы: 2 жашта, семиз, эмделген", parse_mode="HTML", reply_markup=bottom_kb())
        return
    if step == "feed_phone":
        st["phone"] = txt
        st["step"] = "feed_desc"
        bot.send_message(chat_id, "📝 <b>Жем жөнүндө жаз:</b>\nМисалы: 100 тюк бар, жеткирип берем", parse_mode="HTML", reply_markup=bottom_kb())
        return
    if step == "mal_desc":
        d = load_data()
        new_v = {"user_id": chat_id, "type": st["type"], "price": st["price"], "village": st["village"], "phone": st["phone"], "desc": txt}
        d["mal"].append(new_v)
        save_data(d)
        users.pop(chat_id, None)
        bot.send_message(chat_id, "✅ <b>Мал жарыяланды!</b>\n\nЭми башкалар көрө алат.", reply_markup=bottom_kb(), parse_mode="HTML")
        bot.send_message(chat_id, "Танда 👇", reply_markup=main_inline())
        return
    if step == "feed_desc":
        d = load_data()
        new_v = {"user_id": chat_id, "type": st["type"], "price": st["price"], "village": st["village"], "phone": st["phone"], "desc": txt}
        d["feed"].append(new_v)
        save_data(d)
        users.pop(chat_id, None)
        bot.send_message(chat_id, "✅ <b>Жем жарыяланды!</b>", reply_markup=bottom_kb(), parse_mode="HTML")
        bot.send_message(chat_id, "Танда 👇", reply_markup=main_inline())
        return

app = Flask(__name__)
@app.route('/')
def home():
    return "Mal Bot ishтеп жатат!"

def run_bot():
    print("Мал бот иштеп жатат...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
