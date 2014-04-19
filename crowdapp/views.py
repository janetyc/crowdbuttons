from flask import Blueprint, Flask, Response, request, render_template, redirect, url_for, jsonify
from crowdapp import app
from crowdapp.dbquery import DBQuery
from datetime import datetime, timedelta

#dbquery = DBQuery()
views = Blueprint('views', __name__, template_folder='templates')


@views.route('/')
def index():
    answers = DBQuery().get_last_answers(10)
    data_list = []
    for ans in answers:
        answer_index = int(ans.content)
        question_id = ans.question_id
        #fetch question & device
        question = DBQuery().get_question_by_id(question_id)

        device_id = ans.get("device_id", None)
        if device_id and DBQuery().isValidObjectId(device_id):
            device = DBQuery().get_device_by_id(ans.device_id)            
            device_name = device.name
            device_location = device.location
        else:
            device_name = "anonymous"
            device_location = "unknown"

        if answer_index >= len(question.answer_list) or answer_index < 0:
            answer = "No answer!"
        else:
            answer = question.answer_list[answer_index]

        #Asia/Taipei 
        local_time = ans.created_time + timedelta(hours=+8)
        created_time  = datetime.strftime(local_time, "%Y-%m-%d %H:%M:%S")

        data = {
            "question": question.content,
            "answer": answer,
            "device_name": device_name,
            "location": device_location,
            "created_time": created_time
        }
        data_list.append(data)

    return render_template('index.html', data=data_list)

@views.route('/dashboard')
def dashboard():
    devices = DBQuery().get_last_devices(5)
    for d in devices:
        count = DBQuery().get_answer_count_by_device_id(str(d._id))
        d[u'total'] = count

    questions = DBQuery().get_last_questions(5)
    for q in questions:
        count = DBQuery().get_answer_count_by_question_id(q._id)
        q[u'total'] = count

    answers = DBQuery().get_last_answers(5)
    data = {
        'devices': devices,
        'questions': questions,
        'answers': answers
    }

    return render_template('dashboard.html', data=data)

@views.route('/question/<ObjectId:question_id>', methods=('GET','POST'))
def question(question_id):
    question = DBQuery().get_question_by_id(question_id)
    ans_list = question.answer_list
    data = {
        'question': question,
        'ans_list_range': len(question.answer_list)
    }

    return render_template('question.html', data=data)

@views.route('/get_vis/<ObjectId:question_id>/<int:count>',methods=('GET','POST'))
def get_vis(question_id, count):
    device_id = request.args.get('device_id', u'')
    mode = request.args.get('mode', u'hourly')

    data = {
        "question_id": question_id,
        "count": count,
        "device_id": device_id,
        "mode": mode
    }

    return render_template('visualization.html', data=data)

@views.route('/get_answers/<ObjectId:question_id>/<int:count>', methods=('GET','POST'))
def get_answers(question_id, count):
    device_id = request.args.get('device_id', u'')
    mode = request.args.get('mode',u'hourly')

    if DBQuery().isValidObjectId(device_id):
        answers = DBQuery().get_answers_by_question_id(question_id, count, device_id=device_id)
    else:
        answers = DBQuery().get_answers_by_question_id(question_id, count)
    map = {}

    #statistic
    for i, ans in enumerate(answers):
        #convert to local time
        ans.created_time = ans.created_time + timedelta(hours=+8)
        time_interval = "%Y%m%d%H"
        if mode == "daily":
            time_interval = "%Y%m%d"

        if mode == "weekly":
            time_interval = "%Y%m%U"
            
        if mode == "monthly":
            time_interval = "%Y%m"

        created_time  = datetime.strftime(ans.created_time, time_interval)
        ans.content= int(ans.content)
        if created_time in map:
            data = map[created_time]
            if ans.content in data:
                data[ans.content] = data[ans.content] + 1
            else:
                data[ans.content] = 1
        else:
            data = {}
            data[ans.content] = 1
        
        map[created_time] = data


    #data format
    output = []
    for time in map:
        curr = map[time]

        ans_list = []
        for ans_index in curr:
            ans = {
                "answer": ans_index,
                "count": curr[ans_index]
            }
            ans_list.append(ans)

        result = {
            "created_time": time,
            "answers": ans_list
        }
        output.append(result)

    return jsonify(success=1, data=output)

@views.route('/404')
def page_not_found():
    return render_template('404.html'), 404

@views.route('/400')
def bad_request():
    return render_template('400.html'), 400

# ----- add function -----
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
    

