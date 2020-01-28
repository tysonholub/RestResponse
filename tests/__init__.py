from flask import Flask
from flask_sqlalchemy import SQLAlchemy

test_app = Flask(__name__)
test_db = SQLAlchemy(test_app)
