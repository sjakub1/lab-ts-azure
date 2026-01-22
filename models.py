from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))  # 'income' lub 'expense'
    description = db.Column(db.String(100))
    amount = db.Column(db.Float)

    def __repr__(self):
        return f"<Transaction {self.description} {self.amount}>"