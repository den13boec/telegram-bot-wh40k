import telebot
import toml


def get_telegram_creds(path: str = 'config_secret.toml') -> tuple[int, str]:
    secret = toml.load(path)['telegram-creds']
    return secret['api_id'], secret['api_hash']


api_id, api_hash = get_telegram_creds()
bot = telebot.TeleBot(f'{api_id}:{api_hash}', parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


bot.infinity_polling()
