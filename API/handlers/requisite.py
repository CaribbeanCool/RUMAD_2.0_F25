from flask import jsonify, request
from API.dao.requisite import RequisiteDAO

class RequisiteHandler:
    def mapRequisite(self, requisite) -> dict:
        result = {}
        result["classid"] = requisite[0]
        result["reqid"] = requisite[1]
        result["prereq"] = requisite[2]
        return result
    
    def getAllRequisites(self):
        dao = RequisiteDAO()
        requisites = dao.getAllRequisites()
        result = []
        for rows in requisites:
            result.append(self.mapRequisite(rows))
        return jsonify(result), 200


       

    
    def getRequisite(self, classid, reqid):
        dao = RequisiteDAO()
        requisite = dao.getRequisite(classid, reqid)

        if not requisite:
            return jsonify("NOT FOUND"), 404
        
        return jsonify(self.mapRequisite(requisite)), 200
    
    def insertRequisite(self, data):
        # Check required fields
        if (
            "classid" not in data
            or "reqid" not in data
            or "prereq" not in data
        ):
            return jsonify("BAD REQUEST: MISSING VALUES"), 400

        classid = data["classid"]
        reqid = data["reqid"]
        prereq = data["prereq"]

        dao = RequisiteDAO()

        # FK existence: classid must exist
        if dao.classExists(classid) is None:
            return jsonify("NOT FOUND: classid does not exist"), 404

        # FK existence: reqid must exist
        if dao.classExists(reqid) is None:
            return jsonify("NOT FOUND: reqid does not exist"), 404

        # Rule: no self-requisite
        if classid == reqid:
            return jsonify("CONFLICT: class cannot be its own prerequisite"), 409

        # Rule: no duplicate pair
        if dao.pairExists(classid, reqid) is not None:
            return jsonify("CONFLICT: requisite already exists"), 409

        # Rule: no simple 2-cycle
        if dao.twoCycleExist(classid, reqid) is not None:
            return jsonify("CONFLICT: simple cycle detected"), 409

        # Insert
        inserted = dao.insertRequisite(classid, reqid, prereq)

        if inserted is None:
            return jsonify("INTERNAL SERVER ERROR"), 500

        return jsonify(self.mapRequisite(inserted)), 201
    

    def deleteRequisite(self, classid, reqid):
        dao = RequisiteDAO()

        # FK validation
        if dao.classExists(classid) is None:
            return jsonify("NOT FOUND: classid does not exist"), 404
        
        if dao.classExists(reqid) is None:
            return jsonify("NOT FOUND: reqid does not exist"), 404

        # Pair existence validation
        if dao.pairExists(classid, reqid) is None:
            return jsonify("NOT FOUND: requisite does not exist"), 404

        # Delete
        deleted = dao.deleteRequisite(classid, reqid)

        if deleted is None:
            return jsonify("INTERNAL SERVER ERROR"), 500

        # Successful delete → no content
        return "", 204


    