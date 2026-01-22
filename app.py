from flask import Flask, render_template, request, redirect, url_for
from models import db, Transaction
import os
from dotenv import load_dotenv

load_dotenv()  # ładuje zmienne z .env (jeśli istnieje)

app = Flask(__name__)

# Konfiguracja bazy danych z ENV
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
database = os.getenv("MYSQL_DB")
port = os.getenv("MYSQL_PORT", "3306")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Tworzenie tabel przy pierwszym uruchomieniu
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    transactions = Transaction.query.all()
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    balance = total_income - total_expense
    return render_template(
        "index.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
    )

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        t_type = request.form["type"]
        description = request.form["description"]
        amount = float(request.form["amount"])
        new_t = Transaction(type=t_type, description=description, amount=amount)
        db.session.add(new_t)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("add.html")

if __name__ == "__main__":
    app.run(debug=True)