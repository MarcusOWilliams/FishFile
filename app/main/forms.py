from flask import request
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import (
    StringField,
    SubmitField,
    DateTimeField,
    IntegerField,
    SelectField,
    BooleanField,
    DateField,
    TextAreaField,
)
from wtforms.validators import DataRequired, ValidationError, Optional
from app.models import Fish, User


class SimpleSearch(FlaskForm):
    search = StringField("Search by fish tank ID", validators=[DataRequired()])
    submit = SubmitField("Search")

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super(SimpleSearch, self).__init__(*args, **kwargs)


class NewFish(FlaskForm):
    fish_id = StringField("* Fish ID", validators=[DataRequired()])
    tank_id = StringField("* Tank ID", validators=[DataRequired()])
    status = SelectField(
        "* Status",
        choices=["Alive", "Alive (Healthy)", "Alive (Unhealthy)", "Dead"],
        validators=[DataRequired()],
    )
    stock = StringField("* Stock #", validators=[DataRequired()])
    protocol = IntegerField("Protocol #", validators=[Optional()])
    comments = TextAreaField("Comments", validators=[Optional()])
    source = SelectField("* Source", choices=["Home", "Imported"])
    cross_type = StringField("* Cross Type", validators=[DataRequired()])

    birthday = DateField("* Birthday", validators=[DataRequired()])
    date_of_arrival = DateField("Date of Arrival", validators=[Optional()])

    user_code = SelectField("* User Code", validators=[DataRequired()], coerce=str)
    project_license = SelectField(
        "* Project License", validators=[DataRequired()], coerce=str
    )

    allele = StringField("Allele",validators=[Optional()])
    mutant_gene = StringField("* Mutant Gene", validators=[DataRequired()])
    transgenes = StringField("Transgenes", validators=[Optional()])

    father_id = StringField("* Father's ID", validators=[DataRequired()])
    mother_id = StringField("* Mother's ID", validators=[DataRequired()])
    father_stock = StringField("* Father's Stock #", validators=[DataRequired()])
    mother_stock = StringField("* Mother's Stock #", validators=[DataRequired()])

    males = IntegerField("* # Males")
    females = IntegerField("* # Females")
    unsexed = IntegerField("* # Unsexed")
    carriers = IntegerField("* # Carriers/Licenced")
    total = IntegerField("* Total #")

    alert_date = DateField("Reminder date", validators=[Optional()])
    alert_msg = StringField("Reminder message", validators=[Optional()])

    submit = SubmitField("Add Fish")

    def validate_father_stock(self, father_stock):
        fish = Fish.query.filter_by(
            fish_id=self.father_id.data, stock=father_stock.data
        ).first()
        if fish is None:
            raise ValidationError(
                f"There are no fish in the database that match ID = {self.father_id.data} and Stock = {father_stock.data}"
            )

    def validate_mother_stock(self, mother_stock):
        fish = Fish.query.filter_by(
            fish_id=self.mother_id.data, stock=mother_stock.data
        ).first()
        if fish is None:
            raise ValidationError(
                f"There are no fish in the database that match ID = {self.mother_id.data} and Stock = {mother_stock.data}"
            )

    def validate_males(self, males):
        if males.data < 0:
            raise ValidationError("The number of males must not be negative")

    def validate_females(self, females):
        if females.data < 0:
            raise ValidationError("The number of females must not be negative")

    def validate_unsexed(self, unsexed):
        if unsexed.data < 0:
            raise ValidationError("The number of unsexed fish must not be negative")

    def validate_carriers(self, carriers):
        if carriers.data < 0:
            raise ValidationError("The number of carriers must not be negative")

    def validate_total(self, total):
        if total.data < 0:
            raise ValidationError("The total number of fish must not be negative")



class FilterChanges(FlaskForm):
    fish_id = BooleanField("Fish ID")
    tank_id = BooleanField("Tank ID")
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
    comments = BooleanField("Comments")
    submit = SubmitField("Apply")


class SearchFrom(FlaskForm):
    fish_id = StringField("Fish ID", validators=[Optional()])
    tank_id = StringField("Tank ID", validators=[Optional()])
    status = SelectField(
        "Status",
        choices=["", "Alive", "Alive (Healthy)", "Alive (Unhealthy)", "Dead"],
        validators=[Optional()],
    )
    stock = StringField("Stock #", validators=[Optional()])
    protocol = IntegerField("Protocol #", validators=[Optional()])
    source = SelectField(
        "Source", choices=["", "Home", "Imported"], validators=[Optional()]
    )
    cross_type = StringField("Cross Type", validators=[Optional()])
    birthday = DateField("Birthday", validators=[Optional()])
    date_of_arrival = DateField("Date of Arrival", validators=[Optional()])
    user_code = StringField("User Code", validators=[Optional()])
    project_license = StringField("Project License", validators=[Optional()])
    allele = StringField("Allele", validators=[Optional()])
    mutant_gene = StringField("Mutant Gene", validators=[Optional()])
    transgenes = StringField("Transgenes", validators=[Optional()])
    father_id = StringField("Father's ID", validators=[Optional()])
    mother_id = StringField("Mother's ID", validators=[Optional()])
    father_stock = StringField("Father's Stock #", validators=[Optional()])
    mother_stock = StringField("Mother's Stock #", validators=[Optional()])
    total = IntegerField("Total #", validators=[Optional()])
    order = SelectField("Order By:", validators=[DataRequired()], choices=["Newest Added", "Oldest Added","Fish ID", "Tank ID","Stock","Age ( young -> old )","Age (old -> young)"])
    submit = SubmitField("Search")


class SettingsForm(FlaskForm):
    emails = BooleanField("Email notifications:")
    email_reminders = BooleanField("Email reminders:")

    add_notifications = BooleanField("Entry added under your user code:")
    change_notifications = BooleanField("Change made to entry under your user code:")
    turnover_notifications = BooleanField("Custom reminders:")
    age_notifications = BooleanField("Alerts when fish under your user code reach a certain age:")

    pl_add_notifications = BooleanField("Fish added under your project license:")
    pl_turnover_notifications = BooleanField("Custom reminders for all fish under your project license:")
    pl_age_notifications = BooleanField("Fish age reminders for all fish under your project license:")

    project_license = StringField("Project License:")

    submit = SubmitField("Apply")

    def validate_project_license(self, project_license):
        if project_license.data and project_license.data != "":
            user = User.query.filter_by(project_license = project_license.data).first()
            if user is not None and user != current_user:
                raise ValidationError("This project license is already associated with another user")


class RoleChange(FlaskForm):
    role = SelectField('Update Role:', validators=[DataRequired()], coerce=str)
    submit= SubmitField('Change')

class OrderForm(FlaskForm):
    order = SelectField("Order By:", validators=[DataRequired()], choices=["Fish ID", "Tank ID","Stock","Age ( young -> old )","Age (old -> young)", "Newest Added", "Oldest Added"])
    submit = SubmitField("Apply")

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')