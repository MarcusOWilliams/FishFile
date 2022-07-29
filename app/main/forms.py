import os
import sys
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
    SelectMultipleField,
    MultipleFileField,
    FileField,
)
from wtforms.validators import DataRequired, ValidationError, Optional
from app.models import Allele, Fish, User, get_all_allele_names
import validators


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
    tank_id = StringField("* Tank #", validators=[DataRequired()])
    status = SelectField(
        "* Status",
        choices=["Alive", "Alive (Healthy)", "Alive (Unhealthy)", "Dead"],
        validators=[DataRequired()],
    )
    stock = StringField("* Stock #", validators=[DataRequired()])
    protocol = IntegerField("Protocol #", validators=[Optional()])
    comments = TextAreaField("Comments", validators=[Optional()])
    links = TextAreaField("Additional links", validators=[Optional()])
    photos = MultipleFileField("Upload pictures", validators=[Optional()])

    source = StringField("* Source", validators=[DataRequired()])
    cross_type = StringField("* Cross Type", validators=[DataRequired()])

    birthday = DateField("* Birthday", validators=[DataRequired()])
    date_of_arrival = DateField("Date of Arrival", validators=[Optional()])

    user_code = SelectField("* User Code", coerce=str)
    custom_code = StringField("* User Code")
    project_license = SelectField(
        "* Project License", coerce=str
    )
    custom_license = StringField("* User License")

    allele = SelectMultipleField("Allele", coerce=str, validators=[Optional()])
    mutant_gene = TextAreaField("* Mutant Gene", validators=[DataRequired()])
    transgenes = TextAreaField("Transgenes", validators=[Optional()])

    father_tank_id = StringField("Father's Tank #", validators=[Optional()])
    mother_tank_id = StringField("Mother's Tank #", validators=[Optional()])
    father_stock = StringField("Father's Stock #", validators=[Optional()])
    mother_stock = StringField("Mother's Stock #", validators=[Optional()])

    males = IntegerField("* # Males")
    females = IntegerField("* # Females")
    unsexed = IntegerField("* # Unsexed")
    carriers = IntegerField("* # Carriers/Licensed")
    total = IntegerField("* Total #")
    origin_tank_id = StringField("Origin Tank #", validators=[Optional()])
    origin_tank_stock = StringField("Origin Stock #", validators=[Optional()])
    alert_date = DateField("Reminder date", validators=[Optional()])
    alert_msg = StringField("Reminder message", validators=[Optional()])

    total_change_comment= TextAreaField("Add a note", validators=[Optional()])

    submit = SubmitField("Add Fish")

    def validate_father_stock(self, father_stock):
        if self.father_tank_id.data == None or self.father_tank_id.data == "":
            raise ValidationError(
                f"To add a father you must supply both tank # and stock # for the father."
            )
        fish = Fish.query.filter_by(
            tank_id=self.father_tank_id.data.upper(), stock=father_stock.data.upper()
        ).first()
        if fish is None:
            raise ValidationError(
                f"There are no fish in the database that match Tank # = {self.father_tank_id.data} and Stock = {father_stock.data}"
            )

    def validate_father_tank_id(self, father_tank_id):

        if self.father_stock.data == None or self.father_stock.data == "":
            raise ValidationError(
                f"To add a father you must supply both id and stock # for the father."
            )

    def validate_mother_stock(self, mother_stock):
        if self.mother_tank_id.data == None or self.mother_tank_id.data == "":
            raise ValidationError(
                f"To add a mother you must supply both id and stock # for the mother."
            )
        fish = Fish.query.filter_by(
            tank_id=self.mother_tank_id.data.upper(), stock=mother_stock.data.upper()
        ).first()
        if fish is None:
            raise ValidationError(
                f"There are no fish in the database that match tank # = {self.mother_tank_id.data} and Stock = {mother_stock.data}"
            )

    def validate_mother_tank_id(self, mother_tank_id):
        if self.mother_stock.data == None or self.mother_stock.data == "":
            raise ValidationError(
                f"To add a mother you must supply both tank # and stock # for the mother."
            )

    def validate_origin_tank_stock(self, origin_tank_stock):
        if self.origin_tank_id.data == "" or self.origin_tank_id.data == None:
            raise ValidationError(
                f"To add an origin tank you must supply both tank # and stock # for the origin tank."
            )
        fish = Fish.query.filter_by(
            tank_id=self.origin_tank_id.data.upper(),
            stock=origin_tank_stock.data.upper(),
        ).first()
        if fish is None:
            raise ValidationError(
                f"There are no entries in the database that match tank # = {self.origin_tank_id.data} and Stock = {origin_tank_stock.data}"
            )

    def validate_origin_tank_id(self, origin_tank_id):
        if self.origin_tank_stock.data == "" or self.origin_tank_stock.data == None:
            raise ValidationError(
                f"To add an origin tank you must supply both tank # and stock # for the origin tank."
            )

    def validate_males(self, males):
        if males.data == None or males.data == "":
            raise ValidationError("This field is required")
        if males.data < 0:
            raise ValidationError("The number of males must not be negative")

    def validate_females(self, females):
        if females.data == None or females.data == "":
            raise ValidationError("This field is required")
        if females.data < 0:
            raise ValidationError("The number of females must not be negative")

    def validate_unsexed(self, unsexed):
        if unsexed.data == None or unsexed.data == "":
            raise ValidationError("This field is required")
        if unsexed.data < 0:
            raise ValidationError("The number of unsexed fish must not be negative")

    def validate_carriers(self, carriers):
        if carriers.data == None or carriers.data == "":
            raise ValidationError("This field is required")
        if carriers.data < 0:
            raise ValidationError("The number of carriers must not be negative")

    def validate_total(self, total):
        if total.data == None or total.data == "":
            raise ValidationError("This field is required")
        if total.data < 0:
            raise ValidationError("The total number of fish must not be negative")

    def validate_links(self, links):
        link_list = links.data.split("\n")
        for link in link_list:
            if not validators.url(link.strip()):
                raise ValidationError(f'The link "{link}" is not a valid URL')

    def validate_photos(self, photos):

        for file in photos.data:
            filename, file_extension = os.path.splitext(file.filename)

            if filename == "" and file_extension=="":
                continue
            if file_extension not in (".jpg", ".jpeg", ".png"):
                raise ValidationError("File must have a .jpg, .jpeg or .png extension")

            if len(file.read()) > 3 * 1024 * 1024:
                raise ValidationError(f"File size must be less than 3MB for each file")
            file.seek(0)

    def validate_user_code(self, user_code):
        if user_code.data == None or user_code.data == "":
            if self.custom_code.data == None or self.custom_code.data == "":
                raise ValidationError("You must enter a user code.")

               


    def validate_project_license(self, project_license):
        if project_license.data == None or project_license.data == "":
            if self.custom_license.data == None or self.custom_license.data == "":
                raise ValidationError("You must enter a project license.")

    
    def validate_custom_code(self, custom_code):
        if custom_code.data != None and custom_code.data != "":
            if self.user_code.data != None and self.user_code.data != "":
                raise ValidationError("You have selected a user code from the list and entered a custom user code, please clear one of these fields (use the link under the input to change fields).")

    def validate_custom_license(self, custom_license):
        if custom_license.data != None and custom_license.data != "":
            if self.project_license.data != None and self.project_license.data != "":
                raise ValidationError("You have selected a project license from the list and entered a custom project license, please clear one of these fields (use the link under the input to change fields).")



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
    father_tank_id = BooleanField("Father's Tank #")
    mother_tank_id = BooleanField("Mother's Tank #")
    father_stock = BooleanField("Father's Stock #")
    mother_stock = BooleanField("Mother's Stock #")
    males = BooleanField("# Males")
    females = BooleanField("# Females")
    unsexed = BooleanField("# Unsexed")
    carriers = BooleanField("# Carriers/Licensed")
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
    source = StringField("Source", validators=[Optional()])
    cross_type = StringField("Cross Type", validators=[Optional()])
    age_older = IntegerField("Min. age (months)", validators=[Optional()])
    age_younger = IntegerField("Max. age (months)", validators=[Optional()])
    user_code = StringField("User Code", validators=[Optional()])
    project_license = StringField("Project License", validators=[Optional()])
    allele = StringField("Allele", validators=[Optional()])
    mutant_gene = StringField("Mutant Gene", validators=[Optional()])
    transgenes = StringField("Transgene", validators=[Optional()])
    total = IntegerField("Total # (>=)", validators=[Optional()])
    order = SelectField(
        "Order By:",
        validators=[DataRequired()],
        choices=[
            "Newest Added",
            "Oldest Added",
            "Fish ID",
            "Tank ID",
            "Stock",
            "Age ( young -> old )",
            "Age (old -> young)",
        ],
    )
    submit = SubmitField("Search")


class SettingsForm(FlaskForm):
    emails = BooleanField("Email notifications:")
    email_reminders = BooleanField("Email reminders for fish under user code:")
    pl_email_reminders = BooleanField("Email reminders for fish under project license:")

    add_notifications = BooleanField("Entry added under your user code:")
    change_notifications = BooleanField("Change made to entry under your user code:")
    custom_reminders = BooleanField("Custom reminders:")
    age_notifications = BooleanField(
        "Alerts when fish under your user code reach a certain age:"
    )

    pl_add_notifications = BooleanField("Fish added under your project license:")
    pl_custom_reminders = BooleanField(
        "Custom reminders for all fish under your project license:"
    )
    pl_age_notifications = BooleanField(
        "Fish age reminders for all fish under your project license:"
    )

    personal_license = StringField("Personal License:")
    personal_license_file = FileField("Personal Licence PDF", validators=[Optional()])

    project_license = StringField("Project License:")
    project_license_file = FileField("Project Licence PDF", validators=[Optional()])

    submit = SubmitField("Apply")

    def validate_project_license(self, project_license):
        if project_license.data and project_license.data != "":
            user = User.query.filter_by(project_license=project_license.data).first()
            if user is not None and user != current_user:
                raise ValidationError(
                    "This project license is already associated with another user"
                )

    def validate_personal_license_file(self, personal_license_file):
        if not personal_license_file.data or personal_license_file.data.filename == "":
            return
        filename, file_extension = os.path.splitext(personal_license_file.data.filename)
        if file_extension not in (".pdf"):
            raise ValidationError("The file must be a pdf file ending in .pdf")
        if len(personal_license_file.data.read()) > 2 * 1024 * 1024:
            raise ValidationError(f"File size must be less than 2MB")
        personal_license_file.data.seek(0)

    def validate_project_license_file(self, project_license_file):
        if not project_license_file.data or project_license_file.data.filename == "":
            return
        filename, file_extension = os.path.splitext(project_license_file.data.filename)
        if file_extension not in (".pdf"):
            raise ValidationError("The file must be a pdf file ending in .pdf")
        if len(project_license_file.data.read()) > 2 * 1024 * 1024:
            raise ValidationError(f"File size must be less than 2MB")
        project_license_file.data.seek(0)


class RoleChange(FlaskForm):
    role = SelectField("Update Role:", validators=[DataRequired()], coerce=str)
    submit = SubmitField("Change")


class OrderForm(FlaskForm):
    order = SelectField(
        "Order By:",
        validators=[DataRequired()],
        choices=[
            "Fish ID",
            "Tank ID",
            "Stock",
            "Age ( young -> old )",
            "Age (old -> young)",
            "Newest Added",
            "Oldest Added",
        ],
    )
    submit = SubmitField("Apply")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class AlleleForm(FlaskForm):
    unidentified = BooleanField("Unidentified:")
    identified = BooleanField("Identified:")
    homozygous = BooleanField("Homozygous:")
    heterozygous = BooleanField("Heterozygous:")
    hemizygous = BooleanField("Hemizygous:")
    submit = SubmitField("Update")


class PhotoCaptionForm(FlaskForm):
    caption = TextAreaField("Caption:")
    submit = SubmitField("Apply")


class EditAlleles(FlaskForm):
    add = StringField("Add an allele", validators=[Optional()])
    remove = StringField("Remove an allele", validators=[Optional()])
    submit = SubmitField("Apply")

    def validate_add(self, add):
        if add.data in get_all_allele_names():
            raise ValidationError("This allele name is already in the list")

    def validate_remove(self, remove):
        print(get_all_allele_names(), file = sys.stderr)
        if remove.data not in get_all_allele_names():
            raise ValidationError(
                "This allele name is not in the list, so can not be removed"
            )
