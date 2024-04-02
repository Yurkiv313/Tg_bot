import threading
import time
import datetime
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


def trade():
    try:
        global API_KEY, API_SECRET
        ema9 = getTapiData("SOL/USDT", "1m", 2, 9)
        ema20 = getTapiData("SOL/USDT", "1m", 2, 20)
        rsi14 = getFuturesData("SOL/USDT", "1m", 2, 14)
        client = Client(API_KEY, API_SECRET)
        e = 0.0005
        last_ema9 = ema9[0]["value"]
        prev_ema9 = ema9[1]["value"]
        last_ema20 = ema20[0]["value"]
        prev_ema20 = ema20[1]["value"]
        last_rsi = rsi14[0]["value"]
        if not hasattr(trade, "last_action"):
            trade.last_action = "sell"

        if prev_ema9 < prev_ema20 and last_ema9 > last_ema20 and last_rsi < 70 and trade.last_action != "buy":
            current_price = client.get_symbol_ticker(symbol="SOLUSDT")["price"]
            # response = client.order_market_buy(symbol="SOLUSDT", quantity=0.2)
            buy_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Buy SOL at {current_price} at {buy_time}")
            trade.last_action = "buy"
            trade.last_buy_price = current_price
        elif prev_ema9 > prev_ema20 and last_ema9 < last_ema20 and last_rsi > 30 and trade.last_action != "sell":
            current_price = client.get_symbol_ticker(symbol="SOLUSDT")["price"]
            # response = client.order_market_sell(symbol="SOLUSDT", quantity=0.2)
            sell_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Sell SOL at {current_price} at {sell_time}")
            trade.last_action = "sell"
            trade.last_sell_price = current_price
            profit = float(current_price) - float(trade.last_buy_price)
            print(f"Profit: {profit}")
    except Exception as ex:
        print("Caught exception.")
        print(ex)



def getTapiData(symbol, interval, backtracks, period):
    api_url = f"https://api.taapi.io/ema?secret={TAAPI_SECRET}&exchange=binance&symbol={symbol}&interval={interval}&backtracks={backtracks}&period={period}"
    response = requests.get(api_url)
    return response.json()


def futures():
    try:
        rsi14_SOL_USDT = getFuturesData("SOL/USDT", "1m", 2, 14)
        # rsi14_BTC_USDT = getFuturesData("BTC/USDT", "1m", 2, 14)
        # rsi14_ETH_USDT = getFuturesData("ETH/USDT", "1m", 2, 14)
        # rsi14_BNB_USDT = getFuturesData("BNB/USDT", "1m", 2, 14)
        return rsi14_SOL_USDT#,rsi14_BTC_USDT, rsi14_ETH_USDT, rsi14_BNB_USDT
    except Exception as ex:
        print("Caught exception.")
        print(ex)
        return None


def getFuturesData(symbol, interval, backtracks, period):
    api_url = f"https://api.taapi.io/rsi?secret={TAAPI_SECRET}&exchange=binance&symbol={symbol}&interval={interval}&backtracks={backtracks}&period={period}"
    response = requests.get(api_url)
    return response.json()


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
        btn7 = types.KeyboardButton("Get futures notification")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
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
        btn7 = types.KeyboardButton("Get futures notification")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
        bot.send_message(message.from_user.id, "👀 Виберіть потрібний вам розділ", reply_markup=markup)

    elif message.text == "Start trading":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("🔙 Головне меню")
        markup.add(btn)
        bot.send_message(message.from_user.id, "⬇ Виберіть розділ", reply_markup=markup)

        schedule.every(8).seconds.do(trade)
        stop_run_continuously = run_continuously()

    elif message.text == "Get futures notification":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("🔙 Головне меню")
        markup.add(btn)

        def send_rsi_notification():
            try:
                rsi14 = futures()
                rsi = int(rsi14[0]["value"])
                if rsi is not None:
                    if rsi < 15:
                        bot.send_message(message.from_user.id, "RSI is below 15! SOL/USDT Time 1m")
                        time.sleep(120)
                    elif rsi > 65:
                        bot.send_message(message.from_user.id, "RSI is above 65! SOL/USDT Time 1m")
                        time.sleep(120)
            except Exception as ex:
                print("Caught exception.")
                print(ex)

        schedule.every(8).seconds.do(send_rsi_notification)

        stop_run_continuously = run_continuously()


bot.polling(none_stop=True, interval=0)
