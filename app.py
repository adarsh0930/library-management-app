from flask import Flask
from endpoints import ep
from render import render
import secrets
import os

secret_key = secrets.token_hex(32)

app = Flask(__name__)

abs = os.path.abspath(__file__)
uploadPath = abs[0:-6]+"uploads"
app.config['UPLOAD_FOLDER'] = uploadPath

app.secret_key = secret_key
app.register_blueprint(ep)
app.register_blueprint(render)

if __name__ == '__main__':
    app.run(debug=True)