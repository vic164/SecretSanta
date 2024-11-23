import os
import random
import sqlite3
import logging


### Work with SQLITE ###
def create_db_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
    except sqlite3.Error as e:
        print(e)
        exit()
    return conn


def select_db_query(conn, query, val):
    cur = conn.cursor()
    cur.execute(query, (val,))
    rows = cur.fetchall()
    return rows


### Work with SECRET_SANTAS table ###
def get_santa_id(userid):
    """ Checking if user already registered (on /start command)"""
    result = []
    query = "SELECT SANTA_ID FROM SECRET_SANTAS WHERE STATUS = 'registered' AND USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    query_output = select_db_query(sqlite_conn, query, str(userid))
    sqlite_conn.close()
    logging.debug(query_output)
    for i in query_output:
        result.append(i[0])
    return result


def add_new_santa(user_data):
    """ Create new entry in the SECRET_SANTAS table """
    columns = "USER_ID,USERNAME,SANTA_TYPE,DETAILS,DONATION,SANTA_ID,STATUS"
    values = "?,?,?,?,?,?,?"
    query = "INSERT INTO SECRET_SANTAS (" + columns + ") values (" + values + ")"
    logging.debug(query)
    logging.debug(user_data)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, user_data)
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()


def remove_santa(userid):
    """ Remove all entries in SECRET_SANTAS for user (on /cancel command)"""
    query = "DELETE FROM SECRET_SANTAS WHERE USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, (userid,))
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()


def remove_secretsanta(userid):
    """ Remove ClassicSanta entry in SECRET_SANTAS for user (on /cancel command)"""
    query = "DELETE FROM SECRET_SANTAS WHERE SANTA_TYPE = 'ClassicSanta' AND USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, (userid,))
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()


def remove_petsanta(userid):
    """ Remove PetSanta entry in SECRET_SANTAS for user (on /cancel command)"""
    query = "DELETE FROM SECRET_SANTAS WHERE SANTA_TYPE = 'PetSanta' AND USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, (userid,))
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()


def update_santa_data(col, user_data):
    """ Update entry in SECRET_SANTAS to add details (for status = filling) """
    query = """UPDATE SECRET_SANTAS SET {c} = ? 
      WHERE STATUS = 'filling' AND USER_ID = ?""".format(c=col)
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, user_data)
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()

def update_santa_type(userid, value):
    update_santa_data("SANTA_TYPE", (value, str(userid)))


def update_santa_details(userid, value):
    update_santa_data("DETAILS", (value, str(userid)))


def update_santa_donate(userid, value):
    update_santa_data("DONATION", (value, str(userid)))


def update_santa_id(userid, value):
    update_santa_data("SANTA_ID", (value, str(userid)))


def update_santa_status(userid, value):
    update_santa_data("STATUS", (value, str(userid)))


def change_santa_wishes(userid, value):
    """ Change already registered entry """
    conditions = "STATUS = 'registered' and SANTA_TYPE = 'ClassicSanta'"
    query = """UPDATE SECRET_SANTAS SET DETAILS = ? WHERE {c} AND USER_ID = ?""".format(c=conditions)
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, (str(value), str(userid)))
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()


def change_santa_pet(userid, value):
    """ Change already registered entry """
    conditions = "STATUS = 'registered' and SANTA_TYPE = 'PetSanta'"
    query = """UPDATE SECRET_SANTAS SET DETAILS = ? WHERE {c} AND USER_ID = ?""".format(c=conditions)
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, (str(value), str(userid)))
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()


def get_santa_type(userid):
    """ Check which SantaType was set in entry that filling in progress 
    (for ask_details step (if PetSanta - ask which pet, else - ask wishes)) 
    """
    query = "SELECT SANTA_TYPE FROM SECRET_SANTAS WHERE STATUS = 'filling' and USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    query_output = select_db_query(sqlite_conn, query, userid)
    sqlite_conn.close()
    logging.debug(query_output)
    result = query_output[0][0] if query_output else ''
    return result


def get_already_registered_santa_type(userid):
    """ Check which SantaType was set in already completed 
    (for ask if user wants to register second time)) 
    """
    query = "SELECT SANTA_TYPE FROM SECRET_SANTAS WHERE STATUS = 'registered' and USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    query_output = select_db_query(sqlite_conn, query, userid)
    sqlite_conn.close()
    logging.debug(query_output)
    result = query_output[0][0] if query_output else ''
    return result


def get_santa_name(userid):
    """ Get username from already completed entry in SECRET_SANTAS (second registration)"""
    query = "SELECT USERNAME from SECRET_SANTAS WHERE STATUS = 'registered' and USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    query_output = select_db_query(sqlite_conn, query, userid)
    sqlite_conn.close()
    logging.debug(query_output)
    result = query_output[0][0] if query_output else ''
    return result


def get_classicsanta_data(userid, parameter):
    conditions = "SANTA_TYPE = 'ClassicSanta' and STATUS = 'registered'"
    query = "SELECT {p} from SECRET_SANTAS WHERE {c} and USER_ID = ?".format(
            p=parameter, c=conditions)
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    query_output = select_db_query(sqlite_conn, query, userid)
    sqlite_conn.close()
    logging.debug(query_output)
    result = query_output[0][0] if query_output else ''
    return result


def get_petsanta_data(userid, parameter):
    conditions = "SANTA_TYPE = 'PetSanta' and STATUS = 'registered'"
    query = "SELECT {p} from SECRET_SANTAS WHERE {c} and USER_ID = ?".format(
            p=parameter, c=conditions)
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    query_output = select_db_query(sqlite_conn, query, userid)
    sqlite_conn.close()
    logging.debug(query_output)
    result = query_output[0][0] if query_output else ''
    return result


def check_santa_registered(userid, santa_type):
    query = "SELECT * FROM SECRET_SANTAS WHERE STATUS = 'registered' AND SANTA_TYPE = ? AND USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, (str(santa_type), str(userid)))
    query_output = cur.fetchall()
    sqlite_conn.close()
    logging.debug(query_output)
    result = True if query_output else False
    return result


def remove_filling_entries(userid):
    query = "DELETE FROM SECRET_SANTAS WHERE STATUS = 'filling' AND USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, (str(userid),))
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()

### Work with CONVERSATION_HISTORY table ###
def get_conversation_step(userid):
    query = "SELECT CONVERSATION_STEP FROM CONVERSATION_HISTORY WHERE USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    query_output = select_db_query(sqlite_conn, query, userid)
    sqlite_conn.close()
    result = query_output[0][0] if query_output else ''
    return result


def new_santa_conversation(userid, stepname):
    query = "INSERT INTO CONVERSATION_HISTORY (USER_ID,CONVERSATION_STEP) values (?,?)"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    user_data = (str(userid), str(stepname))
    cur.execute(query, user_data)
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()


def update_santa_conversation(userid, stepname):
    user_exist = get_conversation_step(userid)
    if not user_exist:
        new_santa_conversation(userid, stepname)
        return
    query = "UPDATE CONVERSATION_HISTORY SET CONVERSATION_STEP = ? WHERE USER_ID = ?"
    logging.debug(query)
    logging.debug("UserID: " + str(userid))
    logging.debug("New step name: " + str(stepname))
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, (str(stepname), str(userid)))
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()


def clean_santa_conversation(userid):
    query = "DELETE FROM CONVERSATION_HISTORY WHERE USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, (userid,))
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()


### GENERATOR SANTA ID ###
def generate_santa_id():
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    while True:
        # Generate a random 4-digit Santa ID
        santa_id = str(random.randint(1000, 9999))
        # Check if the ID already exists in the database
        query = "SELECT COUNT(*) FROM SECRET_SANTAS WHERE SANTA_ID like ?"
        query_output = select_db_query(sqlite_conn, query, santa_id)
        cur = sqlite_conn.cursor()
        cur.execute(query, ("%-" + santa_id,))
        count = cur.fetchone()[0]
        cur.close()
        # If ID does not exist, return it
        if count == 0:
            sqlite_conn.close()
            return santa_id

### Language support ###
def new_user_lang(userid):
    user_already_saved = get_user_lang(userid)
    if user_already_saved:
        logging.debug("Already known user")
        return
    query = "INSERT INTO SANTA_LANG (USER_ID, LANGUAGE) values (?,?)"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, (str(userid), 'en'))
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()


def get_user_lang(userid):
    query = "SELECT LANGUAGE FROM SANTA_LANG WHERE USER_ID = ?"
    #logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    query_output = select_db_query(sqlite_conn, query, str(userid))
    sqlite_conn.close()
    logging.debug(query_output)
    result = query_output[0][0] if query_output else ''
    return result


def update_user_lang(userid, lang):
    query = "UPDATE SANTA_LANG SET LANGUAGE = ? WHERE USER_ID = ?"
    logging.debug(query)
    home_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_file = os.path.join(home_dir, '_db', 'TG_SERVICE.db')
    sqlite_conn = create_db_connection(sqlite_file)
    cur = sqlite_conn.cursor()
    cur.execute(query, (lang, str(userid)))
    cur.close()
    sqlite_conn.commit()
    sqlite_conn.close()

