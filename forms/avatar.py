from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, FileField
from wtforms.validators import DataRequired


class AvatarForm(FlaskForm):
    avatar = FileField('Изображение профиля', validators=[DataRequired()])
    submit = SubmitField('Загрузить изображение')
