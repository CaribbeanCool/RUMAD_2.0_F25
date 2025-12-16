from flask import jsonify
from API.dao.section import SectionDAO

class SectionHandler:
    def mapSection(self, s) -> dict:
        result = {}
        result["sid"] = s[0]
        result["roomid"] = s[1]
        result["cid"] = s[2]
        result["mid"] = s[3]
        result["semester"] = s[4]
        result["years"] = s[5]
        result["capacity"] = s[6]
        return result

    def getAllSections(self):
        dao = SectionDAO()
        sections = dao.getAllSections()
        result = []
        for s in sections:
            result.append(self.mapSection(s))
        return jsonify(result), 200

    def getSectionByID(self, sid):
        dao = SectionDAO()
        section = dao.getSectionByID(sid)
        if not section:
            return jsonify("NOT FOUND"), 404
        else:
            return jsonify(self.mapSection(section)), 200

    def insertSection(self, s):
        if (
            "roomid" not in s
            or "cid" not in s
            or "mid" not in s
            or "semester" not in s
            or "years" not in s
            or "capacity" not in s
        ):
            return jsonify("BAD REQUEST: MISSING VALUES"), 400
        
        roomid = s["roomid"]
        cid = s["cid"]
        mid = s["mid"]
        semester = s["semester"]
        years = s["years"]
        capacity = s["capacity"]

        dao = SectionDAO()

        # --- Validations ---
        # 1. FK existence
        if dao.classExists(cid) is None:
            return jsonify("cid does not exist"), 404
        if dao.meetingExists(mid) is None:
            return jsonify("mid does not exist"), 404
        if dao.roomExists(roomid) is None:
            return jsonify("roomid does not exist"), 404

        # 2. Capacity
        room_capacity = dao.getRoomCapacity(roomid)
        if capacity < 0 or capacity > room_capacity[0]:
            return jsonify("Section capacity is invalid or exceeds room capacity"), 400

        # 3. Term & Year
        valid_semesters = {"Fall", "Spring", "V1", "V2"}
        if semester not in valid_semesters:
            return jsonify("Invalid semester"), 400
        if not (isinstance(years, str) and len(years) == 4 and years.isdigit()):
            return jsonify("Invalid year format (YYYY expected)"), 400

        # 4. Scheduling conflict
        conflict = dao.hasScheduleConflict(roomid, mid)
        if conflict:
            conflicting_sid = conflict[0]
            return jsonify(f"Scheduling conflict with section {conflicting_sid}"), 409

        # --- Insert ---
        sid = dao.insertSection(roomid, cid, mid, semester, years, capacity)
        if sid is None:
            return jsonify("Internal server error"), 500
        elif sid == -1:
            return jsonify("Bad request"), 400
        
        new_section = dao.getSectionByID(sid)
        return jsonify(self.mapSection(new_section)), 201

    def updateSection(self, sid, s):
        if (
            "roomid" not in s
            or "cid" not in s
            or "mid" not in s
            or "semester" not in s
            or "years" not in s
            or "capacity" not in s
        ):
            return jsonify("BAD REQUEST"), 400
        roomid = s["roomid"]
        cid = s["cid"]
        mid = s["mid"]
        semester = s["semester"]
        years = s["years"]
        capacity = s["capacity"]
        dao = SectionDAO()

        # --- Validations ---

        # --- 0. Check if section exists ---
        existing_section = dao.getSectionByID(sid)
        if existing_section is None:
            return jsonify("Section not found"), 404
    
        # 1. FK existence
        if dao.classExists(cid) is None:
            return jsonify("cid does not exist"), 404
        if dao.meetingExists(mid) is None:
            return jsonify("mid does not exist"), 404
        if dao.roomExists(roomid) is None:
            return jsonify("roomid does not exist"), 404

        # 2. Capacity
        room_capacity = dao.getRoomCapacity(roomid)
        if capacity < 0 or capacity > room_capacity[0]:
            return jsonify("Section capacity is invalid or exceeds room capacity"), 400

        # 3. Term & Year
        valid_semesters = {"Fall", "Spring", "V1", "V2"}
        if semester not in valid_semesters:
            return jsonify("Invalid semester"), 400
        if not (isinstance(years, str) and len(years) == 4 and years.isdigit()):
            return jsonify("Invalid year format (YYYY expected)"), 400

        # 4. Scheduling conflict
        conflict = dao.hasScheduleConflict(roomid, mid, sid)
        if conflict:
            conflicting_sid = conflict[0]
            return jsonify(f"Scheduling conflict with section {conflicting_sid}"), 409
        
        # --- Update ---
        updated_sid = dao.updateSection(sid, roomid, cid, mid, semester, years, capacity)
        if updated_sid is None:
            return jsonify("INTERNAL SERVER ERROR"), 500
        elif updated_sid == -1:
            return jsonify("NOT FOUND"), 404
        
        updated_section = dao.getSectionByID(sid)
        return jsonify(self.mapSection(updated_section)), 200

    def deleteSection(self, sid):
        dao = SectionDAO()
        deleted_sid = dao.deleteSection(sid)

        if deleted_sid == -1:
            return jsonify("Section not found"), 404
        return jsonify(f"Section {deleted_sid} deleted successfully"), 204

