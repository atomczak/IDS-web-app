from flask import Flask
from markupsafe import escape
from flask import render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/<myname>')
def hello_you(myname):
    return f'<h1>Hello {escape(myname)}</h1>'


if __name__ == '__main__':
    app.run()

