from typing import Any
from flask import Flask, jsonify, request
from random import choice
from http import HTTPStatus
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, func
from sqlalchemy.exc import InvalidRequestError
from flask_migrate import Migrate
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    pass



BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate= Migrate(app, db)

class AuthorModel(db.Model):
    __tablename__ = 'authors'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(String(32), index= True, unique=True)
    quotes: Mapped[list['QuoteModel']] = relationship(back_populates='author', lazy='dynamic')

    def __init__(self, name):
       self.name = name

    def to_dict(self):
        return {'name': self.name}


class QuoteModel(db.Model):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey('authors.id'))
    author: Mapped['AuthorModel'] = relationship(back_populates='quotes')
    text: Mapped[str] = mapped_column(String(255))

    def __init__(self, author, text):
        self.author = author
        self.text  = text



with app.app_context():
    db.create_all()
quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так."
   },

]
@app.route('/')
def home():
    return "Hello Python"


@app.route('/quotes')
def get_quotes():
    quotes = QuoteModel.query.all()
    quotes_list = [{"id": q.id, "author": q.author, "text": q.text} for q in quotes]
    return jsonify(quotes_list), 200

@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id: int) -> dict:
   """ Функция возвращает цитату по значению ключа id=quote_id."""
   for quote in quotes:
      if quote["id"] == quote_id:
         return jsonify(quote), 200 
   return {"error": f"Quote with id={quote_id} not found"}, 404               


@app.get("/quotes/count")
def quotes_count():
   """Function for task3 of Practice part1."""
   return jsonify(count=len(quotes))


def create_quote():
    new_quote_data = request.json
    author = new_quote_data.get("author")
    text = new_quote_data.get("text")
    rating = new_quote_data.get("rating", 1)
    if not author or not text:
        return jsonify({"error": "Author and text are required"}), 400
    if rating not in range(1, 6):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    new_quote = QuoteModel(author=author, text=text, rating=rating)
    with app.app_context():
        db.session.add(new_quote)
        db.session.commit()
    return jsonify({
        "id": new_quote.id,
        "author": new_quote.author,
        "text": new_quote.text,
        "rating": new_quote.rating
    }), 201


@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    new_data = request.json
    if not set(new_data.keys()) <= set(('author', 'rating', 'text')):
        return {"error": "Send bad data to update"}, HTTPStatus.BAD_REQUEST
    
  
    with app.app_context():
        quote = db.session.get(QuoteModel, quote_id)
        if quote is None:
            return {"error": f"Quote with id={quote_id} not found."}, 404
        
   
        if "rating" in new_data and (new_data["rating"] not in range(1, 6)):
            new_data.pop("rating")  
       
        for key, value in new_data.items():
            setattr(quote, key, value)
        db.session.commit()

    return jsonify({
        "id": quote.id,
        "author": quote.author,
        "text": quote.text,
        "rating": quote.rating
    }), HTTPStatus.OK

@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id: int):
    with app.app_context():
        quote = db.session.get(QuoteModel, quote_id)
        if quote is None:
            return {"error": f"Quote with id={quote_id} not found."}, 404
        
        db.session.delete(quote)
        db.session.commit()

    return jsonify({"message": f"Quote with id={quote_id} has been deleted."}), 20


@app.route("/quotes/filter")
def filter_quotes():
   filtered_quotes = quotes.copy()
   for key, value in request.args.items():
      if key not in ("author", "rating"):
         return f"Invalid key {key}", HTTPStatus.BAD_REQUEST
      if key == "rating":
         value = int(value)
      filtered_quotes = [quote for quote in filtered_quotes if quote.get(key) == value]
   return filtered_quotes

from flask import g

DATABASE = '/path/to/database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
   app.run(debug=True)