from flask import Blueprint, Flask, Response, request, render_template, redirect, url_for, jsonify
from crowdapp import app, env
from crowdapp.dbquery import DBQuery
from datetime import datetime, timedelta
import random

#dbquery = DBQuery()
views = Blueprint('views', __name__, template_folder='templates')

#only for space monitoring application
#question_id = 53267e1908df4f000247d845
@views.route('/')
def index():
    if(env == "PRODUCTION" or env == "DEBUG"):
        return redirect(url_for('views.show_all_rooms'))
    else:
        return redirect(url_for('views.feeds'))

@views.route('/rooms')
def show_all_rooms():
    question_id = "53267e1908df4f000247d845"
    rooms = ["R310", "R324/R326", "R340"]
    data=[]
    for room in rooms:
        result = get_room_summary(question_id, location=room)
        if result:
            data.append(result)

    return render_template('location_status.html', data=data)

@views.route('/summary', methods=('GET','POST'))
def get_all_summary():
    device_id = request.args.get('device_id', u'')
    location = request.args.get('location', u'')

    questions = DBQuery().get_last_questions(5)
    data=[]
    for q in questions:
        data.append(get_summary_data(q._id, device_id=device_id, location=location))

    return render_template('summary.html', data=data)

@views.route('/summary/<ObjectId:question_id>', methods=('GET','POST'))
def get_summary(question_id):
    device_id = request.args.get('device_id', u'')
    location = request.args.get('location', u'')

    data = [get_summary_data(question_id, device_id=device_id, location=location)]
    return render_template('summary.html', data=data)

def get_summary_data(question_id, *args, **kwargs):
    device_id = kwargs.get("device_id","")
    location = kwargs.get("location","")
    mode = kwargs.get("mode","day")
    if mode == "hour":
        answers = DBQuery().get_answers_by_last_hr(question_id=question_id,
                                                   device_id=device_id, location=location)
    else:
        answers = DBQuery().get_answers_by_last_day(question_id=question_id,
                                                    device_id=device_id, location=location)

    question = DBQuery().get_question_by_id(question_id)

    list = []  
    for ans in answers:
        list.append(ans.content)

    if not question:
        return None

    datalist = []
    for i, ans in enumerate(question.answer_list):
        datalist.append({
                "answer": ans,
                "count": list.count(i)
        })
    
    data = {
        "question_id": question_id,
        "question": question.content,
        "data": datalist,
        "location": location
    }

    return data

def predict_room_status(question_id, location):
    last_hr_data = get_summary_data(question_id,location=location, mode="hour")
    status = get_highest_status(last_hr_data["data"])
    if not status:
        status = u'Empty'

    return status

def get_room_summary(question_id, location):
    result = get_summary_data(question_id, location=location, mode="day")
    if result:
        last_hr_data = get_summary_data(question_id,location=location, mode="hour")

        if last_hr_data:
            status = get_highest_status(last_hr_data["data"])
            if not status:
                status = u'Empty'

        result["status"] = status
    return result

@views.route('/feeds')
def feeds():
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
            created_user = device.name
            location = device.location
        else:
            created_user = ans.get("created_user", "anonymous")
            location = ans.get("location", "unknown")
            if location == "":
                location = "unknown"
            if created_user == "":
                created_user = "anonymous"

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
            "created_user": created_user,
            "location": location,
            "created_time": created_time
        }
        data_list.append(data)

    return render_template('feeds.html', data=data_list)

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
    comments = DBQuery().get_last_comments(5)
    data = {
        'devices': devices,
        'questions': questions,
        'answers': answers,
        'comments': comments
    }

    return render_template('dashboard.html', data=data)

@views.route('/question/<ObjectId:question_id>', methods=('GET','POST'))
def question(question_id):
    location = request.args.get('location', u'')
    question = DBQuery().get_question_by_id(question_id)
    ans_list = question.answer_list
    data = {
        'question': question,
        'ans_list_range': len(question.answer_list),
        'location': location
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

# --- API -----
@views.route('/get_guide/<ObjectId:question_id>', methods=('GET', 'POST'))
def get_guide(question_id):
    location = request.args.get('location', u'')
    #output = "http://%s/arduino/buttons/0,0,0,0" % (request.remote_addr)
    #data = {
    #    "remote_addr": request.remote_addr,
    #    "output": output
    #}
    guide_str = ",".join([str(random.randint(0, 1)) for i in range(4)])
    ans_str = str(random.randint(0,3))

    return "%s:%s" % (guide_str, ans_str)
    #return jsonify(success=1, data=data)

# get prediction result
@views.route('/get_status/<ObjectId:question_id>', methods=('GET', 'POST'))
def get_status(question_id):
    location = request.args.get('location', u'')
    if DBQuery().isValidObjectId(question_id):
        status = predict_room_status(str(question_id), location)
        data = {
            "question_id": str(question_id),
            "location": location,
            "status": status
        }
    else:
        data = {}
    return jsonify(success=1, data=data)

@views.route('/get_data/<ObjectId:question_id>', methods=('GET','POST'))
def get_data(question_id):
    count = int(request.args.get('count', 10))
    device_id = request.args.get('device_id', u'')
    if DBQuery().isValidObjectId(device_id):
        answers = DBQuery().get_answers_by_question_id(question_id, count, device_id=device_id)
    else:
        answers = DBQuery().get_answers_by_question_id(question_id, count)

    output=[]
    for ans in answers:
        ans.created_time = ans.created_time + timedelta(hours=+8)
        item = {
            "id": str(ans._id),
            "question_id": str(ans.question_id),
            "device_id": str(ans.device_id),
            "content": ans.content,
            "created_user": ans.created_user,
            "created_time": datetime.strftime(ans.created_time, "%Y-%m-%d %H:%M:%S") #local time
        }
        output.append(item)

    return jsonify(success=1, data=output)

@views.route('/get_data/last_hr/<ObjectId:question_id>')
def get_last_hr_data(question_id):
    device_id = request.args.get('device_id', u'')
    if DBQuery().isValidObjectId(device_id):
        answers = DBQuery().get_answers_by_last_hr(question_id=question_id,
                                                   device_id=device_id)
    else:
        answers = DBQuery().get_answers_by_last_hr(question_id=question_id)

    output=[]
    for ans in answers:
        ans.created_time = ans.created_time + timedelta(hours=+8)
        item = {
            "id": str(ans._id),
            "question_id": str(ans.question_id),
            "device_id": str(ans.device_id),
            "content": ans.content,
            "created_user": ans.created_user,
            "created_time": datetime.strftime(ans.created_time, "%Y-%m-%d %H:%M:%S")
        }
        output.append(item)

    return jsonify(success=1, data=output)


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

        if mode == "minutely":
            time_interval = "%Y%m%d%H%M"

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
        'created_user': request.args.get('created_user', u'test'),
        'location': request.args.get('location', u'')
    }

    question = DBQuery().get_question_by_id(question_id)
    if not question:
        return jsonify(success=0, data="", error="NOT SUCH QUESTION!!")

    if answer < 0 or answer >= len(question.answer_list):
        return jsonify(success=0, data="", error="INCORRECT ANSWER!")

    answer_id = DBQuery().add_answer(input)
    return jsonify(success=1, data=answer_id)
    

@views.route('/add_comment/<ObjectId:question_id>/<comment>', methods=('GET', 'POST'))
def add_comment(question_id, comment):
    input = {
        'question_id': question_id,
        'device_id': request.args.get('device_id', u''),
        'content': comment,
        'created_user': request.args.get('created_user', u'test'),
        'location': request.args.get('location', u'')
    }

    question = DBQuery().get_question_by_id(question_id)
    if not question:
        return jsonify(success=0, data="", error="NOT SUCH QUESTION!!")

    comment_id = DBQuery().add_comment(input)
    return jsonify(success=1, data=comment_id)

# -----------------------------
def get_highest_status(data):
    list = []
    for d in data:
        list.append((d["count"], d["answer"]))
        
    list.sort(reverse=True)

    if list[0][0] == 0:
        return None
    else:
        return list[0][1]
