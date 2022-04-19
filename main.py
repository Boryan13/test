from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time, os

from telegram import Update, ReplyKeyboardMarkup #upm package(python-telegram-bot)
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext  #upm package(python-telegram-bot)

from flask import Flask, render_template

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("window-size=1000,600")
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)

app = Flask(__name__)
@app.route('/')
def index():
	return render_template("index.html")
	
def open_payeer():
	driver.get("https://proxyscrape.com/web-proxy")
	driver.find_element(By.TAG_NAME, "input").send_keys("https://payeer.com/ru/trade/")
	driver.find_elements(By.TAG_NAME, "button")[1].click()
	time.sleep(4)

def lider(symbol, res):
    driver.find_elements(By.CLASS_NAME, "trade-pairs__filters-item")[2].click()
    time.sleep(1)
    pair = driver.find_elements(By.CLASS_NAME, "trade-pairs__table-item")
    if pair[0].find_elements(By.TAG_NAME, "div")[4].text[0] != symbol:
        driver.find_elements(By.CLASS_NAME, "trade-pairs__filters-item")[2].click()
    pair = driver.find_elements(By.CLASS_NAME, "trade-pairs__table-item")
    for i in pair:
        pair_trade = i.find_elements(By.TAG_NAME, "div")
        if bool(pair_trade[1].text):
            res += pair_trade[1].text + pair_trade[2].text + " = " + pair_trade[3].text + "; " + pair_trade[4].text + "\n"
			
    return res
			
def echo(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    trade = driver.find_elements(By.CLASS_NAME, "trade-pairs__list")
    trade_pair = []
    for i in trade:
        trade_pair += [[j.text] for j in i.find_elements(By.TAG_NAME, "div") if j.text != "ВСЕ"]
    res = ""
    if text == "Все валюты":
        res = "Выберите валюту"
        custom_keyboard = trade_pair
    elif [text] in trade_pair:
        length = trade_pair.index([text])
        for i in trade:
            if i == trade[0]:
                length += 1
            if length < len(i.find_elements(By.TAG_NAME, "div")):
                i.find_elements(By.TAG_NAME, "div")[length].click()
                break
            else:
                length = length - len(i.find_elements(By.TAG_NAME, "div"))
        pair = driver.find_elements(By.CLASS_NAME, "trade-pairs__table-item")
        for i in pair:
            pair_trade = i.find_elements(By.TAG_NAME, "div")
            if bool(pair_trade[1].text):
                res += pair_trade[1].text + pair_trade[2].text + " = " + pair_trade[3].text + "\n"
        custom_keyboard = [["Все валюты"], ["Лидеры роста"], ["Лидеры падения"]]
    elif text == "Лидеры роста":
        trade[0].find_elements(By.TAG_NAME, "div")[0].click()
        res = lider("+", res)
        custom_keyboard = [["Все валюты"], ["Лидеры роста"], ["Лидеры падения"]]
    elif text == "Лидеры падения":
        trade[0].find_elements(By.TAG_NAME, "div")[0].click()
        res = lider("-", res)
        custom_keyboard = [["Все валюты"], ["Лидеры роста"], ["Лидеры падения"]]
    else:
        res = "Неопознанная команда"
        custom_keyboard = [["Все валюты"], ["Лидеры роста"], ["Лидеры падения"]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    update.message.reply_text(res, reply_markup = reply_markup)

def telegram_bot():
    updater = Updater(os.getenv("token"))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()


def main():
    open_payeer()
    telegram_bot()
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
	main()








