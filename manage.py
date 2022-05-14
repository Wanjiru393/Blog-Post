from flask import Flask, render_template


app = Flask(__name__)





@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/blog")
def blog():
    return "<p>Hey You!</p>"


if __name__ == "__main__":
    app.run(debug=True)