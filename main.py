import telebot
import toml
from md_image import get_image_from_md
from manage_data import read_json_data
import os
from telebot.util import smart_split


def get_telegram_creds(path: str = 'config_secret.toml') -> tuple[int, str]:
    """Подключаемся по токену"""
    secret = toml.load(path)['telegram-creds']
    return secret['api_id'], secret['api_hash']


api_id, api_hash = get_telegram_creds()
bot = telebot.TeleBot(f'{api_id}:{api_hash}', parse_mode=None)

# TODO: global reduce usage of varibles
dir_path = os.path.dirname(os.path.realpath(__file__))
json_full_path = os.path.join(dir_path, "data.json")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = markup_format_level_1()
    bot.send_message(
        message.chat.id, "Приветствуем в библиариуме, библиотеке о мире Warhammer40k! О чём вы хотите узнать?",
        reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data in ["lore"])
def process_callback_2(query):
    markup = markup_format_level_2()
    bot.send_message(
        query.message.chat.id, "Выберите фракцию", reply_markup=markup)
    bot.answer_callback_query(query.id)
    pass


# TODO:
#   1) read json (validate on read) saved data before starting telegram bot polling loop
#   2) store data in memory (except content of .md docs)
#   3) check if sys paths (to .md docs) specified in json data actually exist -- fail if not
#   4) start bot
#   5) when user request info about wh40k <factions, lore, ...>
#       -> read content of matching *.md doc to memory
#   6) convert markdown to md telegram representation (configurable?) <== prepare response
#   7) find all pics (if any) and send them with already prepared response


def markup_format_level_1():
    """Разметка для первого уровня общения с ботом"""
    markup = telebot.types.InlineKeyboardMarkup()
    but_lore = telebot.types.InlineKeyboardButton(
        'Лор вселенной', callback_data='lore')
    but_books = telebot.types.InlineKeyboardButton(
        'Книги по вселенной', callback_data='books')
    markup.row(but_lore)
    markup.row(but_books)
    return markup


def markup_format_level_2():
    '''Разметка для второго уровня общения с ботом'''
    data = read_json_data(json_full_path)
    factions = []
    for x in data["things"]:
        if x["category"] == "factions":
            factions.append(x["content"]["name"])
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for x in factions:
        markup.add(telebot.types.InlineKeyboardButton(x, callback_data=x))
    return markup


@bot.message_handler(commands=["factions"])
def wh40k_factions(message):
    data = read_json_data(json_full_path)
    factions = []
    for x in data["things"]:
        if x["category"] == "factions":
            factions.append(x["content"]["name"])

    bot.reply_to(message, ", ".join(factions))
    bot.send_message(
        message.chat.id, "такие вот фракции крч...")


def search_faction(db: dict, name: str) -> tuple[bool, str | None]:
    for item in db["things"]:
        content = item["content"]
        if item["category"] == "factions" and (
                content["name"]).lower() == name.lower():
            return True, content["md_doc_path"]
    return False, None


def read_md(path: str) -> str:
    """Чтение markdown файла"""
    with open(path, "r", encoding='utf-8') as file:
        text = file.read()
        return text


@bot.message_handler(commands=["faction"])
def faction(message):
    data = message.text
    faction_name: str = data.removeprefix("/faction ")
    db = read_json_data(json_full_path)
    found, md_path = search_faction(db, faction_name)
    if not found:
        bot.reply_to(message, f"Фракция: {faction_name} не найдена")
    else:
        doc = read_md(os.path.join(dir_path, md_path))
        messages = smart_split(text=doc)
        for msg in messages:
            bot.reply_to(message, msg, parse_mode="markdown")


@bot.message_handler(content_types=["text"])
def any_text_message(message):
    bot.reply_to(message,
                 "Связь с астрономиконом слишком слабая "
                 "для получения обычных сообщений! Воспользуйтесь имеющимися "
                 "вариантами отправки.")
    markup = markup_format_level_1()
    bot.send_message(
        message.chat.id, "О чём вы хотите узнать?", reply_markup=markup)


def get_assoc_images(path: str = "data/factions/necrons/necrons_race.md"):
    with open(path, "r", encoding='utf-8') as file:
        text = file.read()
        return get_image_from_md(text)


if __name__ == "__main__":
    # read_json_data(json_full_path)
    bot.infinity_polling()
