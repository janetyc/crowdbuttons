from flask.ext.mongokit import MongoKit, Document
from datetime import datetime

from crowdapp import db, app

@db.register
class Device(Document):
    __database__ = app.config["DB_NAME"]
    __collection__ = "device"
    structure = {
        'name': unicode,
        'button_num': int,
        'question_id': unicode,
        'location': unicode,
        'created_time': datetime,
        'created_user': unicode
    }
    required_fields = ['name', 'button_num', 'created_time']
    default_values = {'created_time': datetime.utcnow()}
    use_dot_notation = True


@db.register
class Question(Document):
    __database__ = app.config["DB_NAME"]
    __collection__ = "question"
    structure = {
        'content': unicode,
        'answer_list': list,
        'device_list': list, #store device._id
        'created_time': datetime,
        'created_user': unicode
    }
    required_fields = ['content', 'answer_list', 'created_time']
    default_values = {'created_time': datetime.utcnow()}
    use_dot_notation = True
    
@db.register
class Answer(Document):
    __database__ = app.config["DB_NAME"]
    __collection__ = "answer"
    structure = {
        'question_id': unicode,
        'device_id': unicode,
        'content': unicode,
        'created_time': datetime,
        'created_user': unicode,
        'location': unicode
    }
    required_fields = ['question_id', 'content', 'created_time']
    default_values = {'created_time': datetime.utcnow()}
    use_dot_notation = True


@db.register
class Comment(Document):
    __database__ = app.config["DB_NAME"]
    __collection__ = "comment"
    structure = {
        'question_id': unicode,
        'device_id': unicode,
        'content': unicode,
        'created_time': datetime,
        'created_user': unicode,
        'location': unicode
    }
    required_fields = ['question_id', 'content', 'created_time']
    default_values = {'created_time': datetime.utcnow()}
    use_dot_notation = True


db.register([Device])
db.register([Question])
db.register([Answer])
db.register([Comment])
