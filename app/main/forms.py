from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, RadioField
from wtforms.validators import DataRequired


class SurveyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])


class QuestionForm(FlaskForm):
    question_text = StringField('Question Text', validators=[DataRequired()])
    type = RadioField('Question Type',
                      choices=[('text', 'Text'), ('number', 'Number'), ('single_choice', 'Single Choice'),
                               ('multiple_choice', 'Multiple Choice')], default='text')


class QuestionOptionForm(FlaskForm):
    option_text = StringField('Option Text', validators=[DataRequired()])
