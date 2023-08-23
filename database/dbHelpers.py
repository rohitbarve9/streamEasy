import pymysql
from flask import flash, render_template

DATABASE_NAME = "stream_easy"


def connectDatabase(hostName, userName, userPassword):
  """
  Create a connection to a MySQL databse with a given host name,
  username and password.
  Parameters:
    hostName (string) : name of the MySQL host
    userName (string) : username for the database
    userPassword (string) : password for the database
  Return: a PyMSQL database connection object
  """
  connection = pymysql.connect(host=hostName,
                               user=userName,
                               password=userPassword,
                               db=DATABASE_NAME,
                               cursorclass=pymysql.cursors.DictCursor)

  return connection

def getConnection(hostName, userName, userPassword):
    """
    Get a database connection object. Throw exceptions to the user
    if a connection cannot be made
    Parameters:
        hostName (string) : name of the MySQL host
        userName (string) : username for the database
        userPassword (string) : password for the database
    Return: a PyMSQL database connection object
    """
    try:
      connection = connectDatabase(hostName,
                                   userName,
                                   userPassword)
    except pymysql.err.OperationalError:
      flash("Database Connection Error. Please Re-Enter Credentials.",
            category="error")
      return render_template("home.html", 
                             session=False, 
                             logged_in=False)
    return connection

      
