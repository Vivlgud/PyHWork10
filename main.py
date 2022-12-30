from config import TOKEN

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging

import csv


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CHOICE, NAME, SURNAME, PHONE, FIND = range(5)

def start(update, _):
    update.message.reply_text(
        f'Привет, {update.effective_user.first_name}, это - телефонный справочник.\
    Выберите номер пункта меню или /cancel, для завершения работы.\n\n')
    update.message.reply_text(
        '1 - Добавить контакт; \n2 - Показать все контакты; \n3 - Поиск; \n4 - Выйти из справочника \n')
    return CHOICE

def choice(update, context):
    user = update.message.from_user
    logger.info("Выбор операции: %s: %s", user.first_name, update.message.text)
    user_choice = update.message.text
    if user_choice in '1,2,3,4':
        if user_choice == '1':
            update.message.reply_text('Введите фамилию -  ')
            return SURNAME
        if user_choice == '2':
            with open('phone.csv', 'r',encoding='UTF-8') as f:              
                for line in f:
                    line=line.replace(',','  ')
                    update.message.reply_text(f'{line}')
            update.message.reply_text(f'Вывод контактов завершен. Для продолжения работы нажмите /start')                  
            return ConversationHandler.END 
        if user_choice == '3':
            context.bot.send_message(update.effective_chat.id, 'Введите Фамилию или Имя для поиска:')
            return FIND
        if user_choice == '4':
            update.message.reply_text('Работа завершена, до свидания!')
            return ConversationHandler.END     
    else:
        update.message.reply_text('Ошибка ввода. Введите цифру операции.')


def surname(update, context):
    user = update.message.from_user
    logger.info("Пользователь ввел фамилию: %s: %s",
                user.first_name, update.message.text)
    get_data = update.message.text
    if get_data.isalpha():
        context.user_data['surname'] = get_data
        update.message.reply_text('Введите имя')
        return NAME
    else:
        update.message.reply_text('Ошибка. Вы ввели цифры')

def name(update, context):
    user = update.message.from_user
    logger.info("Пользователь ввел имя: %s: %s",
                user.first_name, update.message.text)
    get_data = update.message.text
    if get_data.isalpha():
        context.user_data['name'] = get_data
        update.message.reply_text('Введите номер телефона')
        return PHONE
    else:
        update.message.reply_text('Ошибка. Вы ввели цифры')

def phone(update, context):
    user = update.message.from_user
    logger.info("Пользователь номер: %s: %s",
                user.first_name, update.message.text)
    get_data = update.message.text
    if get_data.isdigit():
        context.user_data['phone'] = get_data
        surname = context.user_data.get('surname')
        name = context.user_data.get('name')
        phone=context.user_data.get('phone')
        data=[surname,name,phone]
        update.message.reply_text(f'Результат: {surname} {name} {phone}')
        update.message.reply_text(f'Контакт сохранен. Для продолжения работы нажмите /start')
        with open('phone.csv', 'a+',encoding='UTF-8', newline='\n') as f:
            writer = csv.writer(f)
            writer.writerow(data)
        return ConversationHandler.END

def find(update, context):
    with open('phone.csv', 'r',encoding='UTF-8') as f:              
                check=0
                for line in f:
                    if update.message.text in line:
                        check=1
                        line=line.replace(',','  ')
                        update.message.reply_text(f'{line}')
                if check==0:
                    update.message.reply_text(f'Поиск контактов завершен.Контакт не найден. Для продолжения работы нажмите /start')
    update.message.reply_text(f'Для продолжения работы нажмите /start')

    return ConversationHandler.END


def cancel(update, _):
    user = update.message.from_user
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    update.message.reply_text('Спасибо, до свидания!')
    return ConversationHandler.END


# запуск бота
if __name__ == '__main__':
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    conversation_handler = ConversationHandler(

        entry_points=[CommandHandler('start', start)],

        states={
            CHOICE: [MessageHandler(Filters.text, choice)],
            SURNAME: [MessageHandler(Filters.text, surname)],
            NAME: [MessageHandler(Filters.text, name)],
            PHONE: [MessageHandler(Filters.text, phone)],
            FIND: [MessageHandler(Filters.text, find)],
            },

        fallbacks=[CommandHandler('cancel', cancel)],)

    dispatcher.add_handler(conversation_handler)
    print('Start')
    updater.start_polling()
    updater.idle()