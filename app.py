from typing import Any
from flask import Flask, jsonify, request
from random import choice
from http import HTTPStatus
from pathlib import Path
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String




BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)

class QuoteModel(Base):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(32), nullable=False)
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    rating: Mapped[int] = mapped_column(default=1, nullable=False) 

    def __init__(self, author, text):
        self.author = author
        self.text  = text

# Создание таблицы (если она не существует)
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


@app.route("/quotes", methods=['POST'])
def create_quote():
   """ Функция создает новую цитату в списке."""
   new_quote = request.json  # json -> dict
   last_quote = quotes[-1] # Последняя цитата в списке
   new_id = last_quote["id"] + 1
   new_quote["id"] = new_id
   # Мы проверяем наличие ключа rating и его валидность(от 1 до 5)
   rating = new_quote.get("rating")
   if rating is None or rating not in range(1, 6):
      new_quote["rating"] = 1
   quotes.append(new_quote)
   return jsonify(new_quote), 201


@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
   new_data = request.json
   if not set(new_data.keys()) - set(('author', 'rating', 'text')):
      for quote in quotes:
         if quote["id"] == quote_id:
            if "rating" in new_data and new_data["rating"] not in range(1, 6):
               # Валидируем новое значени рейтинга и случае успеха обновляем данные
               new_data.pop("rating")
            quote.update(new_data)
            return jsonify(quote), HTTPStatus.OK
   else:
      return {"error": "Send bad data to update"}, HTTPStatus.BAD_REQUEST 
   return {"error": f"Quote with id={quote_id} not found."}, 404


@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id: int):
   for quote in quotes:
      if quote["id"] == quote_id:
         quotes.remove(quote)
         return jsonify({"message": f"Quote with id={quote_id} has deleted."}), 200 
   return {"error": f"Quote with id={quote_id} not found."}, 404  


@app.route("/quotes/filter")
def filter_quotes():
   filtered_quotes = quotes.copy()
   # request.args хранит данные, полученные из query parameters
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