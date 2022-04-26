import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import json
from data import db_session
from data.users import User

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

TOKEN = '5347393184:AAFInmMpPAeRSvLZzqAwuyZz9jwec3b8Nls'

login_var = False
subscribe_var = False


def query_continuation(update, context):
    global login_var, subscribe_var
    if login_var:
        try:
            name = update.message.text.split(' ')[0]
            password = ' '.join(update.message.text.split(' ')[1:])
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == name).first()
            if not user:
                user = db_sess.query(User).filter(User.nickname == name).first()
            if user and user.check_password(password):
                with open('json_directory/telegram_users.json', 'r', encoding='utf-8') as\
                        loaded_file:
                    data = json.load(loaded_file)
                    with open('json_directory/telegram_users.json', 'w', encoding='utf-8') as \
                            dumped_file:
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
                                      '/login <email/nickname> <password>')
        login_var = False
    elif subscribe_var:
        respondent = update.message.text
        with open('json_directory/telegram_users.json', 'r', encoding='utf-8') as users_file:
            users = json.load(users_file)
            with open('json_directory/friends.json', 'r', encoding='utf-8') as loaded_friends:
                data_friends = json.load(loaded_friends)
                if respondent in data_friends:
                    with open('json_directory/friends.json', 'w', encoding='utf-8') as friends_file:
                        current_user = list(filter(
                            lambda x: x['user_id'] ==
                                      update.message.from_user.id, users))[0]['nickname']
                        if respondent not in data_friends[current_user]['subscriptions']:
                            data_friends[current_user]['subscriptions'] += [respondent]
                            data_friends[respondent]['subscribers'] += [current_user]
                            update.message.reply_text(f'Вы подписались на {respondent}')
                        else:
                            update.message.reply_text('Вы уже подписаны на данного пользователя.')
                        json.dump(data_friends, friends_file)
                else:
                    update.message.reply_text('Пользователь не найден.')
        subscribe_var = False
    else:
        update.message.reply_text('Ваш запрос не понятен.\n'
                                  'Для ознакомления с командами воспользуйтесь /help')


def help(update, context):
    update.message.reply_text('Команды:\n'
                              '/login - авторизация\n'
                              '/logout - выход из профиля\n'
                              '/subscribe - подписаться на пользователя\n'
                              '/subscribers - список подписчиков\n'
                              '/subscriptions - список подписок\n'
                              '/users - список пользователей\n'
                              '/project_info - информация о проекте\n'
                              '/github - ссылка на Github репозиторий')


def login(update, context):
    global login_var
    login_var = True
    update.message.reply_text('Отправьте свой адрес электронной почты или '
                              'имя пользователя и пароль. (<name> <password>)')


def logout(update, context):
    with open('json_directory/telegram_users.json', 'r', encoding='utf-8') as loaded_file:
        data = json.load(loaded_file)
        if update.message.from_user.id in [el['user_id'] for el in data]:
            data.pop(data.index(
                [el for el in data if el['user_id'] == update.message.from_user.id][0]))
            with open('json_directory/telegram_users.json', 'w', encoding='utf-8') as dumped_file:
                json.dump(data, dumped_file)
                update.message.reply_text('Вы вышли из профиля.')
        else:
            update.message.reply_text('Вы не авторизированы!')


def nickname(update, context):
    with open('json_directory/telegram_users.json', 'r', encoding='utf-8') as loaded_file:
        data = json.load(loaded_file)
        if update.message.from_user.id in [el['user_id'] for el in data]:
            update.message.reply_text(list(filter(
                lambda x: x['user_id'] == update.message.from_user.id, data))[0]['nickname'])
        else:
            update.message.reply_text('Войдите в свой аккаунт!')


def subscribe(update, context):
    global subscribe_var
    subscribe_var = True
    update.message.reply_text('Отправьте имя пользователя, на которого хотите подписаться.')


def subscribers(update, context):
    with open('json_directory/friends.json') as friends_file:
        friends = json.load(friends_file)
        with open('json_directory/telegram_users.json') as users_file:
            users = json.load(users_file)
            current_user = list(filter(lambda x: x['user_id'] == update.message.from_user.id,
                                       users))[0]['nickname']
            subscribers_list = friends[current_user]['subscribers']
            if subscribers_list:
                for subscriber in subscribers_list:
                    if current_user in friends[subscriber]['subscribers'] and \
                            subscriber in friends[current_user]['subscriptions']:
                        if list(filter(lambda x: x["nickname"] == subscriber, users)) and \
                                subscriber in [el['nickname'] for el in users]:
                            username = list(
                                filter(lambda x: x["nickname"] == subscriber, users))[0]["username"]
                            subscribers_list[subscribers_list.index(subscriber)] += \
                                f' - t.me/{username}'
                update.message.reply_text('\n'.join([f'Подписчики - {len(subscribers_list)}'] +
                                                    subscribers_list))
            else:
                update.message.reply_text('У вас нет подписчиков :(')


def subscriptions(update, context):
    with open('json_directory/friends.json') as friends_file:
        friends = json.load(friends_file)
        with open('json_directory/telegram_users.json') as users_file:
            users = json.load(users_file)
            current_user = list(filter(lambda x: x['user_id'] == update.message.from_user.id,
                                       users))[0]['nickname']
            subscriptions_list = friends[current_user]['subscriptions']
            if subscriptions_list:
                for subscription in subscriptions_list:
                    if current_user in friends[subscription]['subscriptions'] and \
                            subscription in friends[current_user]['subscribers']:
                        if list(filter(lambda x: x["nickname"] == subscription, users)):
                            username = list(
                                filter(lambda x: x["nickname"] ==
                                       subscription, users))[0]["username"]
                            subscriptions_list[subscriptions_list.index(subscription)] += \
                                f' - t.me/{username}'
                update.message.reply_text('\n'.join([f'Подписчики - {len(subscriptions_list)}'] +
                                                    subscriptions_list))
            else:
                update.message.reply_text('У вас нет подписок.')


def users(update, context):
    with open('json_directory/friends.json', 'r', encoding='utf-8') as loaded_file:
        data = json.load(loaded_file)
        update.message.reply_text('\n'.join([f'{user} - {len(data[user]["subscribers"])} subs'
                                             for user in data.keys()]))


def project_info(update, context):
    update.message.reply_text('Head Knight\n'
                              'Экшен игра, в которой действия разворачиваются в подземелье. '
                              'В ней игроку предстоит сразиться с монстрами. '
                              'В игре ещё много интересного!')


def github(update, context):
    update.message.reply_text('[Github](https://github.com/MatveyLinkov/Head-Knight_game)',
                              parse_mode='Markdown')


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    text_handler = MessageHandler(Filters.text & ~Filters.command, query_continuation)
    dp.add_handler(text_handler)
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('login', login))
    dp.add_handler(CommandHandler('logout', logout))
    dp.add_handler(CommandHandler('nickname', nickname))
    dp.add_handler(CommandHandler('subscribe', subscribe))
    dp.add_handler(CommandHandler('subscribers', subscribers))
    dp.add_handler(CommandHandler('subscriptions', subscriptions))
    dp.add_handler(CommandHandler('users', users))
    dp.add_handler(CommandHandler('project_info', project_info))
    dp.add_handler(CommandHandler('github', github))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    db_session.global_init('db/knight_users.sqlite')
    main()
