from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

from webapp.form import RegistredForm, LoginForm
from webapp.models import User, Comments, Cards
from webapp.models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_db.db'
db.init_app(app)
app.secret_key = "1234"
login = LoginManager()
login.init_app(app)
login.login_view = "login"
migrate = Migrate(app, db, render_as_batch=True)


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
@app.route("/index")
def index():
    list_cards = Cards.query.order_by(Cards.date_add_card.desc()).all()
    return render_template("index.html",   list_cards=list_cards)


@app.route("/personal_acc")
@login_required
def personal_account():
    return render_template('personal_account.html', current_user=current_user)


@app.route('/add_cards')
@login_required
def add_cards():
    return render_template('add_cards.html')


@app.route('/discussion/<int:id>')
def discussion(id):
    card_info = Cards.query.get(id)
    return render_template('discussion.html', card_info=card_info)


@app.route("/all_user")
def user_friend():
    users = User.query.all()
    return render_template('all_user.html', users=users)


@app.route('/user/<id>')
def acc_user(id):
    user = User.query.get(id)
    return render_template('user_acc.html', user=user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Вы вышли')
    return redirect(url_for('index'))


@app.route('/update_card')
def update_card():
    return render_template('update_card.html')



@app.route('/del_comment/<int:id>', methods=["GET", "POST"])
def delete_comment(id):
    comment = Comments.query.get_or_404(id)
    if request.method == "POST":
        try:
            db.session.delete(comment)
            db.session.commit()
            flash("Комментарий успешно удален")
            return redirect(request.referrer)
        except:
            return "ПРи удалении комментария произошла ошибка"

    else:
        return "ERROR 404"


@app.route('/add_comment/<int:id>', methods=['GET','POST'])
@login_required
def add_comment(id):
    if request.method == 'POST':
        author_com = current_user.id
        text = request.form['text']
        comment = Comments(text_comment=text, author_id=author_com, card_id=id)
        try:
            db.session.add(comment)
            db.session.commit()
            flash("Комментарий успешно добавлен")
            return redirect(request.referrer)

        except:
            return "Ошибка при добавлении комментария"
    else:
        flash("Необходимо заполнить все поля ")
        return redirect('/index')

@app.route('/add_card', methods=['POST','GET'])
def add_card():
    if request.method == 'POST':
        poster = current_user.id
        name = request.form['name']
        text = request.form['text']
        card = Cards(name=name, text=text, user_id=poster)
        try:
            db.session.add(card)
            db.session.commit()
            flash("Карточка успешно добавлена")
            return redirect('index')

        except: return "Ошибка при добавлении карточки"
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
            return redirect(request.referrer)
        except: "Не удалось удалить"
    else:
        return "error 404"


@app.route('/update_comment/<int:id>', methods=["POST", "GET"])
def update_comment(id):
    comment = Comments.query.get_or_404(id)
    if request.method == "POST":
        comment.text_comment = request.form["text_comment"]
        try:
            db.session.commit()
            flash("Комментарий успешно изменен")
            return redirect(url_for("discussion", id=comment.card_id))
        except:
            return "При изменении комментария произошла ошибка"
    else:
        return render_template('update_comment.html', comment=comment)


@app.route('/update/<int:id>/post', methods=['POST', 'GET'])
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
        flash("Вы успешно зарегистрировались, можете войти на сайт")
        return redirect(url_for('login'))
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)

