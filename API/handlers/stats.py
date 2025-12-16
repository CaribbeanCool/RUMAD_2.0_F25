from flask import jsonify, request
from API.dao.stats import StatsDAO

class StatsHandler:

    def getSectionsByDay(self):
        semester = request.args.get("semester")
        years = request.args.get("year")

        dao = StatsDAO()
        rows = dao.getSectionsByDay(semester, years)

        # Initialize counters for all days in problem statement
        day_count = { d: 0 for d in ["L","M","W","J","V","S","D"] }

        for (cdays,) in rows:
            for d in cdays:   # each letter increments individually
                if d in day_count:
                    day_count[d] += 1

        result = [{"day": d, "sections": day_count[d]} for d in day_count]
        return jsonify(result), 200


    def getTopDepartments(self):
        semester = request.args.get("semester")
        years = request.args.get("year")
        limit = request.args.get("limit", 1)

        # Try to parse limit, default = 1
        try:
            limit = int(request.args.get("limit", 1))
        except ValueError:
            return jsonify("limit must be an integer"), 400

        # Validate limit range
        if limit < 1 or limit > 5:
            return jsonify("limit must be between 1 and 5"), 400

        dao = StatsDAO()
        rows = dao.getTopDepartments(semester, years, limit)

        result = [{"fullcode": dept, "sections": count} for dept, count in rows]
        return jsonify(result), 200
     
    def getTopRoomsByUtilization(self):
        year=request.args.get("year",type=int)
        semester = request.args.get("semester",type=str)
        limit=request.args.get("limit",type=int,default=5)

        if limit<1 or limit>10:
            return jsonify("BAD REQUEST: Limit must be between 1 and 10"),400
        valid_semesters={"Fall","Spring","V1","V2"}
        if semester and semester not in valid_semesters:
            return jsonify("BAD REQUEST: Invalid semester value"),400
        dao=StatsDAO()
        stats=dao.getTopRoomsByUtilization(year,semester,limit)

        result=[{
            "rid":stat[0],
            "building":stat[1],
            "room_number":stat[2],
            "utilization":float(stat[3]) if stat[3] is not None else 0.0
        } for stat in stats]
        return jsonify(result),200
    
    def getMultiRoomClasses(self):
        year=request.args.get("year",type=int)
        semester=request.args.get("semester",type=str)
        limit=request.args.get("limit",type=int,default=5)
        orderby=request.args.get("orderby",type=str,default="desc")

        if limit<1 or limit>10:
            return jsonify("BAD REQUEST: Limit must be between 1 and 10"),400
        valid_semesters={"Fall","Spring","V1","V2"}
        if semester and semester not in valid_semesters:
            return jsonify("BAD REQUEST: Invalid semester value"),400
        if orderby.lower() not in {"asc","desc"}:
            return jsonify("BAD REQUEST: orderby must be 'asc' or 'desc'"),400
        dao=StatsDAO()
        stats=dao.getMultiRoomClasses(year,semester,limit,orderby)

        result=[
            {"cid":stat[0],
            "fullcode":stat[1],
            "distinct_room_count":stat[2]} for stat in stats]

        return jsonify(result),200


    def getLongestAverageMeetingDuration(self):
        year = request.args.get("year", type=int)
        semester = request.args.get("semester", type=str)
        limit = request.args.get("limit", type=int, default=5)

        # Validate limit range
        if limit < 1 or limit > 10:
            return jsonify("BAD REQUEST: Limit must be between 1 and 10"), 400
        
        valid_semesters = {"Fall", "Spring", "V1", "V2"}
        if semester and semester not in valid_semesters:
            return jsonify("BAD REQUEST: Invalid semester value"), 400

        dao = StatsDAO()
        rows = dao.getLongestAverageMeetingDuration(year, semester, limit)

        result = [{
            "cid": row[0],
            "fullcode": row[1],
            "average_minutes": float(row[2]) if row[2] is not None else 0.0
        } for row in rows]

        return jsonify(result), 200
    

    def getClassesWithoutPrerequisites(self):
        dao = StatsDAO()
        rows = dao.getClassesWithoutPrereqs()
        result = [{"cid": row[0], "fullcode": row[1]} for row in rows]
        return jsonify(result), 200