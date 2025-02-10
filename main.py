import telebot
from telebot import types
import os
import csv
from datetime import datetime

# Замените на свой токен
BOT_TOKEN = '7601944112:AAHtFO2nmERYQ-TgubfvlOgXJM0FLoe1Zlc'
bot = telebot.TeleBot(BOT_TOKEN)

# Путь к папке с картинками и файлами
SOURCES_FOLDER = 'sources'
STATS_FILE = os.path.join(SOURCES_FOLDER, 'stats.csv')

# Правильные ответы (замените на правильные)
CORRECT_ANSWERS = {
    '1': '1.3',
    '2': '0.01',
    '3': '0.1',
    '4': '3.78',
    '5': '1.44',
    '6': '1.2',
    '7': '-0.3',
    '8': '1',
    '9': '2',
    '10': '2',
    '11': 'ac'
}

# Состояния пользователя
user_states = {}

# --- Функция для записи в CSV ---
def record_stats(date, name, lesson_id, task_id, user_answer, correct_answer, mark):
    # Создаем папку, если её нет
    if not os.path.exists(SOURCES_FOLDER):
        os.makedirs(SOURCES_FOLDER)

    # Определяем, нужно ли писать заголовок
    file_exists = os.path.isfile(STATS_FILE)

    with open(STATS_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['date', 'name', 'lesson_id', 'task_id', 'user_answer', 'correct_answer', 'mark']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Записываем заголовок, если файл новый

        writer.writerow({
            'date': date,
            'name': name,
            'lesson_id': lesson_id,
            'task_id': task_id,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'mark': mark
        })

# --- Обработчики команд ---
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text="#1", callback_data='lesson_1')
    markup.add(item1)
    bot.send_message(message.chat.id, "Привет, {0.first_name}! Выбери номер занятия по основам статистики, ОТ которого ты хотел(а) бы получить домашнее задание".format(message.from_user), reply_markup=markup)

# --- Обработчики callback-запросов (нажатия на кнопки) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'lesson_1':
        # Отправляем картинку
        try:
            with open(os.path.join(SOURCES_FOLDER, 'hw1.png'), 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo)
        except FileNotFoundError:
            bot.send_message(call.message.chat.id, "К сожалению, изображение не найдено.")

        # Предлагаем выбрать задание
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton(text="#1", callback_data='task_1')
        item2 = types.InlineKeyboardButton(text="#2", callback_data='task_2')
        item3 = types.InlineKeyboardButton(text="#3", callback_data='task_3')
        item4 = types.InlineKeyboardButton(text="#4", callback_data='task_4')
        item5 = types.InlineKeyboardButton(text="#5", callback_data='task_5')
        item6 = types.InlineKeyboardButton(text="#6", callback_data='task_6')
        item7 = types.InlineKeyboardButton(text="#7", callback_data='task_7')
        item8 = types.InlineKeyboardButton(text="#8", callback_data='task_8')
        item9 = types.InlineKeyboardButton(text="#9", callback_data='task_9')
        item10 = types.InlineKeyboardButton(text="#10", callback_data='task_10')
        item11 = types.InlineKeyboardButton(text="#11", callback_data='task_11')
        back_button = types.InlineKeyboardButton(text="Назад", callback_data='back_to_start')
        markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11)
        markup.add(back_button)
        bot.send_message(call.message.chat.id, "Выбери задание, ответ на которое хочешь ввести", reply_markup=markup)

    elif call.data in ['task_1', 'task_2', 'task_3', 'task_4', 'task_5', 'task_6', 'task_7', 'task_8', 'task_9', 'task_10', 'task_11']:
        task_number = call.data.split('_')[1]  # Извлекаем номер задания (1, 2 или 3)
        user_states[call.message.chat.id] = {'awaiting_answer': True, 'task_number': task_number}
        bot.send_message(call.message.chat.id, "Введите ответ:")

    elif call.data == 'back_to_start':
        start_message(call.message) # возвращаемся в исходное меню
        return

# --- Обработчик текстовых сообщений ---
@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    chat_id = message.chat.id
    if chat_id in user_states and user_states[chat_id].get('awaiting_answer', False):
        task_number = user_states[chat_id]['task_number']
        user_answer = message.text
        correct_answer = CORRECT_ANSWERS.get(task_number)
        lesson_id = '1'  # Занятие всегда #1 в данном коде
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name = message.from_user.first_name

        if correct_answer:
            if user_answer.lower().replace(',','.') == correct_answer:  # Сравниваем без учета регистра
                bot.send_message(chat_id, "Верно!")
                record_stats(date, name, lesson_id, task_number, user_answer, correct_answer, 1)
            else:
                bot.send_message(chat_id, "Неверно. Чтобы ввести ответ еще раз, выбери задание заново.")
                record_stats(date, name, lesson_id, task_number, user_answer, correct_answer, 1)
        else:
            bot.send_message(chat_id, "К сожалению, правильный ответ на это задание пока не задан.")

        # Сбрасываем состояние
        del user_states[chat_id]


# --- Запуск бота ---
if __name__ == '__main__':
    # Создаем папку sources, если ее нет
    if not os.path.exists(SOURCES_FOLDER):
        os.makedirs(SOURCES_FOLDER)

    # Если нет hw1.jpg, то создаем пустой файл (чтобы не было ошибки)
    if not os.path.exists(os.path.join(SOURCES_FOLDER, 'hw1.jpg')):
        open(os.path.join(SOURCES_FOLDER, 'hw1.jpg'), 'a').close()

    print("Бот запущен...")
    bot.polling(none_stop=True)