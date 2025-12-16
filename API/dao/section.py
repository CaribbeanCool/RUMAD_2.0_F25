from API.config.pgconfig import pg_config
import psycopg2


class SectionDAO:
    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s port=%d host=%s" % (
            pg_config["dbname"],
            pg_config["user"],
            pg_config["password"],
            pg_config["port"],
            pg_config["host"],
        )
        self.conn = psycopg2.connect(connection_url)

    def getAllSections(self):
        cursor = self.conn.cursor()
        query = """
        SELECT sid, roomid, cid, mid, semester, years, capacity
        FROM section;
        """
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getSectionByID(self, sid):
        cursor = self.conn.cursor()
        query = """
        SELECT sid, roomid, cid, mid, semester, years, capacity
        FROM section
        WHERE sid = %s;
        """
        cursor.execute(query, (sid,))
        result = cursor.fetchone()
        self.conn.commit()
        return result

    def insertSection(self, roomid, cid, mid, semester, years, capacity):
        cursor = self.conn.cursor()
        query = """
        INSERT INTO section (roomid, cid, mid, semester, years, capacity) 
        VALUES (%s, %s, %s, %s, %s, %s) 
        RETURNING sid;
        """
        cursor.execute(query, (roomid, cid, mid, semester, years, capacity))
        sid = cursor.fetchone()[0]
        self.conn.commit()
        return sid

    def updateSection(self, sid, roomid, cid, mid, semester, years, capacity):
        cursor = self.conn.cursor()
        query = """
        UPDATE section SET roomid = %s, cid = %s, mid = %s, semester = %s, years = %s, capacity = %s
        WHERE sid = %s;
        """
        cursor.execute(query, (roomid, cid, mid, semester, years, capacity, sid))
        self.conn.commit()
        return sid

    def deleteSection(self, sid):
        cursor = self.conn.cursor()

        # Check if section exists
        check_query = "SELECT sid FROM section WHERE sid = %s;"
        cursor.execute(check_query, (sid,))
        section = cursor.fetchone()

        if section is None:
            return -1  # Section not found

        # If it exists, delete it
        delete_query = "DELETE FROM section WHERE sid = %s;"
        cursor.execute(delete_query, (sid,))
        self.conn.commit()
        return sid  # Return deleted sid

    def roomExists(self, roomid):
        cursor = self.conn.cursor()
        query = """
        SELECT rid
        FROM room
        WHERE rid = %s;
        """
        cursor.execute(query, (roomid,))
        result = cursor.fetchone()
        self.conn.commit()
        return result

    def classExists(self, cid):
        cursor = self.conn.cursor()
        query = """
        SELECT cid
        FROM class
        WHERE cid = %s;
        """
        cursor.execute(query, (cid,))
        result = cursor.fetchone()
        self.conn.commit()
        return result

    def meetingExists(self, mid):
        cursor = self.conn.cursor()
        query = """
        SELECT mid
        FROM meeting
        WHERE mid = %s;
        """
        cursor.execute(query, (mid,))
        result = cursor.fetchone()
        self.conn.commit()
        return result
    
    def getRoomCapacity(self, roomid):
        cursor = self.conn.cursor()
        query = """
        SELECT capacity
        FROM room
        WHERE rid = %s;
        """
        cursor.execute(query, (roomid,))
        result = cursor.fetchone()
        self.conn.commit()
        return result
    
    def hasScheduleConflict(self, roomid, mid, sid=None):
        cursor = self.conn.cursor()
        query = """
        SELECT s.sid
        FROM section AS s
        INNER JOIN meeting AS m_existing ON s.mid = m_existing.mid
        INNER JOIN meeting AS m_new ON m_new.mid = %s
        WHERE s.roomid = %s
        AND (%s IS NULL OR s.sid <> %s)
        AND m_existing.cdays = m_new.cdays
        AND m_existing.starttime < m_new.endtime
        AND m_existing.endtime > m_new.starttime;
        """
        cursor.execute(query, (mid, roomid, sid, sid))
        result = cursor.fetchone()
        self.conn.commit()
        return result  # returns conflicting sid or None
