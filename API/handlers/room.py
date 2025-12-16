from flask import request,jsonify
from API.dao.room import RoomDAO

class RoomHandler:
    def mapRoom(self,room)->dict:
        result={}
        result["rid"]=room[0]
        result["building"]=room[1]
        result["room_number"]=room[2]
        result["capacity"]=room[3]
        return result
    def validate_room_payload(self,payload):
        required=["building","room_number","capacity"]
        for field in required:
            if field not in payload:
                return jsonify({"error":f"BAD REQUEST: Missing field {field}"}),400
        building=payload["building"]
        room_number=payload["room_number"]
        capacity=payload["capacity"]
        try:
            capacity_int=int(capacity)
            if capacity_int<0:
                return jsonify({"error":"BAD REQUEST: Capacity must be a non-negative integer"}),400
        except(ValueError,TypeError):
            return jsonify({"error":"BAD REQUEST: Capacity must be a non-negative integer"}),400
        
        if not isinstance(building,str) or building.strip()=="":
            return jsonify({"error":"BAD REQUEST: Building must be a non-empty string"}),400
        if not isinstance(room_number,str) or room_number.strip()=="":
            return jsonify({"error":"BAD REQUEST: Room number must be a non-empty string"}),400
        return None,{"building":building.strip(),"room_number":room_number.strip(),"capacity":capacity_int}

    def getAllRooms(self):
        dao=RoomDAO()
        rooms=dao.getAllRooms()
        result=[self.mapRoom(r) for r in rooms]
        return jsonify(result),200
    
    def getRoomByID(self,rid):
        dao=RoomDAO()
        room=dao.getRoomByID(rid)
        if not room:
            return jsonify({"error":"NOT FOUND"}),404
        return jsonify(self.mapRoom(room)),200
    
    def insertRoom(self,room_payload):
        error,parsed=self.validate_room_payload(room_payload)
        if error:
            return error,parsed
        building=parsed["building"]
        room_number=parsed["room_number"]
        capacity=parsed["capacity"]

        dao=RoomDAO()
        if dao.getRoomByBuildingNumber(building,room_number):
            return jsonify({"error":f"BAD REQUEST: Room {building} {room_number} already exists."}),409
        rid = dao.insertRoom(building,room_number,capacity)
        if rid is None:
            return jsonify({"error":"INTERNAL SERVER ERROR"}),500
        room=dao.getRoomByID(rid)
        return jsonify(self.mapRoom(room)),201
    def updateRoom(self,rid,room_payload):
        dao=RoomDAO()
        if not dao.getRoomByID(rid):
            return jsonify({"error":"NOT FOUND"}),404
        error,parsed=self.validate_room_payload(room_payload)
        if error:
            return error,parsed
        building=parsed["building"]
        room_number=parsed["room_number"]
        capacity=parsed["capacity"]

        existing_room=dao.getRoomByBuildingNumber(building,room_number)
        if existing_room and existing_room[0]!=rid:
            return jsonify({"error":f"BAD REQUEST: Room {building} {room_number} already exists."}),409
        updated_rid=dao.updateRoom(rid,building,room_number,capacity)
        if updated_rid is None:
            return jsonify({"error":"INTERNAL SERVER ERROR"}),500
        updated_room=dao.getRoomByID(rid)
        return jsonify(self.mapRoom(updated_room)),200

    
    def deleteRoom(self,rid):
        dao=RoomDAO()
        deleted=dao.deleteRoom(rid)
        if deleted is None:
            return jsonify({"error": "SERVER ERROR"}),500
        elif deleted==-1:
            return jsonify({"error": "NOT FOUND"}),404
        elif deleted==-2:
            return jsonify({"error": "delete room; room is referenced by a section"}),409
        return "",204
 