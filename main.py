from flask import Flask, render_template, redirect, request
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user
from data.users import User
from forms.user import RegisterForm
from forms.login import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wtf-msi'
login_manager = LoginManager()
login_manager.init_app(app)


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
    list_of_nicknames = [x[0] for x in db_sess.query(User.nickname)]
    return render_template('friends.html', title='Friends', user=user,
                           spisok_nicknames=list_of_nicknames)


@app.route('/home')
def home():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    return render_template('home.html', title='Главная | Head-Knight',
                           user=user, auth=False, home=True)


@app.route('/icon_changing', methods=["GET", "POST"])
def image_of_profile():
    if request.method == 'GET':
        db_sess = db_session.create_session()
        user = db_sess.query(User)
        return render_template('changing_image.html', title='Меняем картинку',
                               user=user)
    elif request.method == 'POST':
        encoded_string = request.files['file'].read()
        print(encoded_string)
        with open("static/images/avatar.jpg", "wb") as img:
            img.write(encoded_string)
    return redirect('/home')


@app.route('/community')
def community():
    return redirect('/home')


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
        user = User()
        user.email = form.email.data
        user.nickname = form.nickname.data

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
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
            return redirect('/')
        return render_template('login.html', title='Войти | Head-Knight',
                               message='Неверный логин или пароль', auth=True, form=form)
    return render_template('login.html', title='Войти | Head-Knight', auth=True, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


def main():
    db_session.global_init('db/knight_users.sqlite')
    app.run()


if __name__ == '__main__':
    main()
