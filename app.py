from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required , current_user
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import MetaData


convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_db.db'
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
app.secret_key = "1234"
login = LoginManager()
login.init_app(app)
login.login_view = "login"
migrate = Migrate(app, db, render_as_batch=True)




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True, index=True)
    password = db.Column(db.String)
    rol = db.Column(db.String(15), index=True)
    date_registration = db.Column(db.DateTime, default=datetime.utcnow)


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def chek_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Cards(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    text = db.Column(db.Text)
    date_add_card = db.Column(db.DateTime,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Card {self.name}'





@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)



@app.route("/")
@app.route("/index")
def index():
    list_cards = Cards.query.all()
    return render_template("index.html", list_cards=list_cards)


@app.route("/personal_account/", methods=['GET', 'POST'])
@login_required
def personal_account():
    return render_template('personal_account.html', current_user=current_user)


@app.route('/add_cards')
@login_required
def add_cards():
    return render_template('add_cards.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Вы вышли')
    return redirect(url_for('index'))


@app.route('/update_card')
def update_card():
    return render_template('update_card.html')



@app.route('/add_card', methods=['GET','POST'])
def add_card():
    if request.method == 'POST':
        name = request.form['name']
        text = request.form['text']
        card = Cards(name=name, text=text)
        try:
            db.session.add(card)
            db.session.commit()
            flash("Карточка успешно добавлена")
            return redirect('index')

        except:"Ошибка при добавлении карточки"
    else:
        flash("Необходимо заполнить все поля ")
        return redirect('/index')


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def del_card(id):
    card = Cards.query.get_or_404(id)
    if request.method == 'POST':


        try:
            db.session.delete(card)
            db.session.commit()
            flash("Карточка успешно удалена")
            return redirect('/index')
        except: "Не удалось удалить"
    else:
        return "error 404"


@app.route('/update/<int:id>/post', methods=['POST' ,'GET'])
def upd_card(id):
    card = Cards.query.get_or_404(id)
    if request.method == 'POST':
        card.name = request.form["name"]
        card.text = request.form["text"]

        try:
            db.session.commit()
            flash("Карточка успешно изменена")
            return redirect(url_for('index'))
        except:
            return "ПРоизошла ошибка редактирования"

    else:
        return render_template('update_card.html', card=card)




@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistredForm()
    if form.validate_on_submit():
        hash_pass = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hash_pass)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Вы успешно вошли на сайт')
                return redirect(url_for('index'))
        flash('не правильно введен логин или пароль')
        return redirect(url_for('login',form=form))
    return render_template('login.html', form=form)




class RegistredForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Введите login"})
    password = PasswordField(validators=[DataRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Введите пароль"})
    submit = SubmitField("Регистрация")

    def validate_username(self, username):
        exist_user_username = User.query.filter_by(username=username.data).first()
        if exist_user_username:
            raise ValidationError(
                f'имя {username.data} уже занято')



class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={"placeholder": "Введите login"})
    password = PasswordField(validators=[InputRequired(), Length(min=3, max=20)],
                             render_kw={"placeholder": "Введите пароль"})

    remember = BooleanField('Запомнить', default=False)

    submit = SubmitField("Вход")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)