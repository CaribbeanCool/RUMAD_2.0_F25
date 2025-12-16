from flask import Flask, jsonify, redirect, request, Blueprint
from flask_cors import CORS

# ==== Handlers ====
from API.handlers.classes import ClassHandler
from API.handlers.meeting import MeetingHandler
from API.handlers.section import SectionHandler
from API.handlers.room import RoomHandler
from API.handlers.requisite import RequisiteHandler
from API.handlers.stats import StatsHandler
from API.handlers.user import UserHandler
from API.handlers.chatbot import ChatbotHandler
from API.handlers.syllabus import SyllabusHandler

app = Flask(__name__)
CORS(app)

# URL Prefix for the API Blueprint
api = Blueprint("api", __name__, url_prefix="/lacy/api")


@app.get("/")
def reroute():
    return redirect("/lacy/api/")


@api.get("/")
def index():
    return jsonify({"message": "Welcome to the LACY RUMAD 2.0 Backend System API"})


# ======= Class Routes =======
chandler = ClassHandler()


@api.route("/classes", methods=["GET", "POST"])
def handle_classes():
    if request.method == "GET":
        return chandler.getAllClasses()
    elif request.method == "POST":
        c = request.get_json()
        return chandler.insertClass(c)


@api.get("/classes/<int:cid>")
def handle_class_by_id(cid):
    return chandler.getClassByID(cid)


@api.put("/classes/<int:cid>")
def handle_class_update(cid):
    c = request.get_json()
    return chandler.updateClass(cid, c)


@api.delete("/classes/<int:cid>")
def handle_class_delete(cid):
    return chandler.deleteClass(cid)


# ======= Meeting Routes =======
mhandler = MeetingHandler()


@api.route("/meeting", methods=["GET", "POST"])
def handle_meetings():
    if request.method == "GET":
        return mhandler.getAllMeetings()
    elif request.method == "POST":
        meeting = request.get_json()
        return mhandler.insertMeeting(meeting)


@api.get("/meeting/<int:mid>")
def handle_meeting_by_id(mid):
    return mhandler.getMeetingByID(mid)


@api.put("/meeting/<int:mid>")
def handle_meeting_update(mid):
    meeting = request.get_json()
    return mhandler.updateMeeting(mid, meeting)


@api.delete("/meeting/<int:mid>")
def handle_meeting_delete(mid):
    return mhandler.deleteMeeting(mid)


# ======= Section Routes =======
shandler = SectionHandler()


@api.route("/section", methods=["GET", "POST"])
def handle_section():
    if request.method == "GET":
        return shandler.getAllSections()
    elif request.method == "POST":
        s = request.get_json()
        return shandler.insertSection(s)


@api.get("/section/<int:sid>")
def handle_section_by_id(sid):
    return shandler.getSectionByID(sid)


@api.put("/section/<int:sid>")
def handle_section_update(sid):
    s = request.get_json()
    return shandler.updateSection(sid, s)


@api.delete("/section/<int:sid>")
def handle_section_delete(sid):
    return shandler.deleteSection(sid)


# ======= Room Routes =======
rhandler = RoomHandler()


@api.route("/room", methods=["GET", "POST"])
def handle_rooms():
    if request.method == "GET":
        return rhandler.getAllRooms()
    elif request.method == "POST":
        room = request.get_json()
        return rhandler.insertRoom(room)


@api.get("/room/<int:rid>")
def handle_room_by_id(rid):
    return rhandler.getRoomByID(rid)


@api.put("/room/<int:rid>")
def handle_room_update(rid):
    room = request.get_json()
    return rhandler.updateRoom(rid, room)


@api.delete("/room/<int:rid>")
def handle_room_delete(rid):
    return rhandler.deleteRoom(rid)


# ======= Requisite Routes =======
requisitehandler = RequisiteHandler()


@api.get("/requisite")
def handle_all_requisites():
    return requisitehandler.getAllRequisites()


@api.route("/requisite", methods=["POST"])
def handle_requisite():
    data = request.get_json()
    return requisitehandler.insertRequisite(data)


@api.get("/requisite/<int:classid>/<int:reqid>")
def handle_get_requisite(classid, reqid):
    return requisitehandler.getRequisite(classid, reqid)


@api.delete("/requisite/<int:classid>/<int:reqid>")
def handle_delete_requisite(classid, reqid):
    return requisitehandler.deleteRequisite(classid, reqid)


# ======= User Routes =======
uhandler = UserHandler()


@api.route("/user", methods=["GET", "POST"])
def handle_users():
    if request.method == "GET":
        return uhandler.getAllUsers()
    elif request.method == "POST":
        user = request.get_json()
        return uhandler.insertUser(user)


@api.get("/user/<int:uid>")
def handle_user_by_id(uid):
    return uhandler.getUserByID(uid)


@api.get("/user/<string:username>")
def handle_user_by_username(username):
    return uhandler.getUserByUsername(username)


@api.put("/user/<int:uid>")
def handle_user_update(uid):
    user = request.get_json()
    return uhandler.updateUser(uid, user)


@api.delete("/user/<int:uid>")
def handle_user_delete(uid):
    return uhandler.deleteUser(uid)


@api.post("/user/login")
def handle_login():
    user_data = request.get_json()
    return uhandler.login(user_data)


# ======= Stats Routes =======
standler = StatsHandler()


@api.get("/stats/sections-by-day")
def stats_sections_by_day():
    return standler.getSectionsByDay()


@api.get("/stats/top-departments-by-sections")
def stats_top_departments():
    return standler.getTopDepartments()


@api.get("/stats/top-rooms-by-utilization")
def handle_top_rooms_by_utilization():
    return standler.getTopRoomsByUtilization()


@api.get("/stats/multi-room-classes")
def handle_multi_room_classes():
    return standler.getMultiRoomClasses()


@api.get("/stats/top-classes-by-avg-duration")
def handle_longest_avg_meetings():
    return standler.getLongestAverageMeetingDuration()


@api.get("/stats/classes-without-prereqs")
def handle_classes_without_prerequisites():
    return standler.getClassesWithoutPrerequisites()


# ======= Syllabus Routes =======
syllabushandler = SyllabusHandler()


@api.route("/syllabus/course/<int:cid>", methods=["GET"])
def handle_syllabus_by_course(cid):
    return syllabushandler.getChunksByCourseID(cid)


@api.route("/syllabus", methods=["POST"])
def handle_insert_syllabus():
    data = request.get_json()
    return syllabushandler.insertChunk(data)


@api.route("/syllabus/search", methods=["POST"])
def handle_search_similar():
    data = request.get_json()
    return syllabushandler.searchSimilar(data)


@api.route("/syllabus/course/<int:cid>/search", methods=["POST"])
def handle_search_similar_by_course(cid):
    data = request.get_json()
    return syllabushandler.searchSimilarByCourse(cid, data)


@api.route("/syllabus/course/<int:cid>", methods=["DELETE"])
def handle_delete_syllabus_by_course(cid):
    return syllabushandler.deleteChunksByCourseID(cid)


# ======= Chatbot Routes =======

chatbothandler = ChatbotHandler()


@api.route("/chatbot", methods=["POST"])
def handle_chatbot():
    data = request.get_json()
    return chatbothandler.getChatbotReply(data)


# --end--------------------------------------------
app.register_blueprint(api)

if __name__ == "__main__":
    app.run(debug=True)
