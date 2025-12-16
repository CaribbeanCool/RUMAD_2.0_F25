from flask import jsonify
from API.dao.classes import ClassDAO


class ClassHandler:
    def mapClass(self, c) -> dict:
        result = {}
        result["cid"] = c[0]
        result["cname"] = c[1]
        result["ccode"] = c[2]
        result["cdesc"] = c[3]
        result["term"] = c[4]
        result["years"] = c[5]
        result["cred"] = c[6]
        result["csyllabus"] = c[7]
        return result

    def is_valid_term(self, term):
        valid_single_terms = {"First Semester", "Second Semester"}
        if term == "According to Demand":
            return True

        parts = {p.strip() for p in term.split(",")}
        return parts.issubset(valid_single_terms) and len(parts) > 0

    def getAllClasses(self):
        dao = ClassDAO()
        classes = dao.getAllClasses()
        result = []
        for c in classes:
            result.append(self.mapClass(c))
        return jsonify(result), 200

    def getClassByID(self, cid):
        dao = ClassDAO()
        cclass = dao.getClassByID(cid)
        if not cclass:
            return jsonify("NOT FOUND"), 404
        else:
            return jsonify(self.mapClass(cclass))

    def insertClass(self, c):
        if (
            "cname" not in c
            or "ccode" not in c
            or "cdesc" not in c
            or "term" not in c
            or "years" not in c
            or "cred" not in c
            or "csyllabus" not in c
        ):
            return jsonify("BAD REQUEST: MISSING VALUES"), 400
        cname = c["cname"]
        ccode = c["ccode"]
        cdesc = c["cdesc"]
        term = c["term"]
        years = c["years"]
        cred = c["cred"]
        csyllabus = c["csyllabus"]
        # cname and ccode must be non-empty
        if (
            not isinstance(cname, str)
            or cname.strip() == ""
            or not isinstance(ccode, str)
            or ccode.strip() == ""
        ):
            return jsonify(
                "BAD REQUEST: cname and ccode must be non-empty strings."
            ), 400

        # Check concatenation unique
        dao = ClassDAO()
        if dao.getClassByNameAndCode(cname, ccode):
            return (
                jsonify(
                    f"BAD REQUEST: Class with name+code {cname + ccode} already exists."
                ),
                400,
            )
        if len(cname) != 4:
            return jsonify("BAD REQUEST: Class name must be 4 characters long."), 400
        if not ccode.isdigit() or len(ccode) != 4:
            return (
                jsonify("BAD REQUEST: Class code must be a 4-digits."),
                400,
            )
        if not self.is_valid_term(term):
            return jsonify("BAD REQUEST: Invalid term value."), 400
        if not isinstance(cred, int) or cred < 0:
            return (
                jsonify("BAD REQUEST: Credits must be a non-negative integer."),
                400,
            )
        if years not in ["Every Year", "According to Demand", "Odd Years"]:
            return jsonify("BAD REQUEST: Invalid years value."), 400
        cid = dao.insertClass(cname, ccode, cdesc, term, years, cred, csyllabus)
        row = (cid, cname, ccode, cdesc, term, years, cred, csyllabus)
        if cid is None:
            return jsonify("INTERNAL SERVER ERROR"), 500
        elif cid == -1:
            return jsonify("BAD REQUEST"), 404
        elif cid == -2:
            return (
                jsonify(
                    f"BAD REQUEST: Class with name + code {cname + ccode} already exists."
                ),
                400,
            )
        return jsonify(self.mapClass(row)), 201

    def updateClass(self, cid, c):
        dao = ClassDAO()
        old_class_data = dao.getClassByID(cid)
        if not old_class_data:
            return jsonify("NOT FOUND"), 404

        # Create a dictionary from the old data for easier access
        prev_class_data = self.mapClass(old_class_data)

        cname = c.get("cname", prev_class_data["cname"])
        ccode = c.get("ccode", prev_class_data["ccode"])
        cdesc = c.get("cdesc", prev_class_data["cdesc"])
        term = c.get("term", prev_class_data["term"])
        years = c.get("years", prev_class_data["years"])
        cred = c.get("cred", prev_class_data["cred"])
        csyllabus = c.get("csyllabus", prev_class_data["csyllabus"])

        # Validate only the fields that are present in the request
        if "cname" in c and len(cname) != 4:
            return jsonify("BAD REQUEST: Class name must be 4 characters long."), 400
        if "ccode" in c and (not ccode.isdigit() or len(ccode) != 4):
            return jsonify("BAD REQUEST: Class code must be a 4-digit string."), 400
        if "term" in c and not self.is_valid_term(term):
            return jsonify("BAD REQUEST: Invalid term value."), 400
        if "cred" in c and (not isinstance(cred, int) or cred < 0):
            return (
                jsonify("BAD REQUEST: Credits must be a non-negative integer."),
                400,
            )
        if "years" in c and years not in [
            "Every Year",
            "According to Demand",
            "Odd Years",
        ]:
            return jsonify("BAD REQUEST: Invalid years value."), 400

        # If cname or ccode were provided (or effectively changed), ensure they are non-empty
        if ("cname" in c and (not isinstance(cname, str) or cname.strip() == "")) or (
            "ccode" in c and (not isinstance(ccode, str) or ccode.strip() == "")
        ):
            return jsonify(
                "BAD REQUEST: cname and ccode must be non-empty strings."
            ), 400

        # Ensure concatenation of cname+ccode is unique across classes (exclude current cid)
        existing = dao.getClassByNameAndCode(cname, ccode)
        if existing and existing[0] != cid:
            return (
                jsonify(
                    f"BAD REQUEST: Class with name+code {cname + ccode} already exists."
                ),
                400,
            )

        updated_cid = dao.updateClass(
            cid, cname, ccode, cdesc, term, years, cred, csyllabus
        )
        row = (cid, cname, ccode, cdesc, term, years, cred, csyllabus)
        if updated_cid is None:
            return jsonify("INTERNAL SERVER ERROR"), 500
        elif updated_cid == -1:
            return jsonify("NOT FOUND"), 404
        elif updated_cid == -2:
            return (
                jsonify(
                    f"BAD REQUEST: Class with name+code {cname + ccode} already exists."
                ),
                400,
            )
        return jsonify(self.mapClass(row)), 200

    def deleteClass(self, cid):
        dao = ClassDAO()
        deleted_cid = dao.deleteClass(cid)
        if deleted_cid is None:
            return jsonify("INTERNAL SERVER ERROR"), 500
        elif deleted_cid == -1:
            return jsonify("NOT FOUND"), 404
        elif deleted_cid == -2:
            return jsonify("CONFLICT: CLASS IS REFERENCED BY A SECTION/REQUISITE"), 409
        return jsonify(deleted_cid), 204
