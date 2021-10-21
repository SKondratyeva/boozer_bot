import telebot
from telebot import types
import pandas as pd
import emoji
import sqlite3

conn = sqlite3.connect('boozer.db')
cursor = conn.cursor()

try:
    query = "CREATE TABLE \"recipes\" (\"ID\" INTEGER UNIQUE, \"user_id\" INTEGER, \"title\" TEXT,\"recipe\" TEXT, PRIMARY KEY (\"ID\"))"
    cursor.execute(query)
except:
    pass

bot = telebot.TeleBot('2090115227:AAG5fKkr5L-Myh8XFoyZj8WWx2OswddPUI0')


@bot.message_handler(commands=['start'])
def send_start_keyboard(message, text="Привет! Я могу подсказать тебе рецепт классного " +
                                      "коктейля. А когда ты приготовишь свой шедевр, то я обработаю его фоточку." +
                                      " Что ты хочешь сейчас?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Узнать рецепт коктейля')
    itembtn2 = types.KeyboardButton('Добавить рецепт')
    itembtn3 = types.KeyboardButton('Мои рецепты')
    keyboard.add(itembtn1, itembtn2, itembtn3)
    msg = bot.send_message(message.from_user.id, text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, menu)


def handle_errors(msg):
    send_start_keyboard(msg, text="Я тебя не понял. Давай попробуем еще раз?")


def end_action(msg):
    send_start_keyboard(msg, text="Надеюсь, тебе понравилось:) Чем я еще могу помочь?")


def menu(call):
    if call.text == "Узнать рецепт коктейля":
        send_menu(call, text='Что будем пить?' + emoji.emojize(':face_with_tongue:'))
    elif call.text == 'Добавить рецепт':
        msg = bot.send_message(call.chat.id, 'Пришли мне рецепт твоего коктейля в таком формате: Название > Рецепт')
        bot.register_next_step_handler(msg, add_recipe)
    elif call.text == 'Мои рецепты':
        get_recipes_list(call)
    else:
        handle_errors(msg)


def send_menu(msg, text='Чем залакируем предыдущий коктейль?' + emoji.emojize(':face_with_tongue:')):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('1.Белый русский')
    itembtn2 = types.KeyboardButton('2.Пина колада')
    itembtn3 = types.KeyboardButton('3.Негрони')
    itembtn4 = types.KeyboardButton('4.Яблочный тини')
    itembtn7 = types.KeyboardButton('В начало')
    keyboard.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn7)
    msg = bot.send_message(msg.from_user.id, text=text, reply_markup=keyboard)
    bot.register_next_step_handler(msg, make_cocktail)


def make_cocktail(call):
    df = pd.read_csv(r'recipes.csv')
    if call.text == '1.Белый русский' or call.text == '1':
        recipe_message = df.loc[df['name'] == '1.Белый русский']['recipe'].values[0]
        more_or_go(call, recipe_message)

    elif call.text == '2.Пина колада' or call.text == '2':
        recipe_message = df.loc[df['name'] == '2.Пина колада']['recipe'].values[0]
        more_or_go(call, recipe_message)

    elif call.text == '3.Негрони' or call.text == '3':
        recipe_message = df.loc[df['name'] == '3.Негрони']['recipe'].values[0]
        more_or_go(call, recipe_message)

    elif call.text == 'В начало':
        send_start_keyboard(call)
    else:
        handle_errors(call)


def more_or_go(call, recipe_message):
    keyboard2 = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Давай другой!')
    itembtn2 = types.KeyboardButton('Класс, спасибо.')
    keyboard2.add(itembtn1, itembtn2)
    msg = bot.send_message(call.chat.id, recipe_message, reply_markup=keyboard2)
    bot.register_next_step_handler(msg, another_cocktail)


def another_cocktail(call):
    if call.text == 'Давай другой!':
        send_menu(call)
    elif call.text == 'Класс, спасибо.':
        end_action(call)
    else:
        handle_errors(call)


def add_recipe(msg):
    with sqlite3.connect('boozer.db') as con:
        try:
            cursor = con.cursor()
            cursor.execute('INSERT INTO recipes (user_id, title, recipe) VALUES (?, ?, ?)',
                           (msg.from_user.id, msg.text.split(' > ')[0], msg.text.split(' > ')[1]))
            con.commit()
            bot.send_message(msg.chat.id, 'Отличный вкус! Теперь ты сможешь найти этот рецепт в разделе Мои рецепты')
            send_start_keyboard(msg, "Самое время чего-то выпить!")
        except:
            handle_errors(msg)


def get_recipes_list(msg):
    bot.send_message(msg.chat.id, 'Какой коктейль ты хочешь сделать? Вот список твои коктейлей:')
    with sqlite3.connect('boozer.db') as con:
        try:
            cursor = con.cursor()
            cursor.execute('SELECT title FROM recipes WHERE user_id=={}'.format(msg.from_user.id))
            names = cursor.fetchall()
            names_string = ''.join([i[0] + "\n" for i in names])
            bot.send_message(msg.chat.id, names_string)
            bot.register_next_step_handler(msg, get_recipe)


        except:
            handle_errors(msg)

def get_recipe(msg):
    bot.send_message(msg.chat.id, 'Нашел рецепт: ' + msg.text)
    with sqlite3.connect('boozer.db') as con:
        try:
            cursor = con.cursor()
            cursor.execute("SELECT recipe FROM recipes WHERE user_id == ? and title == ?", (msg.from_user.id, msg.text))
            recipe_string = cursor.fetchall()
            bot.send_message(msg.chat.id, recipe_string)
            end_action(msg)

        except:
            handle_errors(msg)



bot.polling(none_stop=True)
