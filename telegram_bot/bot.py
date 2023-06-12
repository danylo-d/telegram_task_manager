import os

from dotenv import load_dotenv
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware

load_dotenv(".env")
API_TOKEN = os.getenv("API_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    """
    Handler function for the /start command.
    Sends a welcome message to the user.
    """
    await message.reply(
        "Hi, I'm a task management bot. "
        "For a list of available commands, type /help."
    )


@dp.message_handler(commands=["help"])
async def send_help(message: types.Message):
    """
    Handler function for the /help command.
    Sends a help message with a list of available commands to the user.
    """
    help_message = """
    List of available commands:
        /create <title> <description> <due_date> - creating a new task. Date format: YYYY-MM-DD.
        /list - display the list of all tasks.
        /view <task_id> - view a specific task by its identifier.
        /update <task_id> <new_title> - update task title.
        /complete <task_id> - mark the task as completed.
        /delete <task_id> - deleting a task.
    """
    await message.reply(help_message)


@dp.message_handler(commands=["create"])
async def create_task(message: types.Message):
    """
    Handler function for the /create command.
    Creates a new task based on the provided information.
    """
    try:
        command_parts = message.text.split(" ")
        title = command_parts[1]
        description = " ".join(command_parts[2:-1])
        due_date = command_parts[-1]

        payload = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "completed": False,
        }

        response = requests.post(API_BASE_URL, json=payload)

        if response.status_code == 201:
            await message.reply("The task has been successfully created.")
        else:
            await message.reply("Failed to create a task.")
    except IndexError:
        await message.reply(
            "Incorrect entry of the command /create. Example: /create <title> <description> <due_date>"
        )


@dp.message_handler(commands=["list"])
async def list_tasks(message: types.Message):
    """
    Handler function for the /list command.
    Retrieves and displays the list of all tasks.
    """
    response = requests.get(API_BASE_URL)

    if response.status_code == 200:
        tasks = response.json()
        if tasks:
            tasks_text = "\n\n".join(
                [
                    f'{task["id"]}. {task["title"]} ({task["due_date"]})'
                    for task in tasks
                ]
            )
            await message.reply(f"Task List:\n\n{tasks_text}")
        else:
            await message.reply("The task list is empty.")
    else:
        await message.reply("Failed to get task list.")


@dp.message_handler(commands=["view"])
async def view_task(message: types.Message):
    """
    Handler function for the /view command.
    Retrieves and displays information about a specific task.
    """
    try:
        task_id = int(message.text.split(" ")[1])

        response = requests.get(API_BASE_URL + f"{task_id}/")

        if response.status_code == 200:
            task = response.json()
            task_text = (
                f"Task {task['id']}:\n\n"
                f"Title: {task['title']}\n"
                f"Description: {task['description']}\n"
                f"Due date: {task['due_date']}\n"
                f"Status: {'Done' if task['completed'] else 'Not done.'}"
            )
            await message.reply(task_text)
        elif response.status_code == 404:
            await message.reply("Task not found.")
        else:
            await message.reply("Failed to get task information.")
    except IndexError:
        await message.reply(
            "Incorrect entry of the /view command. Example: /view <task_id>"
        )


@dp.message_handler(commands=["update"])
async def update_task(message: types.Message):
    """
    Handler function for the /update command.
    Updates the title of a specific task.
    """
    try:
        command_parts = message.text.split(" ")
        task_id = int(command_parts[1])
        new_title = command_parts[2]

        payload = {"title": new_title}

        response = requests.patch(API_BASE_URL + f"{task_id}/", json=payload)

        if response.status_code == 200:
            await message.reply("The task header has been successfully updated.")
        elif response.status_code == 404:
            await message.reply("Task not found.")
        else:
            await message.reply("Failed to update task header.")
    except IndexError:
        await message.reply(
            "Incorrect entry of the /update command. Example: /update <task_id> <new_title>"
        )


@dp.message_handler(commands=["complete"])
async def complete_task(message: types.Message):
    """
    Handler function for the /complete command.
    Marks a specific task as completed.
    """
    try:
        task_id = int(message.text.split(" ")[1])

        payload = {"completed": True}

        response = requests.patch(API_BASE_URL + f"{task_id}/", json=payload)

        if response.status_code == 200:
            await message.reply("The task is marked as completed.")
        elif response.status_code == 404:
            await message.reply("Task not found.")
        else:
            await message.reply("It was not possible to mark the task as completed.")
    except IndexError:
        await message.reply(
            "Incorrect entry of the command /complete. Example: /complete <task_id>"
        )


@dp.message_handler(commands=["delete"])
async def delete_task(message: types.Message):
    """
    Handler function for the /delete command.
    Deletes a specific task.
    """
    try:
        task_id = int(message.text.split(" ")[1])

        response = requests.delete(API_BASE_URL + f"{task_id}/")

        if response.status_code == 204:
            await message.reply("The task has been successfully deleted.")
        elif response.status_code == 404:
            await message.reply("Task not found.")
        else:
            await message.reply("The task could not be deleted.")
    except IndexError:
        await message.reply(
            "Incorrect entry of the command /delete. Example: /delete <task_id>"
        )


if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
