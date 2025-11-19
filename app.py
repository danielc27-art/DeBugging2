from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/counter")
def counter():
    return render_template("counter.html")

@app.route("/timer")
def timer():
    return render_template("timer.html")

@app.route("/todo")
def todo():
    return render_template("todo.html")

@app.route("/quotes")
def quotes():
    return render_template("quotes.html")

@app.route("/validator")
def validator():
    return render_template("validator.html")

if __name__ == "__main__":
    app.run(debug=True, port=8001)