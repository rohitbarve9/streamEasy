|================================|
|=== STREAM EASY APPLICATION  ===|
|================================|
  Team: Rohit Barve, Daniel Ryan
  Team Name: RyanDBarveR
  Course: 5200 Database Management Systems
  Semester: Fall 2022
  Assignment: Final Project


|================================|
|===        OVERVIEW          ===|
|================================|
StreamEasy provides users a pay-as-you-go alternative to monthly streaming services.
Additionally, StreamEasy's application provides users with a dashboard containing all 
of their current subscriptions, as well as recommended content and available services. 
Users can browse a vast library of content, track their favorite shows and monitor their
spending activity all in one place. Refer to the sections within for additional details
on how to access and run the application.


|================================|
|===   TECHNOLOGIES UTILIZED  ===|
|================================|
  FRONT END: Flask (Python), Jinja (Flask/Python), HTML, CSS
  BACK END: Python, SQL
  DATABASE: MySQL
  DATABASE CONNECTOR: PyMySQL


|================================|
|=== APPLICATION DEPENDENCIES ===|
|================================|
  * PYTHON LIBRARIES:
    - Flask
    - flask_session
    - pymysql
    - cryptography

  * APPLICATIONS:
    - MySQL Workbench
      * Must have a local server running on localhost
    - IDE (Optional)
    - Terminal
    - Internet Browser (Chrome, Opera, etc.)

  * FILES:
    streamEasy
    │   README.txt
    │   main.py
    │
    └───database
    │      __init__.py
    │      dbHelpers.py
    │      streamEasy.sql
    │   
    └───website
        │  __init__.py
        │  auth.py
        │  views.py
        │
        └───templates
        │     base.html
        │     add_card.html
        │     billing.html
        │     explore.html
        │     home.html
        │     login.html
        │     myAccount.html
        │     payment.html
        │     signUp.html
        │     stats.html
        │     subscriptions.html
        │     update_password.html
        │
        └───static
            │
            └───images
                  Amazon-Prime-Video-Logo.png
                  Apple-TV-logo.png
                  Disney+_logo.png
                  HBO-Max-Logo.png
                  Hulu-logo.png
                  Netflix-Logo.png
                  Paramount+_logo.png
                  Showtime-logo.png
                  profile_picture.png
    
    
|================================|
|=== INSTRUCTIONS FOR RUNNING ===|
|================================|
  Please read each of the instructions below carfully in order to successfully run
  the application. At this point, all dependencies should be downloaded; however,
  instructions are also provided below on how to download the dependencies.
  
  * DOWNLOADING DEPENDENCIES:
  ---------------------------
    - Ensure you have the "streamEasy" folder referenced in the dependencies section above
        - Store the folder in a location you are comfortable navigating to from the command line.
          If in doubt, store in your home directory and navigation instructions will be provided below.
    - Install all required Python libraries
      All commands provided below will be preceded by a '$'. This is to indicate it is
      a command. Please DO NOT include the '$' in your command.
        $ pip install Flask
        $ pip install flask_session
        $ pip install pymysql
        $ pip install cryptography
    - Install MySQL Workbench (if not already installed)
        - https://www.mysql.com/products/workbench/
        
  * SETTING UP THE DATABASE:
  ---------------------------
    - In MySQL Workbench: Open or Set Up a new localhost SQL server
        - Ensure you remember the host, username and password for the server
    - Open (in your MySQL server) the "streamEasy.sql" file in the path: streamEasy/database/streamEasy.sql
        - Run the entire file
            - After running the file, you should have a stream_easy database in your schema
            
  * SETTING UP FLASK:
  -------------------
    - Open your terminal or command line (instructions are provided in bash/zsh)
      All commands provided below will be preceded by a '$'. This is to indicate it is
      a command. Please DO NOT include the '$' in your command.
        
        * NAVIGATING TO THE FOLDER:
        ---------------------------
        - If your file is located in your home directory execute the following command from your home directory:
            $ cd streamEasy
        - If your file is not located in your home directory use the below command to navigate to the correct directory:
            $ cd <folder name>/<sub-folder name>/ ... /streamEasy
       
        * STARTING UP THE FLASK SERVER:
        -------------------------------
        - From the streamEasy directory, execute the following command:
            $ flask --app main.py run

        - After the above command is executed, you should see something similar to the following:
            """
                * Serving Flask app 'main.py'
                * Debug mode: off
                  WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
                  * Running on http://127.0.0.1:5000
            """
        
        - Open Your Browser:
            - Copy and paste the http address (in this case http://127.0.0.1:5000) following "Running on.." into your browser
            
            
  * RUNNING THE APPLICATION:
  --------------------------
    - At this point, your SQL Database should be setup, flask server should be running, and the application should be running in
      your browser of choice.
      
    - CONNECT TO DATABASE PAGE:
        - Enter valid host (likely localhost)
        - Enter valid username (likely root)
        - Enter password for server
    
    - LOGIN:
        - Enter valid username
        - Enter valid password
        * If NOT SIGNED UP --> click on the Sign Up link
    
    - SIGN-UP
         - Enter valid information for all fields
         - Once signed up, Login via the Login Page
         
    - POST-LOGIN PAGES:
        - All post login pages "My Account", "Subscriptions", "Explore" allow the user to perform
          CRUD operations on the database.

  


            
