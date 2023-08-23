from flask import Flask
from flask_session import Session
from .views import views
from .auth import auth


def create_app():
  """
  Create a Flask Application and Initialize a Secret Key.
  Register blueprints (views / auth)
  Return: A Flask Application
  """
  # Create the app and a session
  app = Flask(__name__)
  cookies = Session()

  # Configure the app
  app.config["SECRET_KEY"] = "dsflkjhawl1435kfdgdf234556543gdhfg"
  app.config["SESSION_PERMANENT"] = False
  app.config["SESSION_TYPE"] = "filesystem"
  app.config['SESSION_FILE_THRESHOLD'] = 10

  # Initialize Session
  cookies.init_app(app)
  
  # Register Blueprints
  app.register_blueprint(views, url_prefix="/views")
  app.register_blueprint(auth, url_prefix="/")

  return app