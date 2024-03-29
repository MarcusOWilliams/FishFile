# This is the main project file that is responsible for running the app
# What it does is import the app from the app folder and call the required methods to run the app
# this file is declared as the flask_app in the env file, so when running the virtual environment, this is the file that is run
# to Run the file activate the venv using venv\scripts\activate in the terminal (windows) then type "flask run"
from app import create_app, db
from app.models import Allele, Photo, User, Fish, Change, Settings, Notification, Reminder, Stock, Transgene


app = create_app()


# this part allows you to run a python interpreter session in the context of the flask app using the 'flask shell' command
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Fish': Fish, 'Change': Change, 'Settings': Settings, 'Notification': Notification, 'Reminder':Reminder, 'Allele':Allele, 'Photo':Photo, 'Stock':Stock, 'Transgene':Transgene}
