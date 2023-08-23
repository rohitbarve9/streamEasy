from website import create_app
from flask_session import Session

app = create_app()  # Create the Flask Application


if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0')

