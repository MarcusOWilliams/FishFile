#This is the main project file that is responsible for running the app
#What it does is import the app from the app folder and call the required methods to run the app
#this file is declared as the flask_app in the env file, so when running the virtual environment, this is the file that is run
#to Run the file activate the venv using venv\scripts\activate in the terminal (windows) then type "flask run"
from app import create_app

app = create_app()
