import telebot
import toml
from md_image import get_image_from_md


def get_telegram_creds(path: str = 'config_secret.toml') -> tuple[int, str]:
    secret = toml.load(path)['telegram-creds']
    return secret['api_id'], secret['api_hash']


api_id, api_hash = get_telegram_creds()
bot = telebot.TeleBot(f'{api_id}:{api_hash}', parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


def get_assoc_images(path: str = "data/factions/necrons/necrons_race.md"):
    with open(path, "r", encoding='utf-8') as file:
        text = file.read()
        return get_image_from_md(text)


if __name__ == "__main__":
    bot.infinity_polling()
