import telebot
from telebot import types
from datetime import datetime, timedelta
import threading
import time

# Вставьте ваш токен
TOKEN = "7290853383:AAGY2Q2YAtM8ZjN8qa7VQnus7gAi0o3tLCo"
bot = telebot.TeleBot(TOKEN)

# Хранилище задач
tasks = {}


# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я помогу запоминать ваши дела. Используй /add, чтобы добавить задачу, или /help для списка команд."
    )


# Команда /help
@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(
        message.chat.id,
        "/add [задача] [время] - добавить напоминание (например: /add Купить хлеб 15:30)\n"
        "/list - показать все задачи\n"
        "/delete [номер] - удалить задачу по номеру из списка"
    )


# Команда /add
@bot.message_handler(commands=['add'])
def add_task(message):
    try:
        user_id = message.chat.id
        text = message.text[5:].strip()
        task, task_time = text.rsplit(' ', 1)
        reminder_time = datetime.strptime(task_time, "%H:%M").time()

        # Сохраняем задачу
        if user_id not in tasks:
            tasks[user_id] = []
        tasks[user_id].append((task, reminder_time))

        bot.send_message(user_id, f"Задача '{task}' добавлена на {task_time}.")
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат. Используй: /add Задача HH:MM")


# Команда /list
@bot.message_handler(commands=['list'])
def list_tasks(message):
    user_id = message.chat.id
    if user_id in tasks and tasks[user_id]:
        response = "Ваши задачи:\n"
        for i, (task, task_time) in enumerate(tasks[user_id], 1):
            response += f"{i}. {task} в {task_time.strftime('%H:%M')}\n"
        bot.send_message(user_id, response)
    else:
        bot.send_message(user_id, "У вас нет задач.")


# Команда /delete
@bot.message_handler(commands=['delete'])
def delete_task(message):
    try:
        user_id = message.chat.id
        task_number = int(message.text[8:].strip()) - 1

        if user_id in tasks and 0 <= task_number < len(tasks[user_id]):
            removed_task = tasks[user_id].pop(task_number)
            bot.send_message(user_id, f"Задача '{removed_task[0]}' удалена.")
            if not tasks[user_id]:
                del tasks[user_id]
        else:
            bot.send_message(user_id, "Неверный номер задачи.")
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат. Используй: /delete [номер задачи]")


# Фоновая проверка задач
def task_checker():
    while True:
        now = datetime.now().time()
        for user_id in list(tasks.keys()):
            for task, task_time in tasks[user_id]:
                if task_time <= now:
                    bot.send_message(user_id, f"Напоминание: {task}")
                    tasks[user_id].remove((task, task_time))
            if not tasks[user_id]:
                del tasks[user_id]
        time.sleep(60)


# Запуск фонового потока
threading.Thread(target=task_checker, daemon=True).start()

# Запуск бота
bot.polling()
