import threading
import time

import telebot
import schedule
from telebot import types
from dotenv import load_dotenv
import os
from binance.client import Client
import requests

load_dotenv()

BOT_TOKEN = os.getenv("BOT-TOKEN")
TAAPI_SECRET = os.getenv("TAAPI-SECRET")

bot = telebot.TeleBot(BOT_TOKEN)

API_KEY = None
API_SECRET = None
TradingState = None


@bot.message_handler(commands=["start"])  # початкова команда
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🇺🇦 Українська")
    btn2 = types.KeyboardButton("🇬🇧 English")
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, "🇺🇦 Виберіть мову / 🇬🇧 Choose your language", reply_markup=markup)


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    # Українська мова
    if message.text == "🇺🇦 Українська":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🔐 Автентифікація")
        btn2 = types.KeyboardButton("💰 Баланс")
        btn3 = types.KeyboardButton("💸 Переглянути прайс")
        btn4 = types.KeyboardButton("⚠️ Допомога")
        btn5 = types.KeyboardButton("🔙 Повернутися до вибору мови")
        btn6 = types.KeyboardButton("Start trading")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
        bot.send_message(
            message.from_user.id, "👋 Вас вітає бот для трейдингу на біржі Binance", reply_markup=markup
        )
        bot.send_message(message.from_user.id, "👀 Виберіть потрібний вам розділ")

    elif message.text == "🔙 Повернутися до вибору мови":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🇺🇦 Українська")
        btn2 = types.KeyboardButton("🇬🇧 English")
        markup.add(btn1, btn2)
        bot.send_message(
            message.from_user.id, "🇺🇦 Виберіть мову / 🇬🇧 Choose your language", reply_markup=markup
        )

    # Автентифікація
    elif message.text == "🔐 Автентифікація":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🏁 Почати Автентифікацію")
        btn2 = types.KeyboardButton("⚠️ Допомога Автентифікації")
        btn3 = types.KeyboardButton("🔙 Головне меню")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, "⬇ Виберіть розділ", reply_markup=markup)

    elif message.text == "🏁 Почати Автентифікацію":
        bot.send_message(
            message.from_user.id, "Введіть API ключ та secret ключ через кому (наприклад, API_KEY,API_SECRET)"
        )
        bot.register_next_step_handler(message, get_keys)

    # Операції з бінанс
    elif message.text == "💰 Баланс":
        if not API_KEY or not API_SECRET:
            bot.send_message(message.from_user.id, "Спочатку введіть API ключ і secret ключ.")
            return
        client = Client(API_KEY, API_SECRET)
        account_info = client.get_account()
        balance_text = ""
        for balance in account_info["balances"]:
            if float(balance["free"]) > 0:
                asset = balance["asset"]
                padding = " " * (5 - len(asset))
                balance_text += f"\n{asset}{padding}➡️ Доступно: {balance['free']} 💰\n"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("🔙 Головне меню")
        markup.add(btn)
        bot.send_message(
            message.from_user.id, f"\n{balance_text}", parse_mode="Markdown", reply_markup=markup
        )

    elif message.text == "💸 Переглянути прайс":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("🔙 Головне меню")
        markup.add(btn)
        bot.send_message(message.from_user.id, "⬇ Виберіть розділ", reply_markup=markup)

    # Операції з бінанс
    elif message.text == "⚠️ Допомога":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("🔙 Головне меню")
        markup.add(btn)
        bot.send_message(message.from_user.id, "⬇ Виберіть розділ", reply_markup=markup)

    elif message.text == "🔙 Головне меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🔐 Автентифікація")
        btn2 = types.KeyboardButton("💰 Баланс")
        btn3 = types.KeyboardButton("💸 Переглянути прайс")
        btn4 = types.KeyboardButton("⚠️ Допомога")
        btn5 = types.KeyboardButton("🔙 Повернутися до вибору мови")
        btn6 = types.KeyboardButton("Start trading")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
        bot.send_message(message.from_user.id, "👀 Виберіть потрібний вам розділ", reply_markup=markup)

    elif message.text == "Start trading":
        # schedule.every(30).seconds.do(lambda: trade(API_KEY, API_SECRET))

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("🔙 Головне меню")
        markup.add(btn)
        bot.send_message(message.from_user.id, "⬇ Виберіть розділ", reply_markup=markup)

        # while True:
        #     schedule.run_pending()
        #     time.sleep(1)

        def run_continuously(interval=1):
            cease_continuous_run = threading.Event()

            class ScheduleThread(threading.Thread):
                @classmethod
                def run(cls):
                    while not cease_continuous_run.is_set():
                        schedule.run_pending()
                        time.sleep(interval)

            continuous_thread = ScheduleThread()
            continuous_thread.start()
            return cease_continuous_run

        schedule.every(8).seconds.do(trade)

        # Start the background thread
        stop_run_continuously = run_continuously()
        #
        # # Do some other things...
        # time.sleep(10)
        #
        # # Stop the background thread
        # stop_run_continuously.set()


def get_keys(message):
    global API_KEY, API_SECRET
    keys = message.text.split(",")
    if len(keys) != 2:
        bot.send_message(
            message.from_user.id, "Введіть API ключ та secret ключ через кому (наприклад, API_KEY,API_SECRET)"
        )
        bot.register_next_step_handler(message, get_keys)
    else:
        API_KEY, API_SECRET = keys
        bot.send_message(message.from_user.id, "Автентифікація пройдена успішно!✅")


def trade():
    try:
        global API_KEY, API_SECRET
        ema9 = getTapiData("SOL/USDT", "1m", 2, 9)
        ema20 = getTapiData("SOL/USDT", "1m", 2, 20)
        client = Client(API_KEY, API_SECRET)
        e = 0.0005
        last_ema9 = ema9[0]["value"]
        prev_ema9 = ema9[1]["value"]
        last_ema20 = ema20[0]["value"]
        prev_ema20 = ema20[1]["value"]
        if prev_ema9 < prev_ema20 +prev_ema20*e and last_ema9 > last_ema20+last_ema20*e:
            # response = client.order_market_buy(symbol="SOLUSDT", quantity=0.2)
            print("Buy SOL")
        if prev_ema9+prev_ema9*e > prev_ema20 and last_ema9+last_ema9*e < last_ema20:
            # response = client.order_market_sell(symbol="SOLUSDT", quantity=0.2)
            print("Sell SOL")
    except Exception as ex:
        print("Caught exception.")
        print(ex)


def getTapiData(symbol, interval, backtracks, period):
    api_url = f"https://api.taapi.io/ema?secret={TAAPI_SECRET}&exchange=binance&symbol={symbol}&interval={interval}&backtracks={backtracks}&period={period}"
    response = requests.get(api_url)
    return response.json()


bot.polling(none_stop=True, interval=0)

# def trade():
#     try:
#         global API_KEY, API_SECRET
#         ema9 = getTapiData("SOL/USDT", "1m", 2, 9)
#         ema20 = getTapiData("SOL/USDT", "1m", 2, 20)
#         client = Client(API_KEY, API_SECRET)
#         e = 0.0005
#         last_ema9 = ema9[0]["value"]
#         prev_ema9 = ema9[1]["value"]
#         last_ema20 = ema20[0]["value"]
#         prev_ema20 = ema20[1]["value"]
#         if prev_ema9 < prev_ema20 +prev_ema20*e and last_ema9 > last_ema20+last_ema20*e:
#             # response = client.order_market_buy(symbol="SOLUSDT", quantity=0.2)
#             print("Buy SOL")
#         if prev_ema9+prev_ema9*e > prev_ema20 and last_ema9+last_ema9*e < last_ema20:
#             # response = client.order_market_sell(symbol="SOLUSDT", quantity=0.2)
#             print("Sell SOL")
#     except Exception as ex:
#         print("Caught exception.")
#         print(ex)