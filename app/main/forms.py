from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, IntegerField, SelectField, BooleanField, DateField, TextAreaField
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
    tank_id = StringField('Tank ID', validators=[DataRequired()])
    status = SelectField("Status", choices=["Alive", "Alive (Healthy)", "Alive (Unhealthy)", "Dead"], validators=[DataRequired()])
    stock = StringField("Stock #", validators=[DataRequired()])
    protocol = IntegerField("Protocol #")
    comments = TextAreaField("Comments")
    source = SelectField("Source", choices = ["Home", "Imported"])
    cross_type = StringField("Cross Type", validators=[DataRequired()])

    birthday = DateField("Birthday", validators=[DataRequired()])
    date_of_arrival = DateField("Date of Arrival")

    user_code = StringField("User Code", validators=[DataRequired()])
    project_license = StringField("Project License", validators=[DataRequired()])

    allele = StringField("Allele")
    mutant_gene = StringField("Mutant Gene", validators=[DataRequired()])
    transgenes = StringField("Transgenes")

    father_id = StringField("Father's ID")
    mother_id = StringField("Mother's ID")
    father_stock = StringField("Father's Stock #")
    mother_stock = StringField("Mother's Stock #")

    males = IntegerField("# Males")
    females = IntegerField("# Females")
    unsexed = IntegerField("# Unsexed")
    carriers = IntegerField("# Carriers/Licenced")
    total = IntegerField("Total #")
    

    submit = SubmitField('Add Fish')


    def validate_father_stock(self, father_stock):
        fish = Fish.query.filter_by(fish_id = self.father_id.data, stock=father_stock.data).first()
        if fish is None:
            raise ValidationError(
                f'There are no fish in the database that match ID = {self.father_id.data} and Stock = {father_stock.data}')

    def validate_mother_stock(self, mother_stock):
        fish = Fish.query.filter_by(fish_id = self.mother_id.data, stock=mother_stock.data).first()
        if fish is None:
            raise ValidationError(
                f'There are no fish in the database that match ID = {self.mother_id.data} and Stock = {mother_stock.data}')

    def validate_males(self, males):
        if males.data<0:
            raise ValidationError(
                'The number of males must not be negative')
    def validate_females(self, females):
        if females.data<0:
            raise ValidationError(
                'The number of females must not be negative')
    def validate_unsexed(self, unsexed):
        if unsexed.data<0:
            raise ValidationError(
                'The number of unsexed fish must not be negative')
    def validate_carriers(self, carriers):
        if carriers.data<0:
            raise ValidationError(
                'The number of carriers must not be negative')
    def validate_total(self, total):
        if total.data<0:
            raise ValidationError(
                'The total number of fish must not be negative')
    

        

class FilterChanges(FlaskForm):
    fish_id = BooleanField('Fish ID')
    tank_id = BooleanField('Tank ID')
    status = BooleanField("Status")
    stock = BooleanField("Stock #")
    protocol = BooleanField("Protocol #")
    comments = BooleanField("Comments")
    source = BooleanField("Source")
    cross_type = BooleanField("Cross Type")
    birthday = BooleanField("Birthday")
    date_of_arrival = BooleanField("Date of Arrival")
    user_code = BooleanField("User Code")
    project_license = BooleanField("Project License")
    allele = BooleanField("Allele")
    mutant_gene = BooleanField("Mutant Gene")
    transgenes = BooleanField("Transgenes")
    father_id = BooleanField("Father's ID")
    mother_id = BooleanField("Mother's ID")
    father_stock = BooleanField("Father's Stock #")
    mother_stock = BooleanField("Mother's Stock #")
    males = BooleanField("# Males")
    females = BooleanField("# Females")
    unsexed = BooleanField("# Unsexed")
    carriers = BooleanField("# Carriers/Licenced")
    total = BooleanField("Total #")
    submit = SubmitField('Apply')

class SettingsForm(FlaskForm):
    emails = BooleanField('Email notifications:')
    submit = SubmitField('Apply')
