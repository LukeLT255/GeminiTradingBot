from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or \
        'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Current value: {self.value} - Current time: {self.time}"

class AccountSchema(ma.Schema):
    class Meta:
        fields = ('id', 'value', 'time')


account_schema = AccountSchema(many=True)


@app.route('/')
def index():
    message = {'msg': 'hello'}
    return jsonify(message)

@app.route('/account', methods=['GET'])
def get_all_values():
    values = Account.query.all()
    result = account_schema.dump(values)
    return jsonify(result)


