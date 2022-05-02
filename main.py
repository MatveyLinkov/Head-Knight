import os
import json
from flask import Flask, render_template, redirect, request

from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.users import User
from forms.user import RegisterForm
from forms.login import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wtf-msi'
login_manager = LoginManager()
login_manager.init_app(app)


def user_avatar():
    avatar = '../static/avatars/JohnDoe.jpg'
    if isinstance(current_user, User):
        if os.path.isfile(f'static/avatars/{current_user.nickname}.jpg'):
            avatar = f'../static/avatars/{current_user.nickname}.jpg'
    return avatar


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return redirect('/home')


@app.route('/friends')
def friends():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    subs = 0
    ons = 0
    with open('json_directory/friends.json', 'r') as loaded_file:
        data = json.load(loaded_file)
        if isinstance(current_user, User):
            subs = len(data[current_user.nickname]['subscribers'])
            ons = len(data[current_user.nickname]['subscriptions'])
        list_of_nicknames = [x[0] for x in db_sess.query(User.nickname)]
        return render_template('friends.html', title='Друзья | Head-Knight',
                               user=user, avatar=user_avatar(),
                               spisok_nicknames=list_of_nicknames, users_subs=subs, users_ons=ons)


@app.route('/home')
def home():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    return render_template('home.html', title='Главная | Head-Knight',
                           avatar=user_avatar(), user=user, auth=False, home=True)


@app.route('/subscribe/<nickname>')
def subscribing(nickname):
    return redirect('/friends')


@app.route('/icon_changing', methods=["GET", "POST"])
def image_of_profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    if request.method == 'GET':
        return render_template('changing_image.html', title='Меняем картинку',
                               user=user, avatar=user_avatar())
    elif request.method == 'POST':
        encoded_string = request.files['file'].read()
        if str(encoded_string) == "b''":
            return redirect('/icon_changing')
        else:
            with open(f"static/avatars/{current_user.nickname}.jpg", "wb") as img:
                img.write(encoded_string)
            return redirect('/home')


@app.route('/community')
def community():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    return render_template('community.html', title="Сообщество | Head-Knight",
                           avatar=user_avatar(), user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('register.html', title='Регистрация | Head-Knight', auth=True,
                                   form=form, message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация | Head-Knight', auth=True,
                                   form=form, message='Электронная почта уже используется')
        elif db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html', title='Регистрация | Head-Knight', auth=True,
                                   form=form, message='Имя пользователя уже занято')
        elif form.nickname.data.count(' ') > 0:
            return render_template('register.html', title='Регистрация | Head-Knight', auth=True,
                                   form=form,
                                   message='Имя пользователя не должно содержать пробелов!')
        user = User()
        user.email = form.email.data
        user.nickname = form.nickname.data

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        with open('json_directory/friends.json', 'r', encoding='utf-8') as loaded_file:
            data = json.load(loaded_file)
            with open('json_directory/friends.json', 'w', encoding='utf-8') as dumped_file:
                data[form.nickname.data] = {'subscribers': [], 'subscriptions': []}
                json.dump(data, dumped_file)
        return redirect('/login')
    return render_template('register.html', title='Регистрация | Head-Knight', auth=True, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.login.data).first()
        if not user:
            user = db_sess.query(User).filter(User.nickname == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/home')
        return render_template('login.html', title='Войти | Head-Knight',
                               message='Неверный логин или пароль', auth=True, form=form)
    return render_template('login.html', title='Войти | Head-Knight', auth=True, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/home')


def main():
    db_session.global_init('db/knight_users.sqlite')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
