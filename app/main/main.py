from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound, Forbidden
import uuid

from app import db
from .forms import SurveyForm, QuestionForm, QuestionOptionForm
from .models import Survey, Question, QuestionOption, SurveyState, QuestionAnswer, SurveyAnswer, MultipleAnswers

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['POST', 'GET'])
@login_required
def index():
    survey_form = SurveyForm()
    if survey_form.validate_on_submit():
        new_survey = Survey(title=survey_form.title.data, description=survey_form.description.data, state='new',
                            creator_id=current_user.id, id=str(uuid.uuid4()))
        db.session.add(new_survey)
        db.session.commit()
        db.session.refresh(new_survey)
        flash("Survey successfully created!!")
        return redirect(url_for('main.survey_view', id=new_survey.id))
    return render_template('main/index.html', form=survey_form, title="SurveyApp | Home")


@main_bp.route('/survey/<string:id>')
def survey_view(id):
    survey = Survey.query.get(id)
    if survey is None:
        raise NotFound()

    if not current_user.is_authenticated or survey.creator_id != current_user.id:
        if survey.state.value != 2:
            return render_template('errors/survey_unavailable.html')
        return render_template('main/survey_answer.html', survey=survey, title="SurveyApp | Answer")

    question_form = QuestionForm()
    question_option_form = QuestionOptionForm()

    return render_template('main/survey_view.html', survey=survey, form=question_form, option_form=question_option_form,
                           title="SurveyApp | Details")


@main_bp.route('/survey/<string:id>/delete')
@login_required
def delete_survey(id):
    survey = Survey.query.get(id)

    if survey.creator_id != current_user.id:
        raise Forbidden()

    db.session.delete(survey)
    db.session.commit()

    flash('Survey was deleted')
    return redirect(url_for('main.index'))


@main_bp.route('/survey/<string:survey_id>/change_state/<int:new_state>')
@login_required
def change_survey_state(survey_id, new_state):
    survey = Survey.query.get(survey_id)
    if survey.creator_id != current_user.id:
        raise Forbidden()

    survey.state = SurveyState(new_state)
    db.session.add(survey)
    db.session.commit()

    return redirect(url_for('main.survey_view', id=survey_id))


@main_bp.route('/survey/<string:id>/add_question', methods=['POST'])
@login_required
def add_survey_question(id):
    survey = Survey.query.get(id)
    if survey.creator_id != current_user.id:
        raise Forbidden()

    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(question_statement=form.question_text.data, type=form.type.data, survey_id=id)
        survey_questions = Survey.query.get(id).questions

        if survey_questions:
            last_question = survey_questions[-1]
            question.position = last_question.position + 1
        else:
            question.position = 1

        db.session.add(question)
        db.session.commit()

        flash('Your question was added successfully!!')
        return redirect(url_for('main.survey_view', id=id))
    else:
        flash("Form failed validate.")
        return redirect(url_for('main.survey_view', id=id))
    pass


@main_bp.route('/survey/<string:survey_id>/question/<int:question_id>/delete')
@login_required
def delete_question(survey_id, question_id):
    survey = Survey.query.get(survey_id)
    if survey.creator_id != current_user.id:
        raise Forbidden()

    db.session.delete(Question.query.get(question_id))
    db.session.commit()

    flash("Question deleted")
    return redirect(url_for('main.survey_view', id=survey_id))


@main_bp.route('/survey/<string:survey_id>/question/<int:question_id>/change_position/<int:new_position>')
@login_required
def change_question_position(survey_id, question_id, new_position):
    pass


@main_bp.route('/survey/<string:survey_id>/question/<int:question_id>/add_option', methods=['POST'])
@login_required
def add_question_option(survey_id, question_id):
    survey = Survey.query.get(survey_id)
    if survey.creator_id != current_user.id:
        raise Forbidden()
    form = QuestionOptionForm()
    if form.validate_on_submit():
        question = Question.query.get(question_id)
        option = QuestionOption(option_text=form.option_text.data, question_id=question_id)
        question_options = question.options
        if question_options:
            last_option = question_options[-1]
            option.position = last_option.position + 1
        else:
            option.position = 1
        db.session.add(option)
        db.session.commit()
        return redirect(url_for('main.survey_view', id=survey_id))
    else:
        flash("Form failed to validate!!")
        return redirect(url_for('main.survey_view', id=survey_id))


@main_bp.route("/survey/<string:survey_id>/results")
@login_required
def survey_results(survey_id):
    survey = Survey.query.get(survey_id)
    if survey.creator_id != current_user.id:
        raise Forbidden()
    return render_template('main/results.html', survey=Survey.query.get(survey_id), title="SurveyApp | Results")


@main_bp.route('/survey/<string:survey_id>/answer', methods=['POST'])
def survey_answer(survey_id):
    survey_ans = SurveyAnswer(survey_id=survey_id)
    db.session.add(survey_ans)
    db.session.flush()
    db.session.refresh(survey_ans)

    for key in request.form.keys():
        question = Question.query.get(int(key))
        if question.type.value == 1:
            for value in request.form.getlist(key):
                answer = QuestionAnswer(integer_answer=int(value), question_id=question.id,
                                        survey_answer_id=survey_ans.id)
                db.session.add(answer)
                db.session.commit()

        elif question.type.value == 2:
            for value in request.form.getlist(key):
                answer = QuestionAnswer(text_answer=value, question_id=question.id, survey_answer_id=survey_ans.id)
                db.session.add(answer)
                db.session.commit()

        elif question.type.value == 3:
            for value in request.form.getlist(key):
                answer = QuestionAnswer(single_option_answer=int(value), question_id=question.id,
                                        survey_answer_id=survey_ans.id)
                db.session.add(answer)
                db.session.commit()
        else:
            answer = QuestionAnswer(survey_answer_id=survey_ans.id, question_id=question.id)
            db.session.add(answer)
            db.session.flush()

            db.session.refresh(answer)
            for value in request.form.getlist(key):
                ans = MultipleAnswers(answer_id=answer.id, option_id=int(value))
                db.session.add(ans)
            db.session.commit()

    flash("Your answers were submitted successfully!")
    return redirect(url_for('main.survey_view', id=survey_id))
