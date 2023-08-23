from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from database.dbHelpers import connectDatabase, getConnection
import pymysql

#=====================================#
#==== SQL QUERY - HELPER FUNCTIONS ===#
#=====================================#
def checkUserExists(cursor, username):
  """
  Check that a user exists in the database
  Parameters:
    cursor: An active connection/cursor for a MySQL database
    username: The username to match against the database
  Return: True or False
  """
  query = "SELECT check_user_exists(%s)"
  cursor.execute(query, (username))
  result = cursor.fetchall()
  return bool(list(result[0].values())[0])


def validateUserCredentials(cursor, username, password):
  """
  Check that the username and password are valid for a given user
  Parameters:
    cursor: An active connection/cursor for a MySQL database
    username: The username of the given user
    password: The password of the given user
  Return: True or False
  """
  query = "SELECT check_user_credentials(%s, %s)"
  cursor.execute(query, (username, password))
  result = cursor.fetchall()

  return bool(list(result[0].values())[0])

def createNewUser(cursor, username, password, email, firstName, lastName):
  """
  Create a new user in the database
  Precondition: Username has been validated as unique and non-conflicting
  Parameters:
    cursor: An active connection/cursor for the MySQL Database
    username: The username of the user to be added
    password: The password of the user to be added
    email: The email address of the user to be added
    firstName: The first name of the user to be added
    lastName: The last name of the user to be added
  Return: True or False - indicating if the INSERT was a success
  """
  query = "CALL create_new_user(%s, %s, %s, %s, %s)"
  cursor.execute(query, (username, password, email, firstName, lastName))

  # Return a boolean indicating if successfully added
  return checkUserExists(cursor, username)

  
def get_user_account_info(cursor, username):
  """
  Get a user's account info from the database
  Parameters:
    cursor: An active connection/cursor for the MySQL Database
    username: The username of the user to be added
  Return: a dictionary containing the user account info
  """
  query = "CALL get_account_info(%s)"
  cursor.execute(query, (username))
  result = cursor.fetchall()
  
  return result[0]


#=================================#
#=== Back End Route Management ===#
#=================================#
auth = Blueprint("auth", __name__)


#===========================#
#=== Database Connection ===#
#===========================#
@auth.route("/", methods=["GET", "POST"])
def home():
  """
  Create a route for the home page.
  Return: The home page (rendered from template)
  """
  if request.method == "POST":
    session["hostName"] = request.form.get("db_host")
    session["userName"] = request.form.get("db_username")
    session["userPassword"] = request.form.get("db_password")
    session["db_connected"] = False
    """
    Attampt to connect to the database
    - If unsuccessful, throw an error and try again
    - If successful, proceed to login
    """
    try:
      connection = connectDatabase(session.get("hostName"),
                                   session.get("userName"),
                                   session.get("userPassword"))

      # Successful connection -- Close Cursor and Redirect to Login
      flash("Database connection was successful!", category="sucess")
      session["db_connected"] = True
      connection.close()
      return redirect(url_for("auth.login"))  # Route to login

    except pymysql.err.OperationalError:
      # Unsuccessful Connection
      flash(
        "Error Encountered When Connecting to Database.\
         Please Ensure Correct Credentials are Provided.",
        category="error")
      return render_template("home.html",
                             session=False,
                             logged_in=False,
                             host=session.get("hostName"),
                             user=session.get("userName"))

  # Initially Rendered with no information in the forms
  else:
    return render_template("home.html",
                           session=False,
                           logged_in=False,
                           host=None,
                           user=None)


#=============#
#=== LOGIN ===#
#=============#
@auth.route("/login", methods=["GET", "POST"])
def login():
  """
  Create a route for login page.
  Return: The login page (rendered from template)
  """
  # If Database not Connected - Route Home
  if not session.get("db_connected"):
    return redirect(url_for("auth.home"))

  # Extract Data From the Form
  if request.method == "POST":
    session["user_id"] = request.form.get("username_login")
    session["user_pw"] = request.form.get("password_login")
    session["logged_in"] = False
    
    """
    Create a new connection using current session information
    -- If connection cannot be made - user routed to DB Connection Page
    """
    connection = getConnection(session.get("hostName"),
                               session.get("userName"),
                               session.get("userPassword"))
    with connection.cursor() as cursor:
      # Check if the username exists
      if not checkUserExists(cursor, session.get("user_id")):
        flash("Username not recognized. Please Re-enter Username or Sign-up.",
              category="error")
        return render_template("login.html",
                               session=True,
                               logged_in=False,
                               user_id=None)

      # Check if the User and Password is Correct
      if not validateUserCredentials(cursor, 
                                     session.get("user_id"), 
                                     session.get("user_pw")):
        flash("Incorrect Password. Please Try Again.", category="error")
        return render_template("login.html",
                               session=True,
                               logged_in=False,
                               user_id=session.get("user_id"))

      # Successful login
      session["logged_in"] = True
      userAcctInfo = get_user_account_info(cursor, session.get("user_id"))
      session["user_acct_info"] = userAcctInfo
      connection.commit()
      connection.close()
      return redirect(url_for("views.subscriptions"))
  
  else:
    return render_template("login.html",
                           session=True,
                           logged_in=False,
                           user_id=None)
  

#===============#
#=== SIGN UP ===#
#===============#
@auth.route("/sign-up", methods=["GET", "POST"])
def signUp():
  """
  Create the route for the Sign Up page.
  Return: The sign up page (rendered from template)
  """
  # If Database not Connected - Route Home
  if not session.get("db_connected"):
    return redirect(url_for("home"))

  # Extract Data From the Form
  if request.method == "POST":
    firstName = request.form.get("first_name")
    lastName = request.form.get("last_name")
    email = request.form.get("email")
    username = request.form.get("username_signup")
    password1 = request.form.get("password_signup_1")
    password2 = request.form.get("password_signup_2")

    """
    Create a new connection using current session information
    -- If connection cannot be made - user routed to DB Connection Page
    """
    connection = getConnection(session.get("hostName"),
                               session.get("userName"),
                               session.get("userPassword"))
    with connection.cursor() as cursor:
      # Check if the username exists
      if checkUserExists(cursor, username):
        flash("The Requested Username Already Exists. Please Choose Another.",
              category="error")
        return render_template("signUp.html",
                               session=True,
                               logged_in=False,
                               first_name = firstName,
                               last_name = lastName,
                               email_address = email,
                               user_name = username)
      
      # Check if the passwords match
      if password1 == password2:
        password = request.form.get("password_signup_2")
      else:
        flash("The passwords provided do not match. Please re-enter password",
              category="error")
        return render_template("signUp.html",
                       session=True,
                       logged_in=False,
                       first_name = firstName,
                       last_name = lastName,
                       email_address = email,
                       user_name = username)

      # Add the new user to the database
      if not createNewUser(cursor, 
                           username, 
                           password, 
                           email, 
                           firstName, 
                           lastName):
        flash("User Was Unable To Be Added. Please Try Again.",
              category="error")
        return render_template("signUp.html",
                               session=True,
                               logged_in=False,
                               first_name = firstName,
                               last_name = lastName,
                               email_address = email,
                               user_name = username)

      # Successful Creation
      flash("Successful Account Creation.", category="sucess")
      connection.commit()
      connection.close() # Close the connection
      return redirect(url_for("auth.login"))

  else:
    return render_template("signUp.html",
                            session=True,
                            logged_in=False,
                            first_name = None,
                            last_name = None,
                            email_address = None,
                            user_name = None)

  
#==============#
#=== LOGOUT ===#
#==============#
@auth.route("/logout")
def logout():
  """
  Create a route for logout page.
  Return: The logout page (rendered from template)
  """
  STATIC = ['hostName', 'userName', 'userPassword', 'db_connected']
  for key in list(session.keys()):
    if key not in STATIC:
      session[key] = None      
    
  return redirect(url_for("auth.login"))
