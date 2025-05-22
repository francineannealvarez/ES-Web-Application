from flask import Flask
from routes import app_routes  

app = Flask(__name__)
app.secret_key = 'ecotrack'
app.register_blueprint(app_routes)

if __name__ == '__main__':
    app.run(debug=True)
