#This is the main project file that is responsible for running the app
#What it does is import the app from the app folder and call the required methods to run the app
#this file is declared as the flask_app in the env file, so when running the virtual environment, this is the file that is run
from app import app

if __name__ == '__main__':
    app.run()