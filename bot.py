import telebot
import random
import os
from telebot import types
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"


def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()


#token bota
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
echo_mud = True



#переменная клавиатура, в которой хранится эта команда
#как я понял, в скобочках дается размер кнопок, когда правда = они маленькие, когда лож = они большие
Keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#А это сами кнопки, кнопки это просто слова которые не надо печатать. Если написать в ручную, то все будет работать
#у меня knopka = knp
knp1 = types.KeyboardButton("помощь")
knp2 = types.KeyboardButton("играть")
knpE_ON = types.KeyboardButton("повторяй")
knpE_OFF = types.KeyboardButton("перестань повторять")
Keyboard.add(knp1, knp2, knpE_OFF, knpE_ON)


Keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
knp3 = types.KeyboardButton("1")
knp4 = types.KeyboardButton("2")
knp5 = types.KeyboardButton("3")
knp6 = types.KeyboardButton("4")
knp7 = types.KeyboardButton("5")
knp8 = types.KeyboardButton("6")
knp9 = types.KeyboardButton("7")
knp10 = types.KeyboardButton("8")
#Надо добавить теперь кнопку на экран
Keyboard1.add(knp3, knp4, knp5, knp6, knp7)


#1 функция
#если нажата кнопка старт, то он будет печатать это
@bot.message_handler(commands=["start"])
def start(message):                                                                                #насильно вызывает клавиатуру во время старта
    bot.send_message(message.chat.id, "ПРИВЕЕЕЕТ! Я бот попугай и буду повторять за тобой слова!", reply_markup=Keyboard)
     #тут аналогично, не нужно ретурн, функция сама выполнит и напишет по айди отправителя уже заданный текст!



#2 функция
#если напечатать помощь, то он будет писать кто он и для чего. Ловер и стрип должны быть после text для правильности
@bot.message_handler(func=lambda message: message.text.lower().strip() == "помощь")#и если я делаю кнопки, лучше значения писать с маленькой буквы
def help(message):
    bot.send_message(message.chat.id, "Давай введу в курс дела!\nЯ создан для чила и расслабона!\nПока я могу лишь только повторять за тобой слова\nНО! В будущем я стану куда продвинутей!")
        #тут аналогично, не нужно ретурн, функция сама выполнит и напишет по айди отправителя уже заданный текст!

#4 функция
#Должна быть игра в угадайку
@bot.message_handler(func=lambda message: message.text.lower().strip() == "играть")
def igra(message):
    bot.send_message(message.chat.id, "Чудно, тогда поиграем!")#аналог print!
    sikret = random.randint(1, 8)
    popitki = 3
    bot.send_message(message.chat.id, "Так так, придумал! Знай! У тебя 3 попытки!!!", reply_markup=Keyboard1)
    bot.register_next_step_handler(message, chislo, sikret, popitki)#аналог input!
#ВСЕ ЭТИ АНАЛОГИ ВАЖНО ЗАПОМНИТЬ

def chislo(message, sikret, popitki):
    #Проверка что введены числа. если сообщения не цифры, то истина ложь
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Стоит ввести ЧИСЛА!")#просит ввести еще раз
        bot.register_next_step_handler(message, chislo, sikret, popitki)
        return#возвращает функцию, так думал я, но это выход

    #вариант пользователя превращается из цифры в строку. ТОЖЕ ОЧЕНЬ ВАЖНО
    variant = int(message.text)

    if variant == sikret:
        bot.send_message(message.chat.id, f"Вау, вы просто экстрасенс! Загаданое число {sikret} угадано, Поздравляю!", reply_markup=Keyboard)
        return#Типа выход из функции
    
    popitki -= 1
    if popitki == 0:
        bot.send_message(message.chat.id, f"Прости, но попытки кончились. Ты проиграл, а загаданное число было {sikret}.\nПовезет в другой раз!:3", reply_markup=Keyboard)
        return
    
    if variant > sikret:
        spora = "меньше"
    else:
        spora = "больше"

    bot.send_message(message.chat.id, f"Пупупу, кажется ты не угадал!\nОсталось попыток {popitki}, а загаданное число {spora}")
    bot.register_next_step_handler(message, chislo, sikret, popitki)


@bot.message_handler(func=lambda message: message.text.lower().strip() == "повторяй")
def turn_echo_on(message):
    global echo_mud
    echo_mud = True
    bot.send_message(message.chat.id, "Буду повторять за вами!")


@bot.message_handler(func=lambda message: message.text.lower().strip() == "перестань повторять")
def turn_echo_off(message):
    global echo_mud
    echo_mud = False
    bot.send_message(message.chat.id, "Хорошо, больше не буду.")



#3 функиця
#если он ловит любое сообщение, то вызывается основная функция попугая
@bot.message_handler(func=lambda message:True)
def echo(message):
    global echo_mud
    if echo_mud:
        bot.send_message(message.chat.id, f"КхмКхм... {message.text}")
        #Это то что он будет делать, писать сообщение по айди отправителя копируя его текст с препиской кхмкхм


print("Бот работает!")
bot.infinity_polling()
