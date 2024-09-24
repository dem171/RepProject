from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError

from webapp.models import User


class RegistredForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Введите login"})
    password = PasswordField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Введите пароль"})
    submit = SubmitField("Регистрация")

    def validate_username(self, username):
        exist_user_username = User.query.filter_by(username=username.data).first    ()
        if exist_user_username:
            raise ValidationError(
                f'имя {username.data} уже занято')

    def validate_pass(self,password, confirm_password):
        if password.data != confirm_password.data:
            raise ValidationError(
                "Пароли должны сопвпадать"
            )


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Введите login"})
    password = PasswordField(validators=[InputRequired(), Length(min=3, max=20)],
                             render_kw={"placeholder": "Введите пароль"})

    remember = BooleanField('Запомнить', default=False)

    submit = SubmitField("Вход")


