from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, IntegerField, SelectField
from wtforms.validators import DataRequired, ValidationError
from app.models import Fish

class SearchForm(FlaskForm):
    search = StringField('Search by fish id', validators=[DataRequired()])
    submit = SubmitField('Search')

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

class NewFish(FlaskForm):
    fish_id = StringField('Fish ID', validators=[DataRequired()])
    birthday = DateTimeField("Birthday")
    date_of_arrival = DateTimeField("Date Of Arrival")
    stock = StringField()
    project_license = StringField()
    status = SelectField()
    allele = StringField()
    sex = SelectField()
    mutant_gene = StringField()
    transgenes = StringField()
    protocol = SelectField()
    comments = StringField()
    father_id = StringField()
    mother_id = StringField()
    
    def validate_father_id(self, father_id):
        fish = Fish.query.filter_by(fish_id = father_id).first()
        if fish is None:
             raise ValidationError('The father_id does not match any fish currently in the database.')
        
    
    def validate_mother_id(self, mother_id):
        fish = Fish.query.filter_by(fish_id = mother_id).first()
        if fish is None:
            raise ValidationError('The mother_id does not match any fish currently in the database.')
        
