import os
import re
import logging
import telebot
from datetime import datetime
from sqlitemodule import *
from keyboards import *
from replicas import *


# TG token
home_dir = os.path.dirname(os.path.abspath(__file__))
telebot_file = os.path.join(home_dir, "telebot_token")
with open(telebot_file, 'r')  as x:
    token = x.read().splitlines()[0]
bot = telebot.TeleBot(token)
bot.set_webhook()

# Logging Setting
logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG)
logging.getLogger("telegram").setLevel(logging.WARNING)
# Users data
ADMINS_USERNAMES = {"Victoria Shinkarenko": "vic164"}
admin_chat_id = "281651883"

# KeyBoards
santa_types_buttons = ["ClassicSanta", "PetSanta"]
santa_types_kb = create_keyboard(santa_types_buttons)

pet_santa_recipient_buttons = ['Cat', 'Dog', 'Any']
pet_santa_recipient_kb = create_keyboard(pet_santa_recipient_buttons)

yesno_buttons = ["Yes", "No"]
yesno_kb = create_keyboard(yesno_buttons)

language_buttons = ["Русский", "English", "ქართული"]
language_kb = create_keyboard(language_buttons)

cancel_buttons = ["Cancel PetSanta registration", 
        "Cancel SecretSanta registration", "Cancel all", "Back"]
cancel_kb = create_keyboard(cancel_buttons)

# Global
awaiting_admin_confirmation = {}


def send_msg(uid, replica, kb=None, mode=None, not_replica=False):
    lang = get_user_lang(uid)
    text = ""
    if not_replica:
        text = replica
    else:
        try:
            text = replica[lang]
        except Exception:
            logging.error("Replica with user language not found")
            bot.send_message(uid, "Please contact @vic164")
            return
    if not kb:
        kb = telebot.types.ReplyKeyboardRemove()
    if mode:
        bot.send_message(uid, text, reply_markup=kb, parse_mode="HTML")
    else:
        bot.send_message(uid, text, reply_markup=kb)
    logging.debug("Message has been sent tp user " + str(uid))


@bot.message_handler(func=lambda message: message.from_user.is_bot)
def reject_bots(message):
    logging.info("Bot found, ignore it")
    logging.debug(message)
    return


@bot.message_handler(commands=["start"])
def start(message, res=False):
    """ Message /start """
    logging.debug(message)
    user_id = message.chat.id
    new_user_lang(user_id)
    santa_id = get_santa_id(user_id)
    if get_conversation_step(user_id):
        send_msg(user_id, REPLICA_INAPPROPRIATE_START)
        return
    if len(santa_id) == 2:
        send_msg(user_id, REPLICA_ALREADY_REGISTERED)
        for i in santa_id:
            send_msg(user_id, "<code>" + str(i) + "</code>", None, "HTML", True)
    elif len(santa_id) == 1:
        send_msg(user_id, REPLICA_ALREADY_REGISTERED)
        send_msg(user_id, "<code>" + str(santa_id[0]) + "</code>", None, "HTML", True)
        first_santa_type = get_already_registered_santa_type(user_id)
        if first_santa_type == 'ClassicSanta':
            logging.debug("User already registered as ClassicSanta")
            new_santa_conversation(user_id,"ask_tobe_petsanta")
            send_msg(user_id, REPLICA_SECOND_REGISTRATION_PETSANTA, yesno_kb)
        elif first_santa_type == 'PetSanta':
            logging.debug("User already registered as PetSanta")
            new_santa_conversation(user_id, "ask_tobe_classicsanta")
            send_msg(user_id, REPLICA_SECOND_REGISTRATION_HUMSANTA, yesno_kb)
    else:
        send_msg(user_id, REPLICA_HI, None, "HTML")
        new_santa_conversation(user_id, "ask_name")
        send_msg(user_id, REPLICA_Q1)


@bot.message_handler(commands=["help"])
def help(message, res=False):
    """ Message /help """
    user_id = message.chat.id
    send_msg(user_id, REPLICA_HELP, None, "HTML")


@bot.message_handler(commands=["cancel"])
def cancel(message, res=False):
    """ Message /cancel """
    user_id = message.chat.id
    clean_santa_conversation(str(user_id))
    new_santa_conversation(user_id, "confirm_cancel")
    send_msg(user_id, REPLICA_SURE_TO_CANCEL, cancel_kb)


@bot.message_handler(commands=["donate"])
def donate(message, res=False):
    """ Message /donate """
    user_id = message.chat.id
    send_msg(user_id, REPLICA_DONATION_DATA, None, "HTML")


@bot.message_handler(commands=["change_language"])
def change_language(message, res=False):
    """ Message /change_language """
    user_id = message.chat.id
    update_santa_conversation(user_id, "ask_new_lang")
    send_msg(user_id, REPLICA_CHANGE_LANGUAGE, language_kb)


@bot.message_handler(commands=['profile'])
def profile(message):
    """ Message /profile"""
    user_id = message.chat.id
    # Classic Secret Santa 
    CLASSIC_SANTA_ID = get_classicsanta_data(user_id, "SANTA_ID")
    if CLASSIC_SANTA_ID:
        CLASSIC_SANTA_WISHES = get_classicsanta_data(user_id, "DETAILS")
        send_msg(user_id, REPLICA_SECRETSANTA_PROFILE)
        send_msg(user_id, "<code>" + CLASSIC_SANTA_ID + "</code>", None, "HTML", True)
        send_msg(user_id, "Details: " + CLASSIC_SANTA_WISHES, not_replica=True)
        #send_msg(user_id, "/change_santa_wishes", not_replica=True)
        send_msg(user_id, REPLICA_CAN_UPDATE_CLASSIC)
    # Pet Santa
    PET_SANTA_ID = get_petsanta_data(user_id, "SANTA_ID")
    if PET_SANTA_ID:
        PET_SANTA_WISHES = get_petsanta_data(user_id, "DETAILS")
        send_msg(user_id, REPLICA_PETSANTA_PROFILE)
        send_msg(user_id, "<code>" + PET_SANTA_ID + "</code>", None, "HTML", True)
        send_msg(user_id, PET_SANTA_WISHES, not_replica=True)
        #send_msg(user_id, "\n/change_santa_pet", not_replica=True)
        send_msg(user_id, REPLICA_CAN_UPDATE_PET)
    if CLASSIC_SANTA_ID or PET_SANTA_ID:
        send_msg(user_id, REPLICA_CAN_CANCEL)
    if not CLASSIC_SANTA_ID and not PET_SANTA_ID:
        send_msg(user_id, REPLICA_NOT_SANTA_YET)


@bot.message_handler(commands=['change_santa_wishes'])
def change_santa_wishes_msg(message):
    """ Message /change_santa_wishes"""
    user_id = message.chat.id
    is_registered = check_santa_registered(user_id, 'ClassicSanta')
    logging.warning("Is_registered in change_santa_wishes_reply: " + str(is_registered))
    if not is_registered:
        send_msg(user_id, REPLICA_NOT_SECRETSANTA_YET)
        return
    update_santa_conversation(user_id, "change_santa_wishes")
    send_msg(user_id, REPLICA_Q3_1)


@bot.message_handler(commands=['change_santa_pet'])
def change_santa_pet_msg(message):
    """ Message /change_santa_pet"""
    user_id = message.chat.id
    is_registered = check_santa_registered(user_id, 'PetSanta')
    logging.warning("Is_registered in change_santa_wishes_reply: " + str(is_registered))
    if not is_registered:
        send_msg(user_id, REPLICA_NOT_PETSANTA_YET)
        return
    update_santa_conversation(user_id, "change_santa_pet")
    send_msg(user_id, REPLICA_Q3_2, pet_santa_recipient_kb)


@bot.message_handler(func=lambda message: get_conversation_step(message.chat.id) == "ask_name")
def ask_name(message):
    user_id = message.chat.id
    user_name = str(message.text)
    santa_data = (str(user_id),str(user_name),"tobeupdated",
            "tobeupdated","0","tobeupdated","filling")
    add_new_santa(santa_data)
    update_santa_conversation(user_id, "ask_santa_type")
    send_msg(user_id, REPLICA_Q2, santa_types_kb, "HTML")


@bot.message_handler(func=lambda message: get_conversation_step(message.chat.id) == "ask_santa_type")
def ask_santa_type(message):
    user_id = message.chat.id
    santa_type = message.text
    logging.debug("Santa type: " + str(santa_type))
    if santa_type == "ClassicSanta":
        update_santa_type(user_id, santa_type)
        update_santa_conversation(user_id, "ask_details")
        send_msg(user_id, REPLICA_Q3_1)
    elif santa_type == "PetSanta":
        update_santa_type(user_id, santa_type)
        update_santa_conversation(user_id, "ask_details")
        send_msg(user_id, REPLICA_Q3_2, pet_santa_recipient_kb)
    else:
        send_msg(user_id, REPLICA_INCORRECT_ANSWER)
        send_msg(user_id, REPLICA_Q2, santa_types_kb, "HTML")


@bot.message_handler(func=lambda message: get_conversation_step(message.chat.id) == "ask_details")
def ask_details(message):
    user_id = message.chat.id
    wish_details = str(message.text)
    santa_type = get_santa_type(str(user_id))
    logging.debug("Checking Santa Type: " + str(santa_type))
    if santa_type == "ClassicSanta":
        update_santa_details(user_id, wish_details)
        update_santa_conversation(user_id, "ask_donation")
        send_msg(user_id, REPLICA_DONATION, None, "HTML")
    else:
        try:
            if wish_details == 'Cat' or wish_details == 'Dog' or wish_details == 'Any':
                update_santa_details(user_id, wish_details)
                santa_id = "PetSanta-" + str(generate_santa_id())
                update_santa_id(user_id, santa_id)
                update_santa_status(user_id, "registered")
                send_msg(user_id, REPLICA_SANTA_ID)
                send_msg(user_id, "<code>" + str(santa_id) + "</code>", None, "HTML", True)
                send_msg(user_id, REPLICA_WHATS_NEXT_AFTER_REGISTRATION)
                clean_santa_conversation(str(user_id))
            else:
                send_msg(user_id, REPLICA_INCORRECT_ANSWER)
                send_msg(user_id, REPLICA_Q3_2, pet_santa_recipient_kb)
        except Exception as e:
            logging.error("Saving PetSanta failed: " + str(e))
            send_msg(user_id, REPLICA_INCORRECT_ANSWER)
            send_msg(user_id, REPLICA_Q3_2, pet_santa_recipient_kb)


@bot.message_handler(func=lambda message: get_conversation_step(message.chat.id) == "ask_donation", content_types=['photo'])
def ask_donation(message):
    user_id = message.chat.id
    logging.debug("Photo found")
    forwarded_message = bot.forward_message(admin_chat_id, user_id, message.message_id)
    awaiting_admin_confirmation[forwarded_message.message_id] = user_id
    send_msg(user_id, REPLICA_PIC_SENT_FOR_CONFIRM)


@bot.message_handler(func=lambda message: get_conversation_step(message.chat.id) == "ask_donation", content_types=['text'])
def ask_donation_spare(message):
    user_id = message.chat.id
    send_msg(user_id, REPLICA_ASK_DONATION_REPEAT)
    logging.error("No picture in the message about donation: " + str(message.text))


@bot.message_handler(func=lambda message: message.reply_to_message and message.chat.id == int(admin_chat_id))
def confirm_donation(message):
    if message.reply_to_message.message_id in awaiting_admin_confirmation:
        user_id = awaiting_admin_confirmation[message.reply_to_message.message_id]
        try:
            donated_sum = message.text
            update_santa_donate(user_id, donated_sum)
            # Generate a unique Santa ID for the user
            santa_id = "SecretSanta-" + str(generate_santa_id())
            update_santa_id(user_id, santa_id)
            update_santa_status(user_id, "registered")
            send_msg(user_id, REPLICA_SANTA_ID)
            send_msg(user_id, "<code>" + str(santa_id) + "</code>", None, "HTML", True)
            send_msg(user_id, REPLICA_WHATS_NEXT_AFTER_REGISTRATION)
            clean_santa_conversation(str(user_id))
            del awaiting_admin_confirmation[message.reply_to_message.message_id]
        except ValueError:
            bot.send_message(admin_chat_id, "Please respond with a valid donation amount.")
    else:
        bot.send_message(admin_chat_id, "This donation is not associated with any pending user registration.")


@bot.message_handler(func=lambda message: get_conversation_step(message.chat.id) == "ask_tobe_petsanta")
def ask_tobe_petsanta(message):
    user_id = message.chat.id
    answer = message.text
    if answer == 'Yes':
        user_name = get_santa_name(user_id)
        santa_data = (str(user_id),user_name,"PetSanta",
                "tobeupdated","0","tobeupdated","filling")
        add_new_santa(santa_data)
        update_santa_conversation(user_id, "ask_details")
        send_msg(user_id, REPLICA_Q3_2, pet_santa_recipient_kb)
    elif answer == 'No':
        send_msg(user_id, REPLICA_HAVE_A_NICE_DAY)
        send_msg(user_id, REPLICA_UNKNOWN_MESSAGE)
        clean_santa_conversation(str(user_id))
    else:
        send_msg(user_id, REPLICA_INCORRECT_ANSWER)
        send_msg(user_id, REPLICA_SECOND_REGISTRATION_PETSANTA, yesno_kb)


@bot.message_handler(func=lambda message: get_conversation_step(message.chat.id) == "ask_tobe_classicsanta")
def ask_tobe_classicsanta(message):
    user_id = message.chat.id
    answer = message.text
    if answer == 'Yes':
        user_name = get_santa_name(user_id)
        santa_data = (str(user_id),user_name,"ClassicSanta",
                "tobeupdated","0","tobeupdated","filling")
        add_new_santa(santa_data)
        update_santa_conversation(user_id, "ask_details")
        send_msg(user_id, REPLICA_Q3_1)
    elif answer == 'No':
        send_msg(user_id, REPLICA_HAVE_A_NICE_DAY)
        send_msg(user_id, REPLICA_UNKNOWN_MESSAGE)
        clean_santa_conversation(str(user_id))
    else:
        send_msg(user_id, REPLICA_INCORRECT_ANSWER)
        send_msg(user_id, REPLICA_SECOND_REGISTRATION_HUMSANTA, yesno_kb)


@bot.message_handler(func=lambda message: get_conversation_step(message.chat.id) == "confirm_cancel")
def confirm_cancel(message):
    user_id = message.chat.id
    answer = message.text
    if answer == 'Cancel SecretSanta registration':
        remove_secretsanta(str(user_id))
        clean_santa_conversation(str(user_id))
        send_msg(user_id, REPLICA_CANCELLED)
        send_msg(user_id, REPLICA_HAVE_A_NICE_DAY)
    elif answer == 'Cancel PetSanta registration':
        remove_petsanta(str(user_id))
        clean_santa_conversation(str(user_id))
        send_msg(user_id, REPLICA_CANCELLED)
        send_msg(user_id, REPLICA_HAVE_A_NICE_DAY)
    elif answer == 'Cancel all':
        remove_santa(str(user_id))
        remove_filling_entries(str(user_id))
        clean_santa_conversation(str(user_id))
        send_msg(user_id, REPLICA_CANCELLED)
        send_msg(user_id, REPLICA_HAVE_A_NICE_DAY)
    elif answer == 'Back':
        send_msg(user_id, REPLICA_UNKNOWN_MESSAGE)
    else:
        send_msg(user_id, REPLICA_INCORRECT_ANSWER)
        send_msg(user_id, REPLICA_SURE_TO_CANCEL, cancel_kb)


@bot.message_handler(func=lambda message: get_conversation_step(message.chat.id) == "ask_new_lang")
def ask_new_lang(message):
    user_id = message.chat.id
    new_lang = str(message.text)
    if new_lang == 'Русский':
        update_user_lang(user_id, 'ru')
        clean_santa_conversation(str(user_id))
        send_msg(user_id, REPLICA_LANG_ACCEPTED)
        send_msg(user_id, REPLICA_UNKNOWN_MESSAGE)
    elif new_lang == 'English':
        update_user_lang(user_id, 'en')
        clean_santa_conversation(str(user_id))
        send_msg(user_id, REPLICA_LANG_ACCEPTED)
        send_msg(user_id, REPLICA_UNKNOWN_MESSAGE)
    elif new_lang == 'ქართული':
        update_user_lang(user_id, 'ka')
        clean_santa_conversation(str(user_id))
        send_msg(user_id, REPLICA_LANG_ACCEPTED)
        send_msg(user_id, REPLICA_UNKNOWN_MESSAGE)
    else:
        send_msg(user_id, REPLICA_INCORRECT_ANSWER)
        send_msg(user_id, REPLICA_CHANGE_LANGUAGE, language_kb)


@bot.message_handler(func=lambda message: get_conversation_step(message.chat.id) == "change_santa_wishes")
def change_santa_wishes_reply(message):
    user_id = message.chat.id
    wish_details = str(message.text)
    change_santa_wishes(user_id, wish_details)
    clean_santa_conversation(user_id)
    send_msg(user_id, REPLICA_CHANGE_ACCEPTED)


@bot.message_handler(func=lambda message: get_conversation_step(message.chat.id) == "change_santa_pet")
def change_santa_pet_reply(message):
    user_id = message.chat.id
    wish_details = str(message.text)
    if wish_details == 'Cat' or wish_details == 'Dog' or wish_details == 'Any':
        change_santa_pet(user_id, wish_details)
        clean_santa_conversation(user_id)
        send_msg(user_id, REPLICA_CHANGE_ACCEPTED)
    else:
        send_msg(user_id, REPLICA_INCORRECT_ANSWER)
        send_msg(user_id, REPLICA_Q3_2, pet_santa_recipient_kb)


@bot.message_handler(content_types=['text'])
def unknown_message(message):
    user_id = message.chat.id
    lang = message.from_user.language_code
    logging.debug("Got unknown message: " + str(message.text))
    logging.debug(message)
    send_msg(user_id, REPLICA_UNKNOWN_MESSAGE)


# Run chat-bot
bot.polling(none_stop=True, interval=0)

