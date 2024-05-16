import logging
import os
import re
import paramiko
import psycopg2

from dotenv import load_dotenv
from pathlib import Path
from psycopg2 import Error
from telegram import Update, ForceReply, update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


TOKEN = os.getenv('TOKEN')

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def find_phone_numberCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'


def find_emailCommand(update: Update, context):
    update.message.reply_text("Введите текст для поиска email-адресов: ")
    return 'find_email'


def verify_passwordCommand(update: Update, context):
    update.message.reply_text("Введите пароль для проверки")
    return 'verify_password'


def get_releaseCommand(update: Update, context):
    return 'get_release'


def get_unameCommand(update: Update, context):
    return 'get_uname'


def get_uptimeCommand(update: Update, context):
    return 'get_uptime'


def get_dfCommand(update: Update, context):
    return 'get_df'


def get_freeCommand(update: Update, context):
    return 'get_free'


def get_mpstatCommand(update: Update, context):
    return 'get_mpstat'


def get_wCommand(update: Update, context):
    return 'get_w'


def get_authsCommand(update: Update, context):
    return 'get_auths'


def get_criticalCommand(update: Update, context):
    return 'get_critical'


def get_psCommand(update: Update, context):
    return 'get_ps'


def get_ssCommand(update: Update, context):
    return 'get_ss'


def get_servicesCommand(update: Update, context):
    return 'get_services'


def get_apt_listCommand(update: Update, context):
    update.message.reply_text("Для вывода всех пакетов введите \"all\", для поиска определенного введите его название: ")
    return 'get_apt_list'


def get_repl_logsCommand(update: Update, context):
    return 'get_repl_logs'


def get_emailsCommand(update: Update, context):
    return 'get_emails'


def get_phone_numbersCommand(update: Update, context):
    return 'get_phone_numbers'


def find_phone_number(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:\+7|8)[ -]??\(?\d{3}\)?(?: |-)?\d{3}(?: |-)?\d{2}(?: |-)?\d{2}')

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return  # Завершаем выполнение функции

    context.user_data['phone_numbers'] = phoneNumberList #сохраняем номера под ключом phone_numbers

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'  # Записываем очередной номер

    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю

    update.message.reply_text("Записать найденные номера в базу данных? Введите \"Да\" или \"Нет\"")
    return 'writing_phone_numbers_to_db'


def writing_phone_numbers_to_db(update: Update, context):
    numbersList = context.user_data['phone_numbers']
    user_input = update.message.text

    if user_input == 'ДА' or user_input == 'Да' or user_input == 'да':
        if set_information_to_database(table='phonenumbers (number)', values=numbersList):
            update.message.reply_text('Данные успешно записаны')
        else:
            update.message.reply_text('Ошибка записи')

    return ConversationHandler.END


def find_email(update: Update, context):
    user_input = update.message.text

    emailRegex = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}')
    emailList = emailRegex.findall(user_input)

    if not emailList:
        update.message.reply_text('Email-адреса не найдены')
        return

    context.user_data['emails'] = emailList

    emailAddresses = ''
    for i in range(len(emailList)):
        emailAddresses += f'{i + 1}. {emailList[i]}\n'

    update.message.reply_text(emailAddresses)

    update.message.reply_text("Записать найденные адреса в базу данных? Введите \"Да\" или \"Нет\"")
    return 'writing_emails_to_db'


def writing_emails_to_db(update: Update, context):
    emailList = context.user_data['emails']
    user_input = update.message.text
    if user_input == 'ДА' or user_input == 'Да' or user_input == 'да':
        if set_information_to_database(table='emails (email)', values=emailList):
            update.message.reply_text('Данные успешно записаны')
        else:
            update.message.reply_text('Ошибка записи')

    return ConversationHandler.END


def verify_password(update: Update, context):
    user_input = update.message.text

    passwordRegex = re.compile(r'.*(?=.{8,})(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*()]).*')
    verifiedPassword = passwordRegex.fullmatch(user_input)

    if verifiedPassword:
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')

    return ConversationHandler.END


def get_information_from_remote_server(command: str) -> str:

    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    return data


def get_release(update: Update, context):
    update.message.reply_text(get_information_from_remote_server(command='lsb_release -a'))


def get_uname(update: Update, context):
    update.message.reply_text(get_information_from_remote_server(command='uname -a'))


def get_uptime(update: Update, context):
    update.message.reply_text(get_information_from_remote_server(command='uptime'))


def get_df(update: Update, context):
    update.message.reply_text(get_information_from_remote_server(command='df'))


def get_free(update: Update, context):
    update.message.reply_text(get_information_from_remote_server(command='free -h'))


def get_mpstat(update: Update, context):
    update.message.reply_text(get_information_from_remote_server(command='mpstat'))


def get_w(update: Update, context):
    update.message.reply_text(get_information_from_remote_server(command='w'))


def get_auths(update: Update, context):
    update.message.reply_text(get_information_from_remote_server(command='last -10'))


def get_critical(update: Update, context):
    update.message.reply_text(
        get_information_from_remote_server(command='journalctl -r -p crit -n 5'))


def get_ps(update: Update, context):
    update.message.reply_text(get_information_from_remote_server(command='ps -ef | head -n 15'))


def get_ss(update: Update, context):
    update.message.reply_text(get_information_from_remote_server(command='ss -lntu'))


def get_services(update: Update, context):
    update.message.reply_text(
        get_information_from_remote_server(
            command='systemctl list-units --type=service | head -n 15'))


def get_apt_list(update: Update, context):
    user_input = update.message.text.strip()
    command = ''

    if user_input == 'all' or user_input == 'All' or user_input == 'ALL':
        command = 'dpkg -l | head -n 15'

    else:
        command = f'dpkg -l | grep {user_input} | head -n 15'
    
    update.message.reply_text(
            get_information_from_remote_server(command=command))


def get_repl_logs(update: Update, context):
    update.message.reply_text(
        get_information_from_remote_server(
            command='grep \"repl\" /var/log/postgresql/postgresql-14-main.log | tail'))


def get_emails(update: Update, context):
    update.message.reply_text(get_information_from_database(table='emails'))


def get_phone_numbers(update: Update, context):
    update.message.reply_text(get_information_from_database(table='phonenumbers'))


def get_information_from_database(table: str):

    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_DATABASE')

    connection = None
    cursor = None
    objectsList = []
    try:
        connection = psycopg2.connect(user=username,
                                      password=password,
                                      host=host,
                                      port=port,
                                      database=database)

        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table};")
        data = cursor.fetchall()
        for row in data:
            objectsList.append(row[1])
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    if not objectsList:
        update.message.reply_text('Данных нет')
        return

    objects = ''
    for i in range(len(objectsList)):
        objects += f'{i + 1}. {objectsList[i]}\n'  # Записываем очередной номер

    return objects


def set_information_to_database(table: str, values: list) -> bool:

    flag = False

    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_DATABASE')

    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(user=username,
                                      password=password,
                                      host=host,
                                      port=port,
                                      database=database)

        cursor = connection.cursor()
        values_str = ''
        for value in values:
            values_str += f'(\'{value}\'), '
        values_str = values_str[:-2]
        cursor.execute(f"INSERT INTO {table} VALUES {values_str};")
        connection.commit()
        logging.info("Команда успешно выполнена")
        flag = True
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
    return flag


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_numberCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'writing_phone_numbers_to_db': [MessageHandler(Filters.text & ~Filters.command, writing_phone_numbers_to_db)],
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_emailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'writing_emails_to_db': [MessageHandler(Filters.text & ~Filters.command, writing_emails_to_db)],
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(convHandlerGetAptList)

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
