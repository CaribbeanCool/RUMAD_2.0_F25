from flask import jsonify
from API.dao.meeting import MeetingDAO
from datetime import datetime


class MeetingHandler:
    def mapMeeting(self, meeting) -> dict:
        result = {}
        result["mid"] = meeting[0]
        result["ccode"] = meeting[1]
        result["starttime"] = meeting[2]
        result["endtime"] = meeting[3]
        result["cdays"] = meeting[4]
        return result

    def validate_meeting_time(self, cdays, starttime, endtime):
        if cdays == "MJ":
            # Convert times to minutes from midnight for easier comp
            start_minutes = starttime.hour * 60 + starttime.minute
            end_minutes = endtime.hour * 60 + endtime.minute

            # Valid time slots for MJ in minutes from midnight
            morning_start, morning_end = 7 * 60 + 30, 10 * 60 + 15  # 7:30, 10:15
            afternoon_start, afternoon_end = 12 * 60 + 30, 19 * 60 + 45  # 12:30, 19:45

            # Check if the meeting is within one of the valid slots
            in_morning = morning_start <= start_minutes and end_minutes <= morning_end
            in_afternoon = (
                afternoon_start <= start_minutes and end_minutes <= afternoon_end
            )

            if not (in_morning or in_afternoon):
                return (
                    jsonify(
                        "BAD REQUEST: MJ meetings must be within 7:30-10:15 or 12:30-19:45 (7:45pm)."
                    ),
                    400,
                )
        return None, None

    def getAllMeetings(self):
        dao = MeetingDAO()
        meetings = dao.getAllMeetings()
        result = []
        for meeting in meetings:
            result.append(self.mapMeeting(meeting))
        return jsonify(result), 200

    def getMeetingByID(self, mid):
        dao = MeetingDAO()
        meeting = dao.getMeetingByID(mid)
        if not meeting:
            return jsonify("NOT FOUND"), 404
        else:
            return jsonify(self.mapMeeting(meeting))

    def parse_time(self, time_str: str) -> datetime:
        """
        Parses a time string in "HH:MM" format and combines it with a
        default date (1900-01-01).
        """
        time_obj = datetime.strptime(time_str, "%H:%M").time()
        return datetime.combine(datetime(1900, 1, 1), time_obj)

    def insertMeeting(self, meeting):
        if (
            "ccode" not in meeting
            or "starttime" not in meeting
            or "endtime" not in meeting
            or "cdays" not in meeting
        ):
            return jsonify("BAD REQUEST: MISSING VALUES"), 400

        ccode = meeting["ccode"]
        starttime_str = meeting["starttime"]
        endtime_str = meeting["endtime"]
        cdays = meeting["cdays"]

        if cdays not in ["MJ", "LWV"]:
            return jsonify("BAD REQUEST: Invalid cdays value."), 400

        try:
            starttime = self.parse_time(starttime_str)
            endtime = self.parse_time(endtime_str)
        except ValueError:
            return jsonify("BAD REQUEST: Time must be in HH:MM format."), 400

        if starttime >= endtime:
            return jsonify("BAD REQUEST: Start time must be before end time."), 400

        error, status_code = self.validate_meeting_time(cdays, starttime, endtime)
        if error:
            return error, status_code

        dao = MeetingDAO()
        if dao.getMeetingByCcode(str(ccode)):
            return jsonify(
                f"BAD REQUEST: Meeting with ccode {ccode} already exists."
            ), 400

        mid = dao.insertMeeting(ccode, starttime, endtime, cdays)
        row = (mid, ccode, starttime, endtime, cdays)
        if mid is None:
            return jsonify("INTERNAL SERVER ERROR"), 500
        return jsonify(self.mapMeeting(row)), 201

    def updateMeeting(self, mid, meeting):
        dao = MeetingDAO()
        if not dao.getMeetingByID(mid):
            return jsonify("NOT FOUND"), 404

        if (
            "ccode" not in meeting
            or "starttime" not in meeting
            or "endtime" not in meeting
            or "cdays" not in meeting
        ):
            return jsonify("BAD REQUEST: MISSING VALUES"), 400

        ccode = meeting["ccode"]
        starttime_str = meeting["starttime"]
        endtime_str = meeting["endtime"]
        cdays = meeting["cdays"]

        if cdays not in ["MJ", "LWV"]:
            return jsonify("BAD REQUEST: Invalid cdays value."), 400

        try:
            starttime = self.parse_time(starttime_str)
            endtime = self.parse_time(endtime_str)
        except ValueError:
            return jsonify("BAD REQUEST: Time must be in HH:MM format."), 400

        if starttime >= endtime:
            return jsonify("BAD REQUEST: Start time must be before end time."), 400

        error, status_code = self.validate_meeting_time(cdays, starttime, endtime)
        if error:
            return error, status_code

        existing_meeting = dao.getMeetingByCcode(str(ccode))
        if existing_meeting and existing_meeting[0] != mid:
            return (
                jsonify(f"BAD REQUEST: Meeting with ccode {ccode} already exists."),
                400,
            )

        updated_mid = dao.updateMeeting(mid, ccode, starttime, endtime, cdays)
        row = (mid, ccode, starttime, endtime, cdays)
        if updated_mid is None:
            return jsonify("INTERNAL SERVER ERROR"), 500
        return jsonify(self.mapMeeting(row)), 200

    def deleteMeeting(self, mid):
        dao = MeetingDAO()
        deleted_mid = dao.deleteMeeting(mid)
        if deleted_mid is None:
            return jsonify("INTERNAL SERVER ERROR"), 500
        elif deleted_mid == -1:
            return jsonify("NOT FOUND"), 404
        elif deleted_mid == -2:
            return jsonify("CONFLICT: MEETING IS REFERENCED BY A SECTION"), 409
        return jsonify(deleted_mid), 204
