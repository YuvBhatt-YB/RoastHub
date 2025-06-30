from flask import Flask
from dotenv import load_dotenv

load_dotenv()
def create_app():
    app = Flask(__name__,template_folder="templates")

    from RoastHub.blueprints.HomePage.routes import HomePage
    app.register_blueprint(HomePage,url_prefix="/")

    return app