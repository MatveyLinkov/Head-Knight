from flask import Flask, render_template, redirect


app = Flask(__name__)
app.config['SECRET_KEY'] = 'wtf-msi'


@app.route('/')
def index():
    return redirect('/home')


@app.route('/home')
def home():
    return render_template('base.html', title='Главная | Head-Knight')


def main():
    app.run()


if __name__ == '__main__':
    main()
