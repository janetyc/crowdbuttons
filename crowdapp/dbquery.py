import bson
from datetime import datetime, timedelta

from crowdapp.models import Device, Question, Answer, Comment
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
        if self.isValidObjectId(device_id):
            device = db.Device.get_from_id(bson.ObjectId(device_id))
            return device
        else:
            return None

    def get_devices_by_location(self, location, count=10):
        query_str = {
            "location": location
        }
        query = db.Device.find(query_str, network_timeout=1).sort("created_time", -1).limit(count)
        result = [q for q in query]

        if len(result):
            return result
        else:
            return []

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
        answer.location = input['location']
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

    def get_answers_by_last_hr(self, *args, **kwargs):
        question_id = kwargs.get("question_id")
        device_id = kwargs.get("device_id")
        location = kwargs.get("location")
        now = datetime.utcnow()
        last_hr = now - timedelta(hours=1)
        
        return self.get_answers_by_range(last_hr, now, device_id=device_id, 
                                         question_id=question_id, location=location)

    def get_answers_by_range(self, oldtime, newtime, *args, **kwargs):
        question_id = kwargs.get("question_id")
        device_id = kwargs.get("device_id")
        location = kwargs.get("location")

        if type(question_id) == str:
            question_id = bson.ObjectId(question_id)

        query_str = {
            "created_time":{
                '$gte': oldtime,
                '$lt': newtime
            }
        }
        if device_id:
            query_str["device_id"] = device_id

        elif location:
            devices = self.get_devices_by_location(location)

            query_str["$or"] = [{ "location": location }]
            for d in devices:
                query_str["$or"].append({"device_id": str(d._id)})

        if question_id:
            query_str["question_id"] = question_id

        query = db.Answer.find(query_str, network_timeout=1)
        result = [q for q in query]

        if len(result):
            return result
        else:
            return []

    def get_answer_count_by_device_id(self, device_id, *args, **kwargs):
        query_str = {
            "device_id": device_id
        }
        count = db.Answer.find(query_str, network_timeout=1).count()
        return count
        
    def get_answer_count_by_question_id(self, question_id, *args, **kwargs):
        if type(question_id) == str:
            question_id = bson.ObjectId(question_id)

        device_id = kwargs.get("device_id")
        if device_id:
            query_str = {
                "question_id": question_id,
                "device_id": str(device_id)
            }
        else:
            query_str = {
                "question_id": question_id
            }

        count = db.Answer.find(query_str, network_timeout=1).count()
        return count

    def get_answers_by_question_id(self, question_id, count, *args, **kwargs):
        if type(question_id) == str:
            question_id = bson.ObjectId(question_id)

        device_id = kwargs.get("device_id")
        if device_id:
            query_str = {
                "question_id": question_id,
                "device_id": str(device_id)
            }
        else:
            query_str = {
                "question_id": question_id
            }
        
        query = db.Answer.find(query_str).sort("created_time", -1).limit(count)
        result = [q for q in query]
        
        return result

    def add_comment(self, input):
        comment = Comment()
        comment.question_id = input['question_id']
        comment.device_id = input['device_id']
        comment.content = input['content']
        comment.created_user = input['created_user']
        comment.location = input['location']
        comment.created_time = datetime.utcnow()
        comment_id = db.comment.insert(comment)

        return str(comment_id)

    def get_last_comments(self, count=10):
        query = db.Comment.find().sort("created_time", -1).limit(count)
        result = [q for q in query]

        if len(result):
            return result
        else:
            return []

    def get_comments_by_last_hr(self, *args, **kwargs):
        now = datetime.utcnow()
        last_hr = now - timedelta(hours=1)

        return self.get_comments_by_range(last_hr, now)

    def get_comments_by_range(self, oldtime, newtime, *args, **kwargs):
        query_str = {
            "created_time":{
                '$gte': oldtime,
                '$lt': newtime
            }
        }
    
        query = db.Comment.find(query_str, network_timeout=1)
        result = [q for q in query]

        if len(result):
            return result
        else:
            return []

    def isValidObjectId(self, obj_id):
        try:
            id = bson.ObjectId(obj_id)
            return True
        except bson.errors.InvalidId:
            return False
        
