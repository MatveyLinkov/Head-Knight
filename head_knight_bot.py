import logging
from telegram.ext import Updater, CommandHandler
import json
from data import db_session
from data.users import User

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

TOKEN = '5347393184:AAFInmMpPAeRSvLZzqAwuyZz9jwec3b8Nls'


def login(update, context):
    try:
        name = update.message.text.split(' ')[1]
        password = ' '.join(update.message.text.split(' ')[2:])
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == name).first()
        if not user:
            user = db_sess.query(User).filter(User.nickname == name).first()
        if user and user.check_password(password):
            with open('telegram_users.json', 'r', encoding='utf-8') as loaded_file:
                data = json.load(loaded_file)
                with open('telegram_users.json', 'w', encoding='utf-8') as dumped_file:
                    if user.nickname not in [el['nickname'] for el in data]:
                        data.append({
                            'last_name': update.message.from_user.last_name,
                            'first_name': update.message.from_user.first_name,
                            "username": update.message.from_user.username,
                            'user_id': update.message.from_user.id,
                            'nickname': user.nickname
                        })
                        json.dump(data, dumped_file)
            update.message.reply_text('Вы успешно авторизировась.')
        else:
            update.message.reply_text('Неверное имя пользователя или пароль.')
    except Exception:
        update.message.reply_text('Убедитесь в правильности запроса!\n'
                                  '/login <nickname> <password>')


def logout(update, context):
    with open('telegram_users.json', 'r', encoding='utf-8') as loaded_file:
        data = json.load(loaded_file)
        if update.message.from_user.id in [el['user_id'] for el in data]:
            data.pop(data.index(
                [el for el in data if el['user_id'] == update.message.from_user.id][0]))
            with open('telegram_users.json', 'w', encoding='utf-8') as dumped_file:
                json.dump(data, dumped_file)
                update.message.reply_text('Вы вышли из профиля.')
        else:
            update.message.reply_text('Вы не авторизированы!')


def nickname(update, context):
    with open('telegram_users.json', 'r', encoding='utf-8') as loaded_file:
        data = json.load(loaded_file)
        if update.message.from_user.id in [el['user_id'] for el in data]:
            update.message.reply_text(list(filter(
                lambda x: x['user_id'] == update.message.from_user.id, data))[0]['nickname'])
        else:
            update.message.reply_text('Войдите в свой аккаунт!')


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('login', login, pass_user_data=True))
    dp.add_handler(CommandHandler('logout', logout, pass_user_data=True))
    dp.add_handler(CommandHandler('nickname', nickname, pass_user_data=True))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    db_session.global_init('db/knight_users.sqlite')
    main()
