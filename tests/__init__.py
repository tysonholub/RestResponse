from flask import Flask
from flask_sqlalchemy import SQLAlchemy

test_app = Flask(__name__)
test_app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite+pysqlite:////tmp/rest-response.db")
test_db = SQLAlchemy(test_app)
