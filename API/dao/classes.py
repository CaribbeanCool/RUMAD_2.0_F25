from API.config.pgconfig import pg_config
import psycopg2
from psycopg2 import IntegrityError


class ClassDAO:
    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s port=%d host=%s" % (
            pg_config["dbname"],
            pg_config["user"],
            pg_config["password"],
            pg_config["port"],
            pg_config["host"],
        )
        self.conn = psycopg2.connect(connection_url)

    def getAllClasses(self):
        cursor = self.conn.cursor()
        query = """
        SELECT cid, cname, ccode, cdesc, term, years, cred, csyllabus
        FROM class
        ORDER BY cid;
        """
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getClassByID(self, cid):
        cursor = self.conn.cursor()
        query = """
        SELECT cid, cname, ccode, cdesc, term, years, cred, csyllabus
        FROM class
        WHERE cid = %s;
        """
        cursor.execute(query, (cid,))
        result = cursor.fetchone()
        self.conn.commit()
        return result

    def getClassByNameAndCode(self, cname, ccode):
        cursor = self.conn.cursor()
        query = """
        SELECT cid, cname, ccode, cdesc, term, years, cred, csyllabus
        FROM class
        WHERE cname = %s AND ccode = %s;
        """
        cursor.execute(query, (cname, ccode))
        result = cursor.fetchone()
        self.conn.commit()
        return result

    def insertClass(self, name, code, desc, term, years, cred, syllabus):
        cursor = self.conn.cursor()
        query = """
        INSERT INTO class (cname, ccode, cdesc, term, years, cred, csyllabus) 
        VALUES (%s, %s, %s, %s, %s, %s, %s) 
        RETURNING cid;
        """
        try:
            cursor.execute(query, (name, code, desc, term, years, cred, syllabus))
            cid = cursor.fetchone()[0]
            self.conn.commit()
            return cid
        except IntegrityError as e:
            # Log diagnostics
            print("IntegrityError:", e)
            self.conn.rollback()
        except Exception as e:
            print("DB error:", e)
            self.conn.rollback()
            return None

    def updateClass(self, cid, name, code, desc, term, years, cred, syllabus):
        cursor = self.conn.cursor()
        query = """
        UPDATE class 
        SET cname = %s, ccode = %s, cdesc = %s, term = %s, years = %s, cred = %s, csyllabus = %s
        WHERE cid = %s;
        """
        try:
            cursor.execute(query, (name, code, desc, term, years, cred, syllabus, cid))
            if cursor.rowcount == 0:
                self.conn.rollback()
                return -1
            self.conn.commit()
            return cid
        except IntegrityError as e:
            # Log diagnostics
            print("IntegrityError:", e)
            self.conn.rollback()
        except Exception as e:
            print("DB error:", e)
            self.conn.rollback()
            return None

    def deleteClass(self, cid):
        cursor = self.conn.cursor()

        # Check for references in the section table
        query = """
        SELECT 1 
        FROM section 
        WHERE cid = %s 
        LIMIT 1;
        """
        cursor.execute(query, (cid,))
        if cursor.fetchone():
            return -2  # Conflict

        # Check for references in the requisite table
        query = """
        SELECT 1 
        FROM requisite 
        WHERE classid = %s 
        OR reqid = %s 
        LIMIT 1;
        """
        cursor.execute(query, (cid, cid))
        if cursor.fetchone():
            return -2  # Conflict

        # If no references, delete class
        query = """
        DELETE 
        FROM class 
        WHERE cid = %s;
        """
        cursor.execute(query, (cid,))
        if cursor.rowcount == 0:
            return -1  # Not found
        self.conn.commit()
        return cid
    def getCourseIDByCode(self,cname,ccode):
        cursor=self.conn.cursor()
        query="""
        SELECT cid
        FROM class
        WHERE cname=%s AND ccode=%s;
        """
        cursor.execute(query,(cname,ccode))
        result=cursor.fetchone()
        if result:
            return result[0]
        return None