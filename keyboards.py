import os
import telebot


def create_keyboard(kb_buttons):
    menu_kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for button in kb_buttons:
        item = telebot.types.KeyboardButton(button)
        menu_kb.add(item)
    return menu_kb


def databases_kb():
    home_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(home_dir, '_db')
    list_of_databases = os.listdir(db_dir)
    list_of_databases.remove('TG_SERVICE.db')
    kb = create_keyboard(list_of_databases)
    return kb
