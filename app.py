from flask import Flask
from random import choice
from flask import request

app = Flask(__name__)
app.config['JSON_AS_ASCII']=False

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


about_me = {
   "name": "Константин",
   "surname": "Фурманов",
   "email": "konsfur@gmail.com"
}

@app.route("/")
def hello_world():
   return "Hello, World!"


@app.route("/about")
def about():
   return about_me

@app.route("/quotes")
def get_quotes():
   return quotes

@app.route('/quotes/<int:quote_id>')
def get_quote(quote_id):
    
    quote = next((quote for quote in quotes if quote['id'] == quote_id), None)

    if quote:
        return quote 
    else:
        
      return f"Quote with id={quote_id} not found", 404
    
@app.route('/quotes/count')
def get_quote_count():
    count = len(quotes)
    return{'count': count}

@app.route('/quotes/random')
def get_random_quote():
    random_quote = choice(quotes)
    return (random_quote)

@app.route("/quotes", methods=['POST'])
def create_quote():
   data = request.json
   if 'author' not in data or 'text' not in data:
        return {"error": "Invalid data, 'author' and 'text' are required"}, 400
   new_id = get_new_id()

   new_quote = {
        "id": new_id,
        "author": data['author'],
        "text": data['text']
    }
   quotes.append(new_quote)

   return new_quote, 201

def get_new_id():
    if quotes:
        return max(quote['id'] for quote in quotes) + 1
    else:
        return 1

if __name__ == "__main__":
    app.run(debug=True)