from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, URL, Length, Optional

class ScheduleMeetingForm(FlaskForm):
    title = StringField('Meeting Title', validators=[DataRequired(), Length(max=200)])
    date_time = DateTimeLocalField('Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    link = StringField('Meeting Link (Optional)', validators=[Optional(), Length(max=300), URL()])
    submit = SubmitField('Schedule Meeting')

