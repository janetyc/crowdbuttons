from flask import Blueprint, Flask, Response, request, render_template, redirect, url_for, jsonify
from crowdapp import app
from crowdapp.dbquery import DBQuery

#dbquery = DBQuery()
views = Blueprint('views', __name__, template_folder='templates')

@views.route('/')
def index():
    devices = DBQuery().get_last_devices(5)
    questions = DBQuery().get_last_questions(5)
    answers = DBQuery().get_last_answers(5)
    data = {
        'devices': devices,
        'questions': questions,
        'answers': answers
    }

    return render_template('index.html', data=data)

@views.route('/404')
def page_not_found():
    return render_template('404.html'), 404

@views.route('/400')
def bad_request():
    return render_template('400.html'), 400

@views.route('/add_device', methods=('GET','POST'))
def add_device():
    input = {
        'name': request.args.get('name', u'test'),
        'button_num': int(request.args.get('button_num', u'0')),
        'question_id': request.args.get('question_id', u''),
        'location': request.args.get('location', u''),
        'created_user': request.args.get('created_user', u'test')
    }

    device_id = DBQuery().add_device(input)
    return jsonify(success=1, data=device_id)


@views.route('/add_question', methods=('GET','POST'))
def add_question():
    input = {
        'content': request.args.get('content', u'test question'),
        'answer_list': request.args.get('answer_list', u'ans1|ans2|ans3|ans4').split('|'),
        'device_list': request.args.get('device_list', u'').split('|'),
        'created_user': request.args.get('created_user', u'test')
    }

    question_id = DBQuery().add_question(input)
    return jsonify(success=1, data=question_id)

@views.route('/add_answer/<ObjectId:question_id>/<int:answer>', methods=('GET', 'POST'))
def add_answer(question_id, answer):
    input = {
        'question_id': question_id,
        'device_id': request.args.get('device_id', u''),
        'content': answer,
        'created_user': request.args.get('created_user', u'test')
    }

    question = DBQuery().get_question_by_id(question_id)
    if not question:
        return jsonify(success=0, data="", error="NOT SUCH QUESTION!!")

    if answer < 0 or answer >= len(question.answer_list):
        return jsonify(success=0, data="", error="INCORRECT ANSWER!")

    answer_id = DBQuery().add_answer(input)
    return jsonify(success=1, data=answer_id)
    

