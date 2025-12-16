from flask import jsonify
from API.dao.user import UserDAO

class UserHandler:
    def mapUser(self, u) -> dict:
        result = {}
        result["uid"] = u[0]
        result["username"] = u[1]
        result["password"] = u[2]
        return result

    def getAllUsers(self):
        dao = UserDAO()
        users = dao.getAllUsers()
        result = [self.mapUser(u) for u in users]
        return jsonify(result), 200

    def getUserByID(self, uid):
        dao = UserDAO()
        user = dao.getUserByID(uid)
        if not user:
            return jsonify("NOT FOUND"), 404
        return jsonify(self.mapUser(user)), 200
    
    def getUserByUsername(self, username):
        dao = UserDAO()
        user = dao.getUserByUsername(username)
        if not user:
            return jsonify("NOT FOUND"), 404
        return jsonify(self.mapUser(user)), 200

    def insertUser(self, body):
        if "username" not in body or "password" not in body:
            return jsonify("BAD REQUEST: Missing username or password"), 400

        username = body["username"]
        password = body["password"]

        dao = UserDAO()

        if dao.getUserByUsername(username) is not None:
            return jsonify("Username already exists"), 409

        uid = dao.insertUser(username, password)
        new_user = dao.getUserByID(uid)
        return jsonify(self.mapUser(new_user)), 201

    def updateUser(self, uid, body):
        if "username" not in body or "password" not in body:
            return jsonify("BAD REQUEST"), 400
        
        username = body["username"]
        password = body["password"]

        dao = UserDAO()

        existing = dao.getUserByID(uid)
        if not existing:
            return jsonify("NOT FOUND"), 404

        dao.updateUser(uid, username, password)
        updated = dao.getUserByID(uid)
        return jsonify(self.mapUser(updated)), 200

    def deleteUser(self, uid):
        dao = UserDAO()
        deleted = dao.deleteUser(uid)

        if deleted == -1:
            return jsonify("User not found"), 404

        return jsonify(f"User {deleted} deleted successfully"), 204
    
    def login(self, credentials):
        dao = UserDAO()

        username = credentials.get("username")
        password = credentials.get("password")

        result = dao.verifyUser(username, password)

        if result is None:
            return {"User not found"}, 404
        if result == -1:
            return {"Invalid password"}, 401

        return {"status": "Login successful", "uid": result}, 200