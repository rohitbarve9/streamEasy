from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from database.dbHelpers import getConnection
import pymysql
from datetime import datetime
import calendar
import time

FILTER_TYPES = ["a-z", "z-a", "price-high", "price-low", "popularity-high", "popularity-low"]

#=====================================#
#==== SQL QUERY - HELPER FUNCTIONS ===#
#=====================================#
def getAllServices(cursor, sort_type):
  """
  Get a result set of all the services offered and popularity metrics
    in a given sorted order:
      a-z
      z-a
      price-high
      price-low
      popularity-high
      popularity-low
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    sort_type: A sort type from the list of valid options above
  Return: A dictionary/result set of all offered services
  """
  query = "CALL get_subscription_metrics(%s)"
  cursor.execute(query, (sort_type))
  result = cursor.fetchall()

  return result


def getAllUserServices(cursor, username):
  """
  Get a result set of all services a given user subscribes to
  Precondition: Username has already been validated
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: A given user in the database
  Return: A dictionary/result set of all services a user subscribes to
  """
  query = "CALL get_user_services(%s)"
  cursor.execute(query, (username))
  result = cursor.fetchall()

  return result


def checkUserServiceExists(cursor, username, serviceName):
  """
  Check whether or not a given user is subscribed to a given service
  Precondition: username and service name are valid
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: A given user in the database
    serviceName: A given service offered / in the database
  Returns: True if the given user is subscribed to the given service,
    otherwise False
  """
  query = "SELECT check_subscription_status(%s, %s)"
  cursor.execute(query, (username, serviceName))
  result = cursor.fetchall()

  return bool(list(result[0].values())[0])


def checkUserFavoriteExists(cursor, username, contentId):
  """
  Check whether or not a given user has favorited a movie or show
  Precondition: username and content id are valid
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: A given user in the database
    contentId: A given id for a piece of content in the database
  Returns: True if the given user has favorited the given content,
    otherwise False
  """
  query = "SELECT check_favorite_status(%s, %s)"
  cursor.execute(query, (username, contentId))
  result = cursor.fetchall()

  return bool(list(result[0].values())[0])


def addNewService(cursor, username, serviceName):
  """
  Add a subscription / service for a given user
  Precondition: user is not already subscribed to the given service
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: A given user in the database
    serviceName: A given service offered / in the database
      which the user is not already subscribed to
  Return: True if the operation was a success, False otherwise
  """
  query = "CALL add_new_service(%s, %s)"
  cursor.execute(query, (username, serviceName))
  
  return checkUserServiceExists(cursor, username, serviceName)


def addNewFavorite(cursor, username, contentId):
  """
  Add a favorited content for a given user
  Precondition: user has not already favorited a given piece of content
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: A given user in the database
    contentId: A given id for a piece of content in the database  
  Return: True if the operation was a success, False otherwise
  """
  query = "CALL add_new_user_favorite(%s, %s)"
  cursor.execute(query, (username, contentId))
  
  return checkUserFavoriteExists(cursor, username, contentId)


def removeFavorite(cursor, username, contentId):
  """
  Remove a favorited content for a given user
  Precondition: user has already favorited a given piece of content
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: A given user in the database
    contentId: A given id for a piece of content in the database  
  Return: True if the operation was a success, False otherwise
  """
  query = "CALL remove_user_favorite(%s, %s)"
  cursor.execute(query, (username, contentId))
  
  return not checkUserFavoriteExists(cursor, username, contentId)


def removeService(cursor, username, serviceName):
  """
  Remove/End a subscription / service for a given user
  Precondition: user is subscribed to the given service
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: A given user in the database
    serviceName: A given service offered / in the database
      which the user is subscribed to
  Return: True if the operation was a success, False otherwise
  """
  query = "CALL remove_service(%s, %s)"
  cursor.execute(query, (username, serviceName))

  return not checkUserServiceExists(cursor, username, serviceName)


def getAllMovies(cursor, sort_type):
  """
  Get a result set of all the movies offered and popularity metrics
  in a given sorted order:
    a-z
    z-a
    popularity-high
    popularity-low
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    sort_type: A sort type from the list of valid options above
  Return: A dictionary/result set of all offered movies
  """
  query = "CALL get_all_movies(%s)"
  cursor.execute(query, (sort_type))
  result = cursor.fetchall()

  return result


def getAllTvShows(cursor, sort_type):
  """
  Get a result set of all the tv shows offered and popularity metrics
  in a given sorted order:
    a-z
    z-a
    popularity-high
    popularity-low
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    sort_type: A sort type from the list of valid options above
  Return: A dictionary/result set of all offered tv shows
  """
  query = "CALL get_all_tv_shows(%s)"
  cursor.execute(query, (sort_type))
  result = cursor.fetchall()

  return result


def getUserFavorites(cursor, username, sort_type):
  """
  Get a result set of all user favorites and popularity metrics
  in a given sorted order:
    a-z
    z-a
    popularity-high
    popularity-low
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: A given user in the database
    sort_type: A sort type from the list of valid options above
  Return: A dictionary/result set of all user favorites
  """
  query = "CALL get_user_favorites(%s, %s)"
  cursor.execute(query, (username, sort_type))
  result = cursor.fetchall()

  return result


def checkPasswordValidity(cursor, username, current_password, new_password):
  """
  Check current password entered matches the value in the database and the new passwords entered match.
  Parameter:
    cursor: An active connection / cursor to a MySQL Database
    username: A given user in the database
    current_password: The current password for the user in the database
    new_password: The new password to be stored in the database
  Return: Boolean value on whether the new passoword is valid
  """
  query = "SELECT password from user where username = %s"
  cursor.execute(query, (username,))
  result = cursor.fetchone()

  if result['password'] != current_password:
    print(result['password'], current_password)
    return False
  else:
    query = "UPDATE user SET password = %s WHERE username = %s"
    cursor.execute(query, (new_password, username))
    return True


def getPaymentOptions(cursor, username):
  """
  Get payment options for a user.
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: The username in the database for the given user
  Return: Payment options with the information about card number, type, expiry date
  """
  query = "CALL getPaymentOptions(%s)"
  cursor.execute(query, (username,))
  result = cursor.fetchall()

  return result


def deleteCard(cursor, card_number):
  """
  Delete card and it's associated details from the database table.
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    card_number: The card number to be deleted
  Return: None
  """
  query = "CALL deleteCard(%s)"
  cursor.execute(query, (card_number))


def addNewCard(cursor, card_number, card_type, security_code, month, year):
  """
  Adds a new card in the payment method table.
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    card_number: The number of the new card
    card_type: Type associated with the card (Visa, Mastercard etc.) 
    security_code: CVV code associated with the new card
    month: expiration month of the card
    year: expiration year of the card
  Return: None
  """
  query = "CALL addNewCard(%s, %s, %s, %s)"
  date = f"{year}-{month}-01"
  cursor.execute(query, (card_number, card_type, security_code, date))


def connectCardUser(cursor, username, card_number):
  """
  Adds a new connection between the user and the card.
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: The username in the database for the given user
    card_number: The number of the new card
  Return: None
  """
  query = "CALL connectUserCard(%s, %s)"
  cursor.execute(query, (username, card_number))


def addBillingAddress(cursor, card_number, street_name, city, state, zip_code):
  """
  Adds billing address to card.
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    card_number: The number of the new card
  Return: None
  """
  query = "CALL addBillingAddress(%s, %s, %s, %s, %s)"
  cursor.execute(query, (card_number, street_name, city, state, zip_code))


def getTotalCost(cursor, username):
  """
  Get the total cost incurred by a user from the subscribed services.
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: The username in the database for the given user
  Return: Total monthly cost of all the subscriptions
  """
  query = "SELECT getTotalCost(%s) as total_monthly_cost"
  cursor.execute(query, (username,))
  result = cursor.fetchone()['total_monthly_cost']

  return result


def get_user_recommendations(cursor, username):
  """
  Get user recommendations based on subscribed services.
  The user will receive top 2 movies and top 2 tv shows from
  each service which they are subscribed to and for content
  which they have not favorited.
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    username: The username in the database for the given user
  Return: a set of user recommendation (content)
  """
  # get the user's services
  query = "CALL get_user_service_ids(%s)"
  cursor.execute(query, (username))
  user_services = cursor.fetchall()
  result = []

  # get a list of ids
  ids = []
  for dic in user_services:
    ids.append(int(dic['service_id']))
  
  for id in ids:
    query = "CALL get_top_recs(%s, %s)"
    cursor.execute(query, (username, id))
    recs = cursor.fetchall()
    for dic in recs:
      result.append(dic)

  return result


def get_movie_search(cursor, keyword):
  """
  Get a result set of movies from a given search term.
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    keyword: A search term (title) 
  Return: A result set of movies that are similar to the keyword
  """
  query = "CALL search_movies(%s)"
  cursor.execute(query, (keyword))
  result = cursor.fetchall()

  return result


def get_tv_search(cursor, keyword):
  """
  Get a result set of tv shows from a given search term.
  Parameters:
    cursor: An active connection / cursor to a MySQL Database
    keyword: A search term (title) 
  Return: A result set of tv shows that are similar to the keyword
  """
  query = "CALL search_tv_shows(%s)"
  cursor.execute(query, (keyword))
  result = cursor.fetchall()

  return result


def getBill(cursor, month, year, username):
  query = "CALL generateBill(%s, %s, %s)"
  cursor.execute(query, (month, year, username))
  result = cursor.fetchall()

  return result


def getTotal(cursor, month, year, username):
  query = "CALL generateTotal(%s, %s, %s)"
  cursor.execute(query, (month, year, username))
  result = cursor.fetchone()

  return result


def getMostViewed(cursor, month, year, username):
  query = "CALL getMostViewed(%s, %s, %s)"
  cursor.execute(query, (month, year, username))
  result = cursor.fetchone()

  return result


def getMostBilled(cursor, month, year, username):
  query = "CALL getMostBilled(%s, %s, %s)"
  cursor.execute(query, (month, year, username))
  result = cursor.fetchone()

  return result

#=================================#
#=== Back End Route Management ===#
#=================================#
views = Blueprint("views", __name__)

#=====================#
#=== Subscriptions ===#
#=====================#
@views.route("/subscriptions", methods=["GET", "POST"])
def subscriptions():

  # If Database not Connected - Route Home
  if not session.get("db_connected"):
    return redirect(url_for('auth.home'))

  # If Not Logged In - Route to Login
  if not session.get("logged_in"):
    return redirect(url_for("auth.login"))

  if request.method == "GET":
    # Open a Connection To Get all Subscription Data 
    connection = getConnection(session.get("hostName"),
                               session.get("userName"),
                               session.get("userPassword"))
    with connection.cursor() as cursor:
      if not session.get("current_sub_filter"):
        session["current_sub_filter"] = FILTER_TYPES[0]

      allServiceData = getAllServices(cursor, session.get("current_sub_filter"))
      session["all_services"] = allServiceData
      # Extract all names into session variable
      session["all_service_names"] = []
      for row in session['all_services']:
        session["all_service_names"].append(row['service_name'])
      connection.commit()

      userServices = getAllUserServices(cursor, session.get("user_id"))
      session["user_services"] = userServices
      session["user_recs"] = get_user_recommendations(cursor, session.get("user_id"))
      session["total_monthly_cost"] = getTotalCost(cursor, session.get("user_id"))

    connection.commit()
    connection.close()
      
    return render_template("subscriptions.html", 
                           session=True, 
                           logged_in=True, 
                           option="my_sub", 
                           data=session.get("user_services"),
                           recommended=session.get("user_recs"),
                           total_cost=session["total_monthly_cost"])

  """
  User Interaction with toggle tabs
  """
  if request.method == "POST":
    ###########################################
    ### USER SELECTED ALL SUBSCRIPTIONS TAB ###
    ###########################################
    if "all_sub" in request.form:
      return render_template("subscriptions.html", 
                             session=True, 
                             logged_in=True, 
                             option="all_sub", 
                             data=session.get("all_services"))
    
    ##########################################
    ### USER SELECTED MY SUBSCRIPTIONS TAB ###
    ##########################################
    elif "my_sub" in request.form:
      # Get the most current information from the databse
      connection = getConnection(session.get("hostName"),
                                 session.get("userName"),
                                 session.get("userPassword"))
      with connection.cursor() as cursor:
        userServices = getAllUserServices(cursor, session.get("user_id"))
        userRecs = get_user_recommendations(cursor, session.get("user_id"))
        session["user_services"] = userServices
        session["user_recs"] = userRecs
        session["total_monthly_cost"] = getTotalCost(cursor, session.get("user_id"))
      
      connection.commit()
      connection.close()
      return render_template("subscriptions.html", 
                             session=True, 
                             logged_in=True, 
                             option="my_sub", 
                             data=session.get("user_services"),
                             recommended=session.get("user_recs"),
                             total_cost=session["total_monthly_cost"])
    

    ###################################################
    ### USER SELECTED A FILTER ON ALL SUBSCRIPTIONS ###
    ###################################################
    elif list(request.form.keys())[0] in FILTER_TYPES:
      filter_selection = list(request.form.keys())[0]
      connection = getConnection(session.get("hostName"),
                                session.get("userName"),
                                session.get("userPassword"))    
      with connection.cursor() as cursor:
        session["current_sub_filter"] = filter_selection
        allServiceData = getAllServices(cursor, filter_selection)
        session["all_services"] = allServiceData
        connection.commit()
        connection.close()
        
      return render_template("subscriptions.html", 
                              session=True, 
                              logged_in=True, 
                              option="all_sub", 
                              data=session.get("all_services"))

    ###################################################
    ### USER SELECTED TO MODIFY THEIR SUBSCRIPTIONS ###
    ###################################################
    else:
      buttonInfo = list(request.form.values())[0].split(":")
      action = buttonInfo[0].strip()
      service = buttonInfo[1].strip()

      # Create a connection for Update / Delete
      connection = getConnection(session.get("hostName"),
                                session.get("userName"),
                                session.get("userPassword"))
      
      ##########################
      ### ADD A SUBSCRIPTION ###
      ##########################
      if action == "Add":
        with connection.cursor() as cursor:
          if checkUserServiceExists(cursor,
                                    session.get("user_id"),
                                    service):
                      
            connection.close()
            flash("You Are Already Subscribed!!",
                  category="success")
          else:
            if addNewService(cursor,
                             session.get("user_id"),
                             service):
              flash("You are now subscibed to " + service + "!!",
                  category="success")
              session["all_services"] = getAllServices(cursor, session.get("current_sub_filter"))
              session["user_recs"] = get_user_recommendations(cursor, session.get("user_id"))
            else:
              flash("Error encountered when adding service. Please try again.",
                  category="error")
              
            connection.commit()
            connection.close()
        
        return render_template("subscriptions.html", 
                                session=True, 
                                logged_in=True, 
                                option="all_sub", 
                                data=session.get("all_services"))
                                
      ############################
      ### REMOVE A SUBSCIPTION ###
      ############################
      else:
        with connection.cursor() as cursor:
          if removeService(cursor,
                           session.get("user_id"),
                           service):
            flash("You are unsubscribed from " + service + "!!",
                category="success")
            session["all_services"] = getAllServices(cursor, session.get("current_sub_filter"))
          else:
            flash("Error encountered when removing service. Please try again.",
                category="error")
        
          userServices = getAllUserServices(cursor, session.get("user_id"))
          session["user_services"] = userServices
          session["user_recs"] = get_user_recommendations(cursor, session.get("user_id"))
          session["total_monthly_cost"] = getTotalCost(cursor, session.get("user_id"))

        connection.commit()
        connection.close()
        return render_template("subscriptions.html", 
                               session=True, 
                               logged_in=True, 
                               option="my_sub", 
                               data=session.get("user_services"),
                               recommended=session.get("user_recs"),
                               total_cost=session["total_monthly_cost"])

  else:
    return render_template("subscriptions.html", 
                           session=True, 
                           logged_in=True, 
                           option="all_sub", 
                           data=None)


#===============#
#=== Explore ===#
#===============#
@views.route("/explore", methods=["GET", "POST"])
def explore():
  
  # If Database not Connected - Route Home
  if not session.get("db_connected"):
    return redirect(url_for("auth.home"))

  # If Not Logged In - Route to Login
  if not session.get("logged_in"):
    return redirect(url_for("auth.login"))
  
  if request.method == "GET":
    # Open a Connection To Get all movie Data 
    connection = getConnection(session.get("hostName"),
                               session.get("userName"),
                               session.get("userPassword"))

    #########################
    ### GET ALL FAVORITES ###
    #########################
    with connection.cursor() as cursor:
      if not session.get("current_favorite_filter"):
        session["current_favorite_filter"] = FILTER_TYPES[4]
      
      allFavoriteData = getUserFavorites(cursor, 
                                         session.get("user_id"),
                                         session.get("current_favorite_filter"))
      session["all_favorites"] = allFavoriteData
      connection.commit()
      connection.close()
      
    return render_template("explore.html", 
                           session=True, 
                           logged_in=True, 
                           option="all_favorites",  
                           data=session.get("all_favorites"))

  """
  User Interaction with toggle tabs
  """
  if request.method == "POST":
    connection = getConnection(session.get("hostName"),
                              session.get("userName"),
                              session.get("userPassword"))
    ######################
    ### GET ALL MOVIES ###
    ######################
    if "all_movies" in request.form:      
      with connection.cursor() as cursor:
        if not session.get("current_movie_filter"):
          session["current_movie_filter"] = FILTER_TYPES[4]

        allMovieData = getAllMovies(cursor, session.get("current_movie_filter"))
        session["all_movies"] = allMovieData
        connection.commit()
        connection.close()
        
      return render_template("explore.html", 
                            session=True, 
                            logged_in=True, 
                            option="all_movies",  
                            data=session.get("all_movies"))

    ########################
    ### GET ALL TV SHOWS ###
    ########################
    elif "all_tv" in request.form:      
      with connection.cursor() as cursor:
        if not session.get("current_tv_filter"):
          session["current_tv_filter"] = FILTER_TYPES[4]

        allTVData = getAllTvShows(cursor, session.get("current_tv_filter"))
        session["all_tv"] = allTVData
        connection.commit()
        connection.close()
        
      return render_template("explore.html", 
                            session=True, 
                            logged_in=True, 
                            option="all_tv",  
                            data=session.get("all_tv"))

    #########################
    ### GET ALL FAVORITES ###
    #########################
    elif "all_favorites" in request.form:
      return redirect(url_for("views.explore"))

    ###################################
    ### GET SEARCH RESULTS - MOVIES ###
    ###################################
    elif "movie_search" in request.form:
      searchKey = request.form.get("movie_search")
      with connection.cursor() as cursor:
        searchData = get_movie_search(cursor, searchKey)
        connection.commit()
        connection.close()
        
      return render_template("explore.html", 
                            session=True, 
                            logged_in=True, 
                            option="all_movies",  
                            data=searchData)

    ####################################
    ### GET SEARCH RESULTS - TV SHOW ###
    ####################################
    elif "tv_search" in request.form:
      searchKey = request.form.get("tv_search")
      with connection.cursor() as cursor:
        searchData = get_tv_search(cursor, searchKey)
        connection.commit()
        connection.close()
        
      return render_template("explore.html", 
                            session=True, 
                            logged_in=True, 
                            option="all_tv",  
                            data=searchData)

    #####################################
    ### USER FAVORITED or UNFAVORITED ###
    #####################################
    else:
      print(list(request.form))
      buttonInfo = list(request.form)[0].split("-")
      favorite_class = buttonInfo[0].strip()
      content_id = buttonInfo[1].strip()
      type = buttonInfo[2].strip()

      # Create a connection for Update / Delete
      connection = getConnection(session.get("hostName"),
                                session.get("userName"),
                                session.get("userPassword"))

      #################
      ### FAVORITED ###
      #################
      if favorite_class == "favorite":      
        with connection.cursor() as cursor:
          if checkUserFavoriteExists(cursor,
                                    session.get("user_id"),
                                    content_id):
                        
              connection.close()
              flash("You Have Already Favorited This!!",
                    category="success")
          else:
              if addNewFavorite(cursor,
                                session.get("user_id"),
                                content_id):
                flash("You have a new favorite!!",
                    category="success")
                session["all_favorites"] = getUserFavorites(cursor, 
                                                            session.get("user_id"), 
                                                            session.get("current_sub_filter"))
              else:
                flash("Error encountered when adding favorite. Please try again.",
                    category="error")
                
              connection.commit()
              connection.close()
        
          if type == "Movie":
            return render_template("explore.html", 
                                    session=True, 
                                    logged_in=True, 
                                    option="all_movies", 
                                    data=session.get("all_movies"))
          else:
            return render_template("explore.html", 
                          session=True, 
                          logged_in=True, 
                          option="all_tv", 
                          data=session.get("all_tv"))

      ###################
      ### UNFAVORITED ###
      ###################
      else:
        with connection.cursor() as cursor:
          if checkUserFavoriteExists(cursor,
                                     session.get("user_id"),
                                     content_id):
                        
            if removeFavorite(cursor,
                              session.get("user_id"),
                              content_id):
              flash("You have removed a favorite!!",
                  category="success")
              session["all_favorites"] = getUserFavorites(cursor, 
                                                          session.get("user_id"), 
                                                          session.get("current_sub_filter"))
            else:
              flash("Error encountered when removing favorite. Please try again.",
                  category="error")
                
        connection.commit()
        connection.close()
        
        return redirect(url_for("views.explore"))
 
  else:
    return render_template("explore.html", 
                          session=True, 
                          logged_in=True)


#==================#
#=== My Account ===#
#==================#
@views.route("/my-account", methods=["GET", "POST"])
def myAccount():

  # If Database not Connected - Route Home
  if not session.get("db_connected"):
    return redirect(url_for("auth.home"))

  # If Not Logged In - Route to Login
  if not session.get("logged_in"):
    return redirect(url_for("auth.login"))

  if request.method == 'POST':

    if 'update_password' in request.form:
      return redirect(url_for("views.updatePassword"))
    elif 'payment' in request.form:
      return redirect(url_for("views.payment"))
    elif 'billing' in request.form:
      return redirect(url_for("views.billing"))
    elif 'stats' in request.form:
      return redirect(url_for("views.viewStats"))

  else:
    return render_template("myAccount.html",
                         info=session.get("user_acct_info"), 
                         session=True, 
                         logged_in=True)




#=======================#
#=== Update Password ===#
#=======================#
@views.route("/password-update", methods=["GET", "POST"])
def updatePassword():

  # If Database not Connected - Route Home
  if not session.get("db_connected"):
    return redirect(url_for("auth.home"))

  # If Not Logged In - Route to Login
  if not session.get("logged_in"):
    return redirect(url_for("auth.login"))


  if request.method == 'POST':
  # Create a connection for Update / Delete
    connection = getConnection(session.get("hostName"),
                                  session.get("userName"),
                                  session.get("userPassword"))
    with connection.cursor() as cursor:
      if request.form.get("new_password") == request.form.get("re_new_password"):
        if checkPasswordValidity(cursor, session.get("user_id"), request.form.get("current_password"), request.form.get("new_password")):
          flash("Password successfully updated!", category="sucess")
        else:
          flash("Error while password update!", category="error")
      else:
          flash("Passwords do not match!", category="error")

    connection.commit()
    connection.close() # Close the connection
                              
    return redirect(url_for("views.myAccount"))

  else:
    return render_template("update_password.html", 
                         session=True, 
                         logged_in=True)


#=======================#
#======  Payments ======#
#=======================#
@views.route("/payment", methods=["GET", "POST"])
def payment():

  # If Database not Connected - Route Home
  if not session.get("db_connected"):
    return redirect(url_for("auth.home"))

  # If Not Logged In - Route to Login
  if not session.get("logged_in"):
    return redirect(url_for("auth.login"))


  if request.method == 'POST':
    action_type = list(request.form)[0].split('_')[0]
    action_id = list(request.form)[0].split('_')[-1]

    if 'add_card' in request.form:
      return redirect(url_for("views.addCard"))


    elif action_type == 'delete':
      connection = getConnection(session.get("hostName"),
                                        session.get("userName"),
                                        session.get("userPassword"))
      with connection.cursor() as cursor:
        deleteCard(cursor, action_id)
      
      flash("Payment successfully deleted!", category="sucess")

      connection.commit()
      connection.close() # Close the connection
      
      return redirect(url_for("views.payment"))

  else:
    # Create a connection for Update / Delete
    connection = getConnection(session.get("hostName"),
                                  session.get("userName"),
                                  session.get("userPassword"))
    with connection.cursor() as cursor:
      session["payment_options"] = getPaymentOptions(cursor, session["user_id"])

    connection.commit()
    connection.close() # Close the connection

    return render_template("payment.html", 
                         session=True, 
                         logged_in=True, 
                         data=session["payment_options"])




#=======================#
#====== Add card =======#
#=======================#
@views.route("/add-card", methods=["GET", "POST"])
def addCard():

  # If Database not Connected - Route Home
  if not session.get("db_connected"):
    return redirect(url_for("auth.home"))

  # If Not Logged In - Route to Login
  if not session.get("logged_in"):
    return redirect(url_for("auth.login"))


  if request.method == 'POST':
    # Create a connection for Update / Delete
    if len(str(request.form['card_number'])) != 16:
      flash("Please enter valid 16 digit card number!", category="error")
      return redirect(url_for("views.payment"))

    connection = getConnection(session.get("hostName"),
                                  session.get("userName"),
                                  session.get("userPassword"))

    with connection.cursor() as cursor:
      addNewCard(cursor, str(request.form['card_number']), request.form['card_type'], \
                int(request.form['security_code']), str(request.form['month']), str(request.form['year']))
      connectCardUser(cursor, session["user_id"], str(request.form['card_number']))
      addBillingAddress(cursor,  str(request.form['card_number']), str(request.form['street_name']), str(request.form['city']), \
                str(request.form['state']), str(request.form['zip_code']))        
    
    connection.commit()
    connection.close() # Close the connection              
    return redirect(url_for("views.payment"))

  else:
    return render_template("add_card.html", 
                         session=True, 
                         logged_in=True)


#=======================#
#======  Billing  ======#
#=======================#
@views.route("/billing", methods=["GET", "POST"])
def billing():

  # If Database not Connected - Route Home
  if not session.get("db_connected"):
    return redirect(url_for("auth.home"))

  # If Not Logged In - Route to Login
  if not session.get("logged_in"):
    return redirect(url_for("auth.login"))


  if request.method == 'POST':
    # Create a connection for Update / Delete
    connection = getConnection(session.get("hostName"),
                                  session.get("userName"),
                                  session.get("userPassword"))
    try:
      month = request.form.get("month")
      year = request.form.get("year")
    except:
      month = datetime.now().month
      year = datetime.now().year

    with connection.cursor() as cursor:
      result = getBill(cursor, month, year, session.get("user_id"))
      total_cost = getTotal(cursor, month, year, session.get("user_id"))

    if result and total_cost:
      connection.commit()
      connection.close() # Close the connection
      return render_template("billing.html", 
                              session=True, 
                              logged_in=True,
                              result=result,
                              year=year,
                              month=month,
                              month_name=calendar.month_abbr[int(month)],
                              total_cost=total_cost)
    else:
      connection.commit()
      connection.close() # Close the connection
      flash("Data does not exist for the inputed month and year!", category="error")
      return redirect(url_for("views.myAccount"))

                  

  else:
    # Create a connection for Update / Delete
    connection = getConnection(session.get("hostName"),
                                  session.get("userName"),
                                  session.get("userPassword"))
    month = datetime.now().month
    year = datetime.now().year
    with connection.cursor() as cursor:
      result = getBill(cursor, month, year, session.get("user_id"))
      total_cost = getTotal(cursor, month, year, session.get("user_id"))

    if result and total_cost:    
      connection.commit()
      connection.close() # Close the connection

      return render_template("billing.html", 
                          session=True, 
                          logged_in=True,
                          result=result, 
                          month=month,
                          year=year,
                          month_name=calendar.month_abbr[int(month)],
                          total_cost=total_cost)
    else:
      connection.commit()
      connection.close() # Close the connection
      flash("Data does not exist for the inputed month and year!", category="error")
      return redirect(url_for("views.myAccount"))



#=======================#
#===== View Stats ======#
#=======================#
@views.route("/stats", methods=["GET", "POST"])
def viewStats():

  # If Database not Connected - Route Home
  if not session.get("db_connected"):
    return redirect(url_for("auth.home"))

  # If Not Logged In - Route to Login
  if not session.get("logged_in"):
    return redirect(url_for("auth.login"))


  if request.method == 'POST':
    # Create a connection for Update / Delete
    connection = getConnection(session.get("hostName"),
                                  session.get("userName"),
                                  session.get("userPassword"))
    try:
      month = request.form.get("month")
      year = request.form.get("year")
    except:
      month = datetime.now().month
      year = datetime.now().year
  
    with connection.cursor() as cursor:
      mostViewed = getMostViewed(cursor, month, year, session.get("user_id"))
      mostBilled = getMostBilled(cursor, month, year, session.get("user_id"))

    if mostViewed and mostBilled:  
      connection.commit()
      connection.close() # Close the connection
      return render_template("stats.html", 
                          session=True, 
                          logged_in=True,
                          year=year,
                          month=month,
                          month_name=calendar.month_abbr[int(month)],
                          mostViewed_img=mostViewed['image'],
                          mostViewed_name=mostViewed['name'],
                          mostViewed_time_spent=round(mostViewed['time_spent'], 2),
                          mostBilled_img=mostBilled['image'],
                          mostBilled_name=mostBilled['name'],
                          mostBilled_cost=round(mostBilled['cost'], 2))
    else:
        flash("Data does not exist for the inputed month and year!", category="error")
        return redirect(url_for("views.myAccount"))

  else:
    # Create a connection for Update / Delete
    connection = getConnection(session.get("hostName"),
                                  session.get("userName"),
                                  session.get("userPassword"))
    month = datetime.now().month
    year = datetime.now().year
    with connection.cursor() as cursor:
      mostViewed = getMostViewed(cursor, month, year, session.get("user_id"))
      mostBilled = getMostBilled(cursor, month, year, session.get("user_id"))

    if mostBilled and mostViewed:    
      connection.commit()
      connection.close() # Close the connection

      return render_template("stats.html", 
                          session=True, 
                          logged_in=True,
                          month=month,
                          year=year,
                          month_name=calendar.month_abbr[int(month)],
                          mostViewed_img=mostViewed['image'],
                          mostViewed_name=mostViewed['name'],
                          mostViewed_time_spent=round(mostViewed['time_spent'], 2),
                          mostBilled_img=mostBilled['image'],
                          mostBilled_name=mostBilled['name'],
                          mostBilled_cost=round(mostBilled['cost'], 2))
    else:
      connection.commit()
      connection.close() # Close the connection
      flash("Data does not exist for the inputed month and year!", category="error")
      return redirect(url_for("views.myAccount"))