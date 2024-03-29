import telebot
import toml
from data_provider import DataProvider
from telebot.util import smart_split
from data_helpers import get_directory_realpath


# TODO:
#   - check if sys paths (to .md docs) specified in json data actually exist -- fail if not


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
    """Answer start command"""
    bot.send_message(
        message.chat.id,
        "Приветствуем в библиариуме, библиотеке о мире Warhammer40k! О чём вы хотите узнать?",
        reply_markup=markup_format_level_1()
    )


@bot.callback_query_handler(lambda query: query.data == "lore")
def answer_query_lore(query):
    """Answer button lore"""
    bot.send_message(
        query.message.chat.id, "Выберите фракцию", reply_markup=markup_format_level_2())
    bot.answer_callback_query(query.id)


@bot.callback_query_handler(lambda query: query.data in provider.get_items_names_by_category('factions'))
def answer_query_lore(query):
    """Give info about chosen faction"""
    paths_dict = provider.collect_paths('factions')
    faction_name = query.data
    if faction_name in paths_dict.keys():
        updated_text, images = provider.get_md_for_telegram(
            'factions', faction_name)
        messages = smart_split(updated_text)
        for msg in messages:
            bot.send_message(query.message.chat.id, msg, parse_mode="markdown")

        for alt_caption, path in images:
            bot.send_photo(query.message.chat.id, photo=open(
                path, 'rb'), caption=alt_caption)
    else:
        bot.reply_to(
            query.message, f"Не найдена фракция: {faction_name}\nНевозможно! Быть может архивы неполные...")
    bot.answer_callback_query(query.id)
    bot.send_message(query.message.chat.id, "О чём вы ещё хотите узнать?",
                     reply_markup=markup_format_level_1())


@bot.callback_query_handler(lambda query: query.data == "books")
def answer_query_books(query):
    """Give info about books to read"""
    updated_text, images = provider.get_md_for_telegram(
        'books', 'книги по вселенной')
    messages = smart_split(updated_text)

    for msg in messages:
        bot.send_message(query.message.chat.id, msg, parse_mode="markdown")

    for alt_caption, path in images:
        bot.send_document(query.message.chat.id, document=open(
            path, 'rb'), caption=alt_caption)

    bot.answer_callback_query(query.id)
    bot.send_message(query.message.chat.id, "О чём вы ещё хотите узнать?",
                     reply_markup=markup_format_level_1())


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
        markup.add(telebot.types.InlineKeyboardButton(
            x.title(), callback_data=x))
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
    """fun just in case: for the future"""
    data = message.text
    faction_name: str = data.removeprefix("/faction ")
    paths_dict = provider.collect_paths('factions')

    # if specified faction exists in keys - continue
    if faction_name in paths_dict.keys():
        updated_text, images = provider.get_md_for_telegram(
            'factions', faction_name)
        messages = smart_split(updated_text)

        for msg in messages:
            bot.reply_to(message, msg, parse_mode="markdown")

        for alt_caption, path in images:
            bot.send_photo(message.chat.id, photo=open(
                path, 'rb'), caption=alt_caption)
    else:
        bot.reply_to(message, f"Фракция: {faction_name} не найдена")


@bot.message_handler(content_types=["text"])
def any_text_message(message):
    """Answer any text, only use input buttons for the time being"""
    bot.reply_to(message,
                 "Связь с астрономиконом слишком слабая "
                 "для получения обычных сообщений! Воспользуйтесь имеющимися "
                 "вариантами отправки.")
    bot.send_message(message.chat.id, "О чём вы хотите узнать?",
                     reply_markup=markup_format_level_1())


if __name__ == "__main__":
    bot.infinity_polling()
