from pymongo import MongoClient
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
MONGODB_URI="mongodb+srv://yourUsername:yourPassword@yourClusterName.n9z04.mongodb.net/sample_mflix?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URI)
db=client.Attendance_Bot
user=db.DemoUsers

#insert username if chatid not present else update username
def update_username(chatid,username):
    user.update_one({
        "chatid":chatid
    },{
        "$set":{
            "username":username
        }
    },upsert=True)

#insert password in users collection after matching chatid and insert if chatid is not present
def update_password(chatid,password):
    user.update_one({
        "chatid":chatid
    },{
        "$set":{
            "password":password
        }
    },upsert=True)

#get username and password from chatid
def get_details(chatid):
    student=user.find_one({
        "chatid":chatid
    })
    if student:
        if "username" in student.keys() and "password" in student.keys():
            details=[student['username'],student['password']]
        elif "password" in student.keys():
            details=[None,student['password']]
        else:
            details=[student['username'],None]
        return details
    else:
        return None,None

#updat attendace for a particular user
def update_attendance(chatid,attendance):
    user.update_one({
        "chatid":chatid
    },{
        "$set":{
            "attendance":attendance
        }
    },upsert=True)

#get attendance for a particular user
def get_attendance(chatid):
    student=user.find_one({
        "chatid":chatid
    })
    if student and 'attendance' in student.keys():
        return student['attendance']
    else:
        return None