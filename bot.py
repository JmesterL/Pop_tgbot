import telebot
import random
import json
import time
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
echo_mud = False


#Куда сохранится бот. Типа путь к данным
data_file = os.path.join(os.path.dirname(__file__), "popug.json")


#выгружает питомцев если есть
def load_popug():
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return{}

#Сохраняет питомца
def save_popug(popug):
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(popug, f, ensure_ascii=False, indent=4)


#Обновления данных об питомце
def get_popug(user_id):
    popug = load_popug()
    user_id = str(user_id)
#если нет создаю нового
    if user_id not in popug:
        popug[user_id] = { #списочек как в json файле с данными
            "Level": 1,
            "xp": 0,
            "XP_next": 5,
            "Last_feed": 0,
            "money": 0
        }
        save_popug(popug)#сохраняет опять же
    return popug[user_id]

def update_popug(user_id, data):#обновляет попуга
    popug = load_popug()#загружает 
    popug[str(user_id)] = data #вот это я не понял
    save_popug(popug)#И сохраняет

#Функция добавления опыта. Очень важно
def add_xp(user_id, amount):
    user_id = str(user_id)
    popug = load_popug()
    #это если нет попуга
    if user_id not in popug:
        popug[user_id] = {"Level": 1, "xp": 0, "XP_next": 5, "Last_feed": 0, "money": 0}
        #как я понял, это список который находится в popug[user_id]
    
    pet = popug[user_id]#pet будет равен попугу для удобства
    pet["xp"] += amount #а это я как здесь сколько нужно будет добавить к хр, это будет ниже по коду
    leveled = False#Если кормим и не хватает опыта, то переход типа лож

    while pet["xp"] >= pet["XP_next"]: #Если хр больше требуемого значения
        pet["xp"] -= pet["XP_next"] #ТО от хр отнимается требуемый уровень
        pet["Level"] += 1 # и добовляется +1 уровень
        pet["XP_next"] = int(pet["XP_next"] * 2) # и так же следущий уровень требует в 2 раза больше опыта
        leveled = True#Соответсвенно, когда переход удовлетворителен, то это истина

    save_popug(popug)#сохраняет попуга
    return leveled, pet

#Зернышки, принцип добавления такой же как и с уровнем
def add_money(user_id, amount):
    user_id = str(user_id)#Теперь понял!!! Мы превращаем айди пользователя в строку для json файла
    pet = get_popug(user_id)#pet становится popugom для удобства
    pet['money'] += amount#Как и с уровнем, добовляем опыт
    update_popug(user_id, pet)#обращаемся к функции обновления попуга
    return pet["money"]#обновляем значения зерен

#переменная клавиатура, в которой хранится эта команда
#как я понял, в скобочках дается размер кнопок, когда правда = они маленькие, когда лож = они большие
Keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#А это сами кнопки, кнопки это просто слова которые не надо печатать. Если написать в ручную, то все будет работать
#у меня knopka = knp
knp1 = types.KeyboardButton("Помощь")
knp2 = types.KeyboardButton("Играть")
knpE_ON = types.KeyboardButton("Повторяй")
knpE_OFF = types.KeyboardButton("Не повторяй")
knp_popug = types.KeyboardButton("Попугай")
Keyboard.add(knp1, knp2, knpE_OFF, knpE_ON, knp_popug)


#Это для тамагочи
Keyboardpopug = types.ReplyKeyboardMarkup(resize_keyboard=True)
knp_est = types.KeyboardButton("Покормить")
knp_info = types.KeyboardButton("Инфо")
knp_mag = types.KeyboardButton("Магазин")
knp_e = types.KeyboardButton("Назад")
Keyboardpopug.add(knp_est, knp_info, knp_mag, knp_e)


#Это в магазине!
KeyboardTRED = types.ReplyKeyboardMarkup(resize_keyboard=True)
knp_k = types.KeyboardButton("Купить корм")
knp_e = types.KeyboardButton("Назад")
KeyboardTRED.add(knp_k, knp_e)


#Это выбор цифр во время игры
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
Keyboard1.add(knp3, knp4, knp5, knp6, knp7, knp8, knp9, knp10)


#Функция магазина
@bot.message_handler(func=lambda message: message.text.lower().strip() == "магазин")
def magas(message):
    bot.send_message(message.chat.id, "Вот что тут можно купить!\nКорм - 50 зерен", reply_markup=KeyboardTRED)


@bot.message_handler(func=lambda message: message.text.lower().strip() == "купить корм")
def pokupka(message):
    user_id = message.from_user.id
    pet = get_popug(user_id)

    if pet["money"] >= 50:
        pet["money"] -= 50

        leveled, nov_popug = add_xp(user_id, 8)
        pet["Last_feed"] = time.time()
        update_popug(user_id, pet)

        text = f"Вы купили корм! Он стоит 50 зерен.\n+8XP\nУ вас осталось зерен:{pet['money']}"
        if leveled:
            text += f"\nПоздравляю! Попуг достиг {nov_popug['Level']} уровень!"
        bot.send_message(message.chat.id, text, reply_markup=KeyboardTRED)
    
    else:
        bot.send_message(message.chat.id, "Простите, но у вас недостаточно зерен.", reply_markup=KeyboardTRED)

@bot.message_handler(func=lambda message: message.text.lower().strip() == "назад")
def vihod(message):
    bot.send_message(message.chat.id, "Хорошо, будет сделано!", reply_markup=Keyboard)


#1 Функция просмотра попугая
@bot.message_handler(func=lambda message: message.text.lower().strip() == "попугай")
def popug(message):
    bot.send_message(message.chat.id, "Это твой личный попугай. Пока он гордый и его нельзя назвать каким то именем\nНо можно покормить и посмотреть информацию о нем\nКстати, займись этим", reply_markup=Keyboardpopug)

#2 Функция просмотра инфо
@bot.message_handler(func=lambda message: message.text.lower().strip() == "инфо")
def info(message):
    user_id = message.from_user.id
    pet = get_popug(user_id)
    text = f"Уровень: {pet['Level']}\nОпыт: {pet['xp']}/{pet['XP_next']}\nЗерна: {pet['money']}"
    bot.send_message(message.chat.id, text, reply_markup=Keyboardpopug)

#3 Функция кормешки
@bot.message_handler(func=lambda message: message.text.lower().strip() == "покормить")
def corm(message):
    user_id = message.from_user.id
    pet = get_popug(user_id)
    now = time.time()

    if now - pet.get("Last_feed", 0) < 300:
        bot.send_message(message.chat.id, "Попуг еще сыт. Нужно подождать пять минут", reply_markup=Keyboardpopug)
        return

    pet["Last_feed"] = now
    update_popug(user_id, pet)

    leveled, nov_popug = add_xp(user_id, 2)
    money = add_money(user_id, 5)
    text = f"Вы покормили попуга и теперь он сыт!!!\n+2XP. Вы заслужили целых 5 зерен!\nТеперь у вас зерен в количевстве {money} штук"
    if leveled:
        text += f"\nПоздравляю! Попуг достиг {nov_popug['Level']} уровень!"
    bot.send_message(message.chat.id, text, reply_markup=Keyboardpopug)

#4 функция
#если нажата кнопка старт, то он будет печатать это
@bot.message_handler(commands=["start"])
def start(message):                                                                                #насильно вызывает клавиатуру во время старта
    bot.send_message(message.chat.id, "ПРИВЕЕЕЕТ! Я бот попугай! Воспользуйся помощью чтобы понять что к чему.", reply_markup=Keyboard)
     #тут аналогично, не нужно ретурн, функция сама выполнит и напишет по айди отправителя уже заданный текст!



#5 функция
#если напечатать помощь, то он будет писать кто он и для чего. Ловер и стрип должны быть после text для правильности
@bot.message_handler(func=lambda message: message.text.lower().strip() == "помощь")#и если я делаю кнопки, лучше значения писать с маленькой буквы
def help(message):
    bot.send_message(message.chat.id, "Давай введу в курс дела!\nЯ создан для чила и расслабона!\n!Я могу повторять за тобой слова\nСо мной можно играть в числа\nМожно растить и ухаживать за собственным\nНО! В будущем я стану куда продвинутей и появится куда больше интересных фич!")
        #тут аналогично, не нужно ретурн, функция сама выполнит и напишет по айди отправителя уже заданный текст!

#6 функция
#Должна быть игра в угадайку
@bot.message_handler(func=lambda message: message.text.lower().strip() == "играть")
def igra(message):
    bot.send_message(message.chat.id, "Чудно, тогда поиграем!")#аналог print!
    user_id = message.from_user.id
    sikret = random.randint(1, 8)
    popitki = 3
    bot.send_message(message.chat.id, "Так так, придумал! Знай! У тебя 3 попытки!!!", reply_markup=Keyboard1)
    bot.register_next_step_handler(message, chislo, sikret, popitki, user_id)#аналог input!
#ВСЕ ЭТИ АНАЛОГИ ВАЖНО ЗАПОМНИТЬ

def chislo(message, sikret, popitki, user_id):
    #Проверка что введены числа. если сообщения не цифры, то истина ложь
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Стоит ввести ЧИСЛА!")#просит ввести еще раз
        bot.register_next_step_handler(message, chislo, sikret, popitki, user_id)
        return#возвращает функцию, так думал я, но это выход

    #вариант пользователя превращается из цифры в строку. ТОЖЕ ОЧЕНЬ ВАЖНО
    variant = int(message.text)

    if variant == sikret:
        money = add_money(user_id, 10)#За победу дает целых 10 зерен
        bot.send_message(message.chat.id, f"Вау, вы просто экстрасенс! Загаданое число {sikret} угадано, Поздравляю!\nДумаю вы заслужили 10 зерен. Теперь у тебя зерен в количестве {money} штук", reply_markup=Keyboard)
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
    bot.register_next_step_handler(message, chislo, sikret, popitki, user_id)


#7 пара функций вкл и вкл повторяйки
#включает повтор
@bot.message_handler(func=lambda message: message.text.lower().strip() == "повторяй")
def turn_echo_on(message):
    global echo_mud
    echo_mud = True
    bot.send_message(message.chat.id, "Буду повторять за вами!")


#выключает повтор
@bot.message_handler(func=lambda message: message.text.lower().strip() == "не повторяй")
def turn_echo_off(message):
    global echo_mud
    echo_mud = False
    bot.send_message(message.chat.id, "Хорошо, больше не буду.")



#8 функиця
#если он ловит любое сообщение, то вызывается основная функция попугая
@bot.message_handler(func=lambda message:True)
def echo(message):
    global echo_mud
    if echo_mud:
        bot.send_message(message.chat.id, f"КхмКхм... {message.text}")
        #Это то что он будет делать, писать сообщение по айди отправителя копируя его текст с препиской кхмкхм


print("Бот работает!")
bot.infinity_polling()
