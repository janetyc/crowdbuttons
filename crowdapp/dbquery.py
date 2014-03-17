import bson
from datetime import datetime

from crowdapp.models import Device, Question, Answer
from crowdapp import db

class DBQuery(object):
    
    #device
    def add_device(self, input):
        device = Device()
        device.name = input['name']
        device.button_num = input['button_num']
        device.question_id = input['question_id']
        device.location = input['location']
        device.created_user = input['created_user']
        device.created_time = datetime.utcnow()
        device_id = db.device.insert(device)

        return str(device_id)

    def get_device_by_id(self, device_id):
        device = db.Device.get_from_id(bson.ObjectId(device_id))
        return device

    def get_last_devices(self, count=10):
        query = db.Device.find().sort("created_time", -1).limit(count)
        result = [q for q in query]

        if len(result):
            return result
        else:
            return []

    #question
    def add_question(self, input):
        question = Question()
        question.content = input['content']
        question.answer_list = input['answer_list']
        question.device_list = input['device_list']
        question.created_user = input['created_user']
        question.created_time = datetime.utcnow()
        question_id = db.question.insert(question)

        return str(question_id)

    def get_question_by_id(self, question_id):
        question = db.Question.get_from_id(bson.ObjectId(question_id))
        return question

    def get_last_questions(self, count=10):
        query = db.Question.find().sort("created_time", -1).limit(count)
        result = [q for q in query]

        if len(result):
            return result
        else:
            return []

    #answer
    def add_answer(self, input):
        answer = Answer()
        answer.question_id = input['question_id']
        answer.device_id = input['device_id']
        answer.content = input['content']
        answer.created_user = input['created_user']
        answer.created_time = datetime.utcnow()
        answer_id = db.answer.insert(answer)

        return str(answer_id)

    def get_answer_by_id(self, answer_id):
        answer = db.Answer.get_from_id(bson.ObjectId(answer_id))
        return answer

    def get_last_answers(self, count=10):
        query = db.Answer.find().sort("created_time", -1).limit(count)
        result = [q for q in query]

        if len(result):
            return result
        else:
            return []
        