import telebot
import toml
from data_provider import DataProvider
import os
from telebot.util import smart_split
from data_helpers import get_directory_realpath

# TODO:
#   3) check if sys paths (to .md docs) specified in json data actually exist -- fail if not
#   4) bot behaviour


def get_telegram_creds(path: str = 'config_secret.toml') -> tuple[int, str]:
    """Connect to Telegram API via token"""
    secret = toml.load(path)['telegram-creds']
    return secret['api_id'], secret['api_hash']


api_id, api_hash = get_telegram_creds()
bot = telebot.TeleBot(f'{api_id}:{api_hash}', parse_mode=None)

dir_path = get_directory_realpath(__file__)
provider = DataProvider('data.json')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = markup_format_level_1()
    bot.send_message(
        message.chat.id,
        "Приветствуем в библиариуме, библиотеке о мире Warhammer40k! О чём вы хотите узнать?",
        reply_markup=markup
    )


@bot.callback_query_handler(lambda query: query.data == "lore")
def answer_query_lore(query):
    markup = markup_format_level_2()
    bot.send_message(
        query.message.chat.id, "Выберите фракцию", reply_markup=markup)
    bot.answer_callback_query(query.id)


def script_location():
    return os.path.dirname(os.path.realpath(__file__))


@bot.callback_query_handler(lambda query: query.data == "books")
def answer_query_books(query):
    updated_text, images = provider.get_md_for_telegram('books', 'книги по вселенной')
    messages = smart_split(updated_text)

    for msg in messages:
        bot.reply_to(query.message, msg, parse_mode="markdown")

    for alt_caption, path in images:
        bot.send_document(query.message.chat.id, document=open(path, 'rb'), caption=alt_caption)

    bot.answer_callback_query(query.id)


def markup_format_level_1():
    """Markup for first level of communication with bot"""
    markup = telebot.types.InlineKeyboardMarkup()
    but_lore = telebot.types.InlineKeyboardButton(
        'Лор вселенной', callback_data='lore')
    but_books = telebot.types.InlineKeyboardButton(
        'Книги по вселенной', callback_data='books')
    markup.row(but_lore)
    markup.row(but_books)
    return markup


def markup_format_level_2():
    """Markup for second level of communication with bot"""
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for x in provider.get_items_names_by_category('factions'):
        markup.add(telebot.types.InlineKeyboardButton(x, callback_data=x))
    return markup


# @bot.message_handler(commands=["factions"])
# def wh40k_factions(message):
#     data = provider.json_data
#     factions = []
#     for x in data["things"]:
#         if x["category"] == "factions":
#             factions.append(x["content"]["name"])
#
#     bot.reply_to(message, ", ".join(factions))
#     bot.send_message(
#         message.chat.id, "такие вот фракции крч...")


@bot.message_handler(commands=["faction"])
def faction(message):
    data = message.text
    faction_name: str = data.removeprefix("/faction ")
    paths_dict = provider.collect_paths('factions')

    # if specified faction exists in keys - continue
    if faction_name in paths_dict.keys():
        updated_text, images = provider.get_md_for_telegram('factions', faction_name)
        messages = smart_split(updated_text)

        for msg in messages:
            bot.reply_to(message, msg, parse_mode="markdown")

        for alt_caption, path in images:
            bot.send_photo(message.chat.id, photo=open(path, 'rb'), caption=alt_caption)
    else:
        bot.reply_to(message, f"Фракция: {faction_name} не найдена")


@bot.message_handler(content_types=["text"])
def any_text_message(message):
    bot.reply_to(message,
                 "Связь с астрономиконом слишком слабая "
                 "для получения обычных сообщений! Воспользуйтесь имеющимися "
                 "вариантами отправки.")
    markup = markup_format_level_1()
    bot.send_message(
        message.chat.id, "О чём вы хотите узнать?", reply_markup=markup)


if __name__ == "__main__":
    # read_json_data(json_full_path)
    bot.infinity_polling()
