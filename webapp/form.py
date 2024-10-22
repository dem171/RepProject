from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError, EqualTo
from flask_ckeditor import CKEditorField

from models import User


class RegistredForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Введите login"})
    password = PasswordField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Введите пароль"})
    password2 = PasswordField( validators=[DataRequired(), EqualTo('password')],  render_kw={"placeholder":"Повторите пароль"})
    submit = SubmitField("Регистрация")

    def validate_username(self, username):
        exist_user_username = User.query.filter_by(username=username.data).first()
        if exist_user_username:
            raise ValidationError(
                f'Login {username.data} уже занят')





class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Введите login"})
    password = PasswordField(validators=[InputRequired(), Length(min=3, max=20)],
                             render_kw={"placeholder": "Введите пароль"})

    remember = BooleanField('Запомнить', default=False)

    submit = SubmitField("Вход")


class CommentForm(FlaskForm):
    text_comment = CKEditorField(validators=[InputRequired(), Length(min=5,max=100)],
                               render_kw={"placeholder": "Введите комментарий"})
    submit = SubmitField("Отправить")


class PostForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=5,max=100)],
                            render_kw={"placeholder": "Введите название поста"})
    text = CKEditorField(validators=[InputRequired()], render_kw={'placeholder': "Введите текс"})
    submit = SubmitField('Добавить')