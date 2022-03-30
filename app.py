from datetime import datetime
from flask import Flask
app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currentValue = db.Column(db.Float, nullable=False)
    currentTime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Current value: {self.currentValue} - Current time: {self.currentTime}"


@app.route('/')
def index():
    return "hullooooo"

@app.route('/account')
def get_all_values():
    values = Account.query.all()

    output = []
    for value in values:
        value_data = {'value': value.currentValue, 'time': value.currentTime}

        output.append(value_data)

    return {"values": output}
