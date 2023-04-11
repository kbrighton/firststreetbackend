from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
import os


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

Base = automap_base()
Base.prepare(db.engine, reflect=True)




@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
