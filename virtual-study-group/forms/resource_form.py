from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired, Length

class ResourceUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    file = FileField('Upload File', validators=[DataRequired()])
    submit = SubmitField('Upload Resource')
