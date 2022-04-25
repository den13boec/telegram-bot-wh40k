import telebot
import toml
from md_image import get_image_from_md
from manage_data import read_json_data
import os


def get_telegram_creds(path: str = 'config_secret.toml') -> tuple[int, str]:
    secret = toml.load(path)['telegram-creds']
    return secret['api_id'], secret['api_hash']


api_id, api_hash = get_telegram_creds()
bot = telebot.TeleBot(f'{api_id}:{api_hash}', parse_mode=None)

# TODO: global reduce usage of varibles
dir_path = os.path.dirname(os.path.realpath(__file__))
json_full_path = os.path.join(dir_path, "data.json")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = markup_format()
    bot.send_message(
        message.chat.id, "Приветствуем в библиариуме, библиотеке о мире Warhammer40k! О чём вы хотите узнать?", reply_markup=markup)


def markup_format():
    markup = telebot.types.InlineKeyboardMarkup()
    but_lore = telebot.types.InlineKeyboardButton(
        'Лор вселенной', callback_data='lore')
    but_books = telebot.types.InlineKeyboardButton(
        'Книги по вселенной', callback_data='books')
    markup.row(but_lore)
    markup.row(but_books)
    return (markup)


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


@bot.message_handler(content_types=["text"])
def any_text_message(message):
    bot.reply_to(message, "Связь с астрономиконом слишком слабая для получения обычных сообщений! Воспользуйтесь имеющимися вариантами отправки.")
    markup = markup_format()
    bot.send_message(
        message.chat.id, "О чём вы хотите узнать?", reply_markup=markup)


def get_assoc_images(path: str = "data/factions/necrons/necrons_race.md"):
    with open(path, "r", encoding='utf-8') as file:
        text = file.read()
        return get_image_from_md(text)


if __name__ == "__main__":
    # read_json_data(json_full_path)
    bot.infinity_polling()
