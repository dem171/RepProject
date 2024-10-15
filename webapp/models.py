from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData




convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True, index=True)
    password = db.Column(db.String)
    rol = db.Column(db.String(15), index=True)
    date_registration = db.Column(db.DateTime, default=datetime.utcnow)
    user_cards = db.relationship("Cards", backref="user", cascade='all, delete')
    user_comment = db.relationship("Comments", backref="user_com", cascade='all, delete')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def chek_password(self, password):
        return check_password_hash(self.password, password)


    def post_count(self):
        return Cards.query.filter(Cards.user_id == self.id).count()

    def __repr__(self):
        return f'User {self.username}'


class Cards(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    text = db.Column(db.Text)
    date_add_card = db.Column(db.DateTime, default=datetime.utcnow)
    comment_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_comment = db.relationship("Comments", backref="card_com", cascade='all, delete')

    def comments_count(self):
        return Comments.query.filter(Comments.card_id == self.id).count()

    def __repr__(self):
        return f'Card {self.name}'


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_comment = db.Column(db.String, nullable=False)
    date_comment = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer,  db.ForeignKey("user.id"))
    card_id = db.Column(db.Integer,  db.ForeignKey("cards.id"))

    def __repr__(self):
        return f'Comment {self.text_comment} ,{self.id}, {self.date_comment}'