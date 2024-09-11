from flask import Flask
from random import choice

app = Flask(__name__)
app.config['JSON_AS_ASCII']=False

quotes = [
    {'id': 1, 'quote' : 'First quote'},
    {'id': 2, 'quote': 'Second quote.'},
    {'id': 3, 'quote': 'Third quote.'},
    {'id': 4, 'quote': 'Fifth quote.'}
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

if __name__ == "__main__":
    app.run(debug=True)