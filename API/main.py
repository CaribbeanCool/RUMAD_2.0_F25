from flask import Flask, jsonify, redirect, request, Blueprint
from flask_cors import CORS
from flasgger import Swagger

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

# Swagger Configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/lacy/api/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/lacy/api/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/lacy/api/docs",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "LACY RUMAD 2.0 API",
        "description": "API for LACY RUMAD 2.0 Backend System - Course Management and Analytics",
        "version": "2.0.0",
        "contact": {
            "name": "RUMAD 2.0 Team",
        },
    },
    "basePath": "/lacy/api",
    "schemes": ["http", "https"],
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# URL Prefix for the API Blueprint
api = Blueprint("api", __name__, url_prefix="/lacy/api")


@app.get("/")
def reroute():
    return redirect("/lacy/api/")


@api.get("/")
def index():
    return jsonify(
        {
            "message": "Welcome to the LACY RUMAD 2.0 Backend System API",
            "version": "2.0.0",
            "documentation": "/lacy/api/docs",
        }
    )


# ======= Class Routes =======
chandler = ClassHandler()


@api.get("/classes")
def get_all_classes():
    """
    Get All Classes
    ---
    tags:
      - Classes
    responses:
      200:
        description: List of all classes
        schema:
          type: array
          items:
            type: object
            properties:
              cid:
                type: integer
                description: Class ID
              cname:
                type: string
                description: Department code
              ccode:
                type: string
                description: Course code
              cdesc:
                type: string
                description: Course description
              term:
                type: string
                description: Semester term
              years:
                type: string
                description: Year frequency
              cred:
                type: integer
                description: Credits
              csyllabus:
                type: string
                description: Syllabus link
    """
    return chandler.getAllClasses()


@api.post("/classes")
def create_class():
    """
    Create New Class
    ---
    tags:
      - Classes
    parameters:
      - in: body
        name: body
        required: true
        description: Class object to create
        schema:
          type: object
          required:
            - cname
            - ccode
            - cdesc
            - term
            - years
            - cred
            - csyllabus
          properties:
            cname:
              type: string
              description: Department code (must be 4 characters)
              example: "ICOM"
            ccode:
              type: string
              description: Course code (must be 4 digits)
              example: "4035"
            cdesc:
              type: string
              description: Course description
              example: "Database Systems"
            term:
              type: string
              description: 'Valid values: "First Semester", "Second Semester", "First Semester, Second Semester", or "According to Demand"'
              example: "First Semester"
            years:
              type: string
              description: 'Valid values: "Every Year", "According to Demand", or "Odd Years"'
              example: "Every Year"
            cred:
              type: integer
              description: Number of credits (non-negative integer)
              example: 3
            csyllabus:
              type: string
              description: Syllabus URL or description
              example: "http://example.com/syllabus.pdf"
    responses:
      201:
        description: Class created successfully
        schema:
          type: object
          properties:
            cid:
              type: integer
            cname:
              type: string
            ccode:
              type: string
            cdesc:
              type: string
            term:
              type: string
            years:
              type: string
            cred:
              type: integer
            csyllabus:
              type: string
      400:
        description: Bad request (validation error)
      409:
        description: Class with same name+code already exists
    """
    c = request.get_json()
    return chandler.insertClass(c)


@api.get("/classes/<int:cid>")
def handle_class_by_id(cid):
    """
    Get Class by ID
    ---
    tags:
      - Classes
    parameters:
      - name: cid
        in: path
        type: integer
        required: true
        description: Class ID
    responses:
      200:
        description: Class details
        schema:
          type: object
          properties:
            cid:
              type: integer
            cname:
              type: string
            ccode:
              type: string
            cdesc:
              type: string
            term:
              type: string
            years:
              type: string
            cred:
              type: integer
            csyllabus:
              type: string
      404:
        description: Class not found
    """
    return chandler.getClassByID(cid)


@api.put("/classes/<int:cid>")
def handle_class_update(cid):
    """
    Update Class
    ---
    tags:
      - Classes
    parameters:
      - name: cid
        in: path
        type: integer
        required: true
        description: Class ID
      - in: body
        name: body
        required: true
        description: Updated class fields
        schema:
          type: object
          required:
            - cname
            - ccode
            - cdesc
            - term
            - years
            - cred
            - csyllabus
          properties:
            cname:
              type: string
              example: "ICOM"
            ccode:
              type: string
              example: "4035"
            cdesc:
              type: string
              example: "Advanced Database Systems"
            term:
              type: string
              example: "First Semester"
            years:
              type: string
              example: "Every Year"
            cred:
              type: integer
              example: 3
            csyllabus:
              type: string
              example: "http://example.com/syllabus.pdf"
    responses:
      200:
        description: Updated class
      404:
        description: Class not found
      400:
        description: Validation error
    """
    c = request.get_json()
    return chandler.updateClass(cid, c)


@api.delete("/classes/<int:cid>")
def handle_class_delete(cid):
    """
    Delete Class
    ---
    tags:
      - Classes
    parameters:
      - name: cid
        in: path
        type: integer
        required: true
        description: Class ID
    responses:
      200:
        description: Class deleted successfully
      404:
        description: Class not found
    """
    return chandler.deleteClass(cid)


# ======= Meeting Routes =======
mhandler = MeetingHandler()


@api.get("/meeting")
def get_all_meetings():
    """
    Get All Meetings
    ---
    tags:
      - Meetings
    responses:
      200:
        description: List of all meetings
        schema:
          type: array
          items:
            type: object
            properties:
              mid:
                type: integer
                description: Meeting ID
              ccode:
                type: string
                description: Course code
              starttime:
                type: string
                description: Start time
              endtime:
                type: string
                description: End time
              cdays:
                type: string
                description: Days (MJ or LWV)
    """
    return mhandler.getAllMeetings()


@api.post("/meeting")
def create_meeting():
    """
    Create New Meeting
    ---
    tags:
      - Meetings
    parameters:
      - in: body
        name: body
        required: true
        description: Meeting object to create
        schema:
          type: object
          required:
            - ccode
            - starttime
            - endtime
            - cdays
          properties:
            ccode:
              type: string
              description: Course code
              example: "ICOM4035"
            starttime:
              type: string
              description: 'Start time in HH:MM format. MJ meetings must be 7:30-10:15 or 12:30-19:45'
              example: "14:30"
            endtime:
              type: string
              description: End time in HH:MM format
              example: "15:45"
            cdays:
              type: string
              description: 'Valid values: "MJ" (Mon/Wed) or "LWV" (Tue/Thu)'
              example: "MJ"
    responses:
      201:
        description: Meeting created successfully
        schema:
          type: object
          properties:
            mid:
              type: integer
            ccode:
              type: string
            starttime:
              type: string
            endtime:
              type: string
            cdays:
              type: string
      400:
        description: Bad request (validation error, time conflicts, or invalid format)
      409:
        description: Meeting with same ccode already exists
    """
    meeting = request.get_json()
    return mhandler.insertMeeting(meeting)


@api.get("/meeting/<int:mid>")
def handle_meeting_by_id(mid):
    """
    Get Meeting by ID
    ---
    tags:
      - Meetings
    parameters:
      - name: mid
        in: path
        type: integer
        required: true
        description: Meeting ID
    responses:
      200:
        description: Meeting details
        schema:
          type: object
          properties:
            mid:
              type: integer
            ccode:
              type: string
            starttime:
              type: string
            endtime:
              type: string
            cdays:
              type: string
      404:
        description: Meeting not found
    """
    return mhandler.getMeetingByID(mid)


@api.put("/meeting/<int:mid>")
def handle_meeting_update(mid):
    """
    Update Meeting
    ---
    tags:
      - Meetings
    parameters:
      - name: mid
        in: path
        type: integer
        required: true
        description: Meeting ID
      - in: body
        name: body
        required: true
        description: Updated meeting object
        schema:
          type: object
          required:
            - ccode
            - starttime
            - endtime
            - cdays
          properties:
            ccode:
              type: string
              example: "ICOM4035"
            starttime:
              type: string
              example: "14:30"
            endtime:
              type: string
              example: "15:45"
            cdays:
              type: string
              example: "MJ"
    responses:
      200:
        description: Meeting updated successfully
      404:
        description: Meeting not found
      400:
        description: Validation error
    """
    meeting = request.get_json()
    return mhandler.updateMeeting(mid, meeting)


@api.delete("/meeting/<int:mid>")
def handle_meeting_delete(mid):
    """
    Delete Meeting
    ---
    tags:
      - Meetings
    parameters:
      - name: mid
        in: path
        type: integer
        required: true
        description: Meeting ID
    responses:
      200:
        description: Meeting deleted successfully
      404:
        description: Meeting not found
    """
    return mhandler.deleteMeeting(mid)


# ======= Section Routes =======
shandler = SectionHandler()


@api.get("/section")
def get_all_sections():
    """
    Get All Sections
    ---
    tags:
      - Sections
    responses:
      200:
        description: List of all sections
        schema:
          type: array
          items:
            type: object
            properties:
              sid:
                type: integer
                description: Section ID
              roomid:
                type: integer
                description: Room ID
              cid:
                type: integer
                description: Class ID
              mid:
                type: integer
                description: Meeting ID
              semester:
                type: string
                description: Semester (Fall, Spring, V1, V2)
              years:
                type: string
                description: Year (YYYY format)
              capacity:
                type: integer
                description: Section capacity
    """
    return shandler.getAllSections()


@api.post("/section")
def create_section():
    """
    Create New Section
    ---
    tags:
      - Sections
    parameters:
      - in: body
        name: body
        required: true
        description: Section object to create
        schema:
          type: object
          required:
            - roomid
            - cid
            - mid
            - semester
            - years
            - capacity
          properties:
            roomid:
              type: integer
              description: Room ID (must exist)
              example: 1
            cid:
              type: integer
              description: Class ID (must exist)
              example: 5
            mid:
              type: integer
              description: Meeting ID (must exist)
              example: 3
            semester:
              type: string
              description: 'Valid values: "Fall", "Spring", "V1", "V2"'
              example: "Fall"
            years:
              type: string
              description: Year in YYYY format
              example: "2025"
            capacity:
              type: integer
              description: Section capacity (must not exceed room capacity)
              example: 35
    responses:
      201:
        description: Section created successfully
        schema:
          type: object
          properties:
            sid:
              type: integer
            roomid:
              type: integer
            cid:
              type: integer
            mid:
              type: integer
            semester:
              type: string
            years:
              type: string
            capacity:
              type: integer
      400:
        description: Bad request (validation error or capacity exceeds room)
      404:
        description: Referenced class, meeting, or room does not exist
      409:
        description: Scheduling conflict with another section
    """
    s = request.get_json()
    return shandler.insertSection(s)


@api.get("/section/<int:sid>")
def handle_section_by_id(sid):
    """
    Get Section by ID
    ---
    tags:
      - Sections
    parameters:
      - name: sid
        in: path
        type: integer
        required: true
        description: Section ID
    responses:
      200:
        description: Section details
        schema:
          type: object
          properties:
            sid:
              type: integer
            roomid:
              type: integer
            cid:
              type: integer
            mid:
              type: integer
            semester:
              type: string
            years:
              type: string
            capacity:
              type: integer
      404:
        description: Section not found
    """
    return shandler.getSectionByID(sid)


@api.put("/section/<int:sid>")
def handle_section_update(sid):
    """
    Update Section
    ---
    tags:
      - Sections
    parameters:
      - name: sid
        in: path
        type: integer
        required: true
        description: Section ID
      - in: body
        name: body
        required: true
        description: Updated section object
        schema:
          type: object
          required:
            - roomid
            - cid
            - mid
            - semester
            - years
            - capacity
          properties:
            roomid:
              type: integer
              example: 1
            cid:
              type: integer
              example: 5
            mid:
              type: integer
              example: 3
            semester:
              type: string
              example: "Spring"
            years:
              type: string
              example: "2026"
            capacity:
              type: integer
              example: 40
    responses:
      200:
        description: Section updated successfully
      404:
        description: Section not found
      400:
        description: Validation error
      409:
        description: Scheduling conflict
    """
    s = request.get_json()
    return shandler.updateSection(sid, s)


@api.delete("/section/<int:sid>")
def handle_section_delete(sid):
    """
    Delete Section
    ---
    tags:
      - Sections
    parameters:
      - name: sid
        in: path
        type: integer
        required: true
        description: Section ID
    responses:
      200:
        description: Section deleted successfully
      404:
        description: Section not found
    """
    return shandler.deleteSection(sid)


# ======= Room Routes =======
rhandler = RoomHandler()


@api.get("/room")
def get_all_rooms():
    """
    Get All Rooms
    ---
    tags:
      - Rooms
    responses:
      200:
        description: List of all rooms
        schema:
          type: array
          items:
            type: object
            properties:
              rid:
                type: integer
                description: Room ID
              building:
                type: string
                description: Building name
              room_number:
                type: string
                description: Room number
              capacity:
                type: integer
                description: Room capacity
    """
    return rhandler.getAllRooms()


@api.post("/room")
def create_room():
    """
    Create New Room
    ---
    tags:
      - Rooms
    parameters:
      - in: body
        name: body
        required: true
        description: Room object to create
        schema:
          type: object
          required:
            - building
            - room_number
            - capacity
          properties:
            building:
              type: string
              description: Building name (non-empty string)
              example: "Stefani"
            room_number:
              type: string
              description: Room number (non-empty string)
              example: "S-113"
            capacity:
              type: integer
              description: Room capacity (non-negative integer)
              example: 40
    responses:
      201:
        description: Room created successfully
        schema:
          type: object
          properties:
            rid:
              type: integer
            building:
              type: string
            room_number:
              type: string
            capacity:
              type: integer
      400:
        description: Bad request (validation error)
      409:
        description: Room with same building and room_number already exists
    """
    room = request.get_json()
    return rhandler.insertRoom(room)


@api.get("/room/<int:rid>")
def handle_room_by_id(rid):
    """
    Get Room by ID
    ---
    tags:
      - Rooms
    parameters:
      - name: rid
        in: path
        type: integer
        required: true
        description: Room ID
    responses:
      200:
        description: Room details
        schema:
          type: object
          properties:
            rid:
              type: integer
            building:
              type: string
            room_number:
              type: string
            capacity:
              type: integer
      404:
        description: Room not found
    """
    return rhandler.getRoomByID(rid)


@api.put("/room/<int:rid>")
def handle_room_update(rid):
    """
    Update Room
    ---
    tags:
      - Rooms
    parameters:
      - name: rid
        in: path
        type: integer
        required: true
        description: Room ID
      - in: body
        name: body
        required: true
        description: Updated room object
        schema:
          type: object
          required:
            - building
            - room_number
            - capacity
          properties:
            building:
              type: string
              example: "Stefani"
            room_number:
              type: string
              example: "S-113"
            capacity:
              type: integer
              example: 45
    responses:
      200:
        description: Room updated successfully
      404:
        description: Room not found
      400:
        description: Validation error
      409:
        description: Another room with same building and room_number exists
    """
    room = request.get_json()
    return rhandler.updateRoom(rid, room)


@api.delete("/room/<int:rid>")
def handle_room_delete(rid):
    """
    Delete Room
    ---
    tags:
      - Rooms
    parameters:
      - name: rid
        in: path
        type: integer
        required: true
        description: Room ID
    responses:
      204:
        description: Room deleted successfully (no content)
      404:
        description: Room not found
      409:
        description: Cannot delete - room is referenced by a section
    """
    return rhandler.deleteRoom(rid)


# ======= Requisite Routes =======
requisitehandler = RequisiteHandler()


@api.get("/requisite")
def handle_all_requisites():
    """
    Get All Requisites
    ---
    tags:
      - Requisites
    responses:
      200:
        description: List of all prerequisite relationships
        schema:
          type: array
          items:
            type: object
            properties:
              classid:
                type: integer
                description: Class ID that has the prerequisite
              reqid:
                type: integer
                description: Prerequisite class ID
              prereq:
                type: string
                description: Type of prerequisite (e.g., "Pre", "Co")
    """
    return requisitehandler.getAllRequisites()


@api.post("/requisite")
def handle_requisite():
    """
    Create New Requisite
    ---
    tags:
      - Requisites
    parameters:
      - in: body
        name: body
        required: true
        description: Requisite relationship to create
        schema:
          type: object
          required:
            - classid
            - reqid
            - prereq
          properties:
            classid:
              type: integer
              description: Class ID that requires the prerequisite (must exist)
              example: 10
            reqid:
              type: integer
              description: Prerequisite class ID (must exist, cannot be same as classid)
              example: 5
            prereq:
              type: string
              description: Type of prerequisite
              example: "Pre"
    responses:
      201:
        description: Requisite created successfully
        schema:
          type: object
          properties:
            classid:
              type: integer
            reqid:
              type: integer
            prereq:
              type: string
      400:
        description: Missing required fields
      404:
        description: Class ID or prerequisite ID does not exist
      409:
        description: Conflict (self-requisite, duplicate, or cycle detected)
    """
    data = request.get_json()
    return requisitehandler.insertRequisite(data)


@api.get("/requisite/<int:classid>/<int:reqid>")
def handle_get_requisite(classid, reqid):
    """
    Get Specific Requisite
    ---
    tags:
      - Requisites
    parameters:
      - name: classid
        in: path
        type: integer
        required: true
        description: Class ID
      - name: reqid
        in: path
        type: integer
        required: true
        description: Prerequisite class ID
    responses:
      200:
        description: Requisite details
        schema:
          type: object
          properties:
            classid:
              type: integer
            reqid:
              type: integer
            prereq:
              type: string
      404:
        description: Requisite not found
    """
    return requisitehandler.getRequisite(classid, reqid)


@api.delete("/requisite/<int:classid>/<int:reqid>")
def handle_delete_requisite(classid, reqid):
    """
    Delete Requisite
    ---
    tags:
      - Requisites
    parameters:
      - name: classid
        in: path
        type: integer
        required: true
        description: Class ID
      - name: reqid
        in: path
        type: integer
        required: true
        description: Prerequisite class ID
    responses:
      204:
        description: Requisite deleted successfully (no content)
      404:
        description: Class ID, prerequisite ID, or requisite pair not found
    """
    return requisitehandler.deleteRequisite(classid, reqid)


# ======= User Routes =======
uhandler = UserHandler()


@api.get("/user")
def get_all_users():
    """
    Get All Users
    ---
    tags:
      - Users
    responses:
      200:
        description: List of all users
        schema:
          type: array
          items:
            type: object
            properties:
              uid:
                type: integer
                description: User ID
              username:
                type: string
                description: Username
              password:
                type: string
                description: Hashed password
    """
    return uhandler.getAllUsers()


@api.post("/user")
def create_user():
    """
    Create New User
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        description: User object to create
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: Unique username
              example: "jsmith"
            password:
              type: string
              description: User password (will be hashed)
              example: "securepassword123"
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            uid:
              type: integer
            username:
              type: string
            password:
              type: string
      400:
        description: Missing username or password
      409:
        description: Username already exists
    """
    user = request.get_json()
    return uhandler.insertUser(user)


@api.get("/user/<int:uid>")
def handle_user_by_id(uid):
    """
    Get User by ID
    ---
    tags:
      - Users
    parameters:
      - name: uid
        in: path
        type: integer
        required: true
        description: User ID
    responses:
      200:
        description: User details
        schema:
          type: object
          properties:
            uid:
              type: integer
            username:
              type: string
            password:
              type: string
      404:
        description: User not found
    """
    return uhandler.getUserByID(uid)


@api.get("/user/<string:username>")
def handle_user_by_username(username):
    """
    Get User by Username
    ---
    tags:
      - Users
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: Username
    responses:
      200:
        description: User details
        schema:
          type: object
          properties:
            uid:
              type: integer
            username:
              type: string
            password:
              type: string
      404:
        description: User not found
    """
    return uhandler.getUserByUsername(username)


@api.put("/user/<int:uid>")
def handle_user_update(uid):
    """
    Update User
    ---
    tags:
      - Users
    parameters:
      - name: uid
        in: path
        type: integer
        required: true
        description: User ID
      - in: body
        name: body
        required: true
        description: Updated user object
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "jsmith_updated"
            password:
              type: string
              example: "newpassword123"
    responses:
      200:
        description: User updated successfully
        schema:
          type: object
          properties:
            uid:
              type: integer
            username:
              type: string
            password:
              type: string
      404:
        description: User not found
      400:
        description: Missing required fields
    """
    user = request.get_json()
    return uhandler.updateUser(uid, user)


@api.delete("/user/<int:uid>")
def handle_user_delete(uid):
    """
    Delete User
    ---
    tags:
      - Users
    parameters:
      - name: uid
        in: path
        type: integer
        required: true
        description: User ID
    responses:
      204:
        description: User deleted successfully
      404:
        description: User not found
    """
    return uhandler.deleteUser(uid)


@api.post("/user/login")
def handle_login():
    """
    User Login
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        description: Login credentials
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    user_data = request.get_json()
    return uhandler.login(user_data)


# ======= Stats Routes =======
standler = StatsHandler()


@api.get("/stats/sections-by-day")
def stats_sections_by_day():
    """
    Get Sections by Day
    ---
    tags:
      - Statistics
    responses:
      200:
        description: Number of sections per day
    """
    return standler.getSectionsByDay()


@api.get("/stats/top-departments-by-sections")
def stats_top_departments():
    """
    Get Top Departments by Sections
    ---
    tags:
      - Statistics
    responses:
      200:
        description: Departments ranked by number of sections
    """
    return standler.getTopDepartments()


@api.get("/stats/top-rooms-by-utilization")
def handle_top_rooms_by_utilization():
    """
    Get Top Rooms by Utilization
    ---
    tags:
      - Statistics
    responses:
      200:
        description: Rooms ranked by utilization
    """
    return standler.getTopRoomsByUtilization()


@api.get("/stats/multi-room-classes")
def handle_multi_room_classes():
    """
    Get Classes Using Multiple Rooms
    ---
    tags:
      - Statistics
    responses:
      200:
        description: Classes that use multiple rooms
    """
    return standler.getMultiRoomClasses()


@api.get("/stats/top-classes-by-avg-duration")
def handle_longest_avg_meetings():
    """
    Get Classes by Average Meeting Duration
    ---
    tags:
      - Statistics
    responses:
      200:
        description: Classes ranked by average meeting duration
    """
    return standler.getLongestAverageMeetingDuration()


@api.get("/stats/classes-without-prereqs")
def handle_classes_without_prerequisites():
    """
    Get Classes Without Prerequisites
    ---
    tags:
      - Statistics
    responses:
      200:
        description: Classes that have no prerequisites
    """
    return standler.getClassesWithoutPrerequisites()


# ======= Syllabus Routes =======
syllabushandler = SyllabusHandler()


@api.get("/syllabus/course/<int:cid>")
def handle_syllabus_by_course(cid):
    """
    Get Syllabus Chunks by Course ID
    ---
    tags:
      - Syllabus
    parameters:
      - name: cid
        in: path
        type: integer
        required: true
        description: Course ID
    responses:
      200:
        description: List of syllabus chunks for the course
        schema:
          type: array
          items:
            type: object
            properties:
              chunkid:
                type: integer
                description: Chunk ID
              courseid:
                type: integer
                description: Course ID
              chunk:
                type: string
                description: Text chunk from syllabus
              embedding_text:
                type: string
                description: Vector embedding as string
      404:
        description: No chunks found for this course
    """
    return syllabushandler.getChunksByCourseID(cid)


@api.post("/syllabus")
def handle_insert_syllabus():
    """
    Insert Syllabus Chunk
    ---
    tags:
      - Syllabus
    parameters:
      - in: body
        name: body
        required: true
        description: Syllabus chunk to insert
        schema:
          type: object
          required:
            - courseid
            - chunk
            - embedding_text
          properties:
            courseid:
              type: integer
              description: Course ID (non-negative)
              example: 5
            chunk:
              type: string
              description: Text chunk from syllabus (non-empty)
              example: "This course covers database design and SQL."
            embedding_text:
              type: string
              description: Comma-separated list of floats for vector embedding
              example: "0.123,0.456,0.789"
    responses:
      201:
        description: Chunk inserted successfully
        schema:
          type: object
          properties:
            chunkid:
              type: integer
            courseid:
              type: integer
            chunk:
              type: string
            embedding_text:
              type: string
      400:
        description: Missing fields or validation error
    """
    data = request.get_json()
    return syllabushandler.insertChunk(data)


@api.post("/syllabus/search")
def handle_search_similar():
    """
    Search Similar Syllabus Content
    ---
    tags:
      - Syllabus
    parameters:
      - in: body
        name: body
        required: true
        description: Embedding vector to search
        schema:
          type: object
          required:
            - embedding_text
          properties:
            embedding_text:
              type: array
              description: List of floats representing the query embedding
              items:
                type: number
              example: [0.123, 0.456, 0.789]
            limit:
              type: integer
              description: Maximum number of results to return (default 5)
              example: 5
    responses:
      200:
        description: Similar syllabus chunks
        schema:
          type: object
          properties:
            count:
              type: integer
              description: Number of results
            results:
              type: array
              items:
                type: object
                properties:
                  chunkid:
                    type: integer
                  courseid:
                    type: integer
                  chunk:
                    type: string
                  embedding_text:
                    type: string
      400:
        description: Missing or invalid embedding_text
    """
    data = request.get_json()
    return syllabushandler.searchSimilar(data)


@api.post("/syllabus/course/<int:cid>/search")
def handle_search_similar_by_course(cid):
    """
    Search Similar Syllabus Content for Specific Course
    ---
    tags:
      - Syllabus
    parameters:
      - name: cid
        in: path
        type: integer
        required: true
        description: Course ID
      - in: body
        name: body
        required: true
        description: Embedding vector to search
        schema:
          type: object
          required:
            - embedding
          properties:
            embedding:
              type: array
              description: List of floats representing the query embedding
              items:
                type: number
              example: [0.123, 0.456, 0.789]
            limit:
              type: integer
              description: Maximum number of results (default 5)
              example: 5
    responses:
      200:
        description: Similar syllabus chunks for the course
        schema:
          type: object
          properties:
            count:
              type: integer
            results:
              type: array
              items:
                type: object
      400:
        description: Missing embedding field
    """
    data = request.get_json()
    return syllabushandler.searchSimilarByCourse(cid, data)


@api.delete("/syllabus/course/<int:cid>")
def handle_delete_syllabus_by_course(cid):
    """
    Delete All Syllabus Chunks for a Course
    ---
    tags:
      - Syllabus
    parameters:
      - name: cid
        in: path
        type: integer
        required: true
        description: Course ID
    responses:
      204:
        description: Chunks deleted successfully (no content)
      404:
        description: Course not found or no chunks to delete
    """
    return syllabushandler.deleteChunksByCourseID(cid)


# ======= Chatbot Routes =======

chatbothandler = ChatbotHandler()


@api.route("/chatbot", methods=["POST"])
def handle_chatbot():
    """
    Chatbot Query
    ---
    tags:
      - Chatbot
    parameters:
      - in: body
        name: body
        required: true
        description: User message
        schema:
          type: object
          properties:
            message:
              type: string
              example: "What classes are available in ICOM?"
    responses:
      200:
        description: Chatbot response
    """
    data = request.get_json()
    return chatbothandler.getChatbotReply(data)


# --end--------------------------------------------
app.register_blueprint(api)

if __name__ == "__main__":
    app.run(debug=True)
