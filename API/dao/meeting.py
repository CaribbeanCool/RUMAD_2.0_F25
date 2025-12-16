from API.config.pgconfig import pg_config
import psycopg2


class MeetingDAO:
    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s port=%d host=%s" % (
            pg_config["dbname"],
            pg_config["user"],
            pg_config["password"],
            pg_config["port"],
            pg_config["host"],
        )
        self.conn = psycopg2.connect(connection_url)

    def getAllMeetings(self):
        cursor = self.conn.cursor()
        query = """
        SELECT mid, ccode, starttime, endtime, cdays
        FROM meeting
        ORDER BY mid;
        """
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getMeetingByID(self, mid):
        cursor = self.conn.cursor()
        query = """
        SELECT mid, ccode, starttime, endtime, cdays
        FROM meeting
        WHERE mid = %s;
        """
        cursor.execute(query, (mid,))
        result = cursor.fetchone()
        self.conn.commit()
        return result

    def getMeetingByCcode(self, ccode):
        cursor = self.conn.cursor()
        query = """
        SELECT mid, ccode, starttime, endtime, cdays
        FROM meeting
        WHERE ccode = %s;
        """
        cursor.execute(query, (ccode,))
        result = cursor.fetchone()
        self.conn.commit()
        return result

    def insertMeeting(self, ccode, starttime, endtime, cdays):
        cursor = self.conn.cursor()
        query = """
        INSERT INTO meeting (ccode, starttime, endtime, cdays) 
        VALUES (%s, %s, %s, %s) 
        RETURNING mid;
        """
        cursor.execute(query, (ccode, starttime, endtime, cdays))
        mid = cursor.fetchone()[0]
        self.conn.commit()
        return mid

    def updateMeeting(self, mid, ccode, starttime, endtime, cdays):
        cursor = self.conn.cursor()
        query = """
        UPDATE meeting 
        SET ccode = %s, starttime = %s, endtime = %s, cdays = %s
        WHERE mid = %s;
        """
        cursor.execute(query, (ccode, starttime, endtime, cdays, mid))
        self.conn.commit()
        return mid

    def deleteMeeting(self, mid):
        cursor = self.conn.cursor()
        # Check for conflicts in the section table first
        query = """
        SELECT 1 
        FROM section 
        WHERE mid = %s 
        LIMIT 1;
        """
        cursor.execute(query, (mid,))
        if cursor.fetchone():
            return -2  # Conflict

        # If no conflict, delete meeting
        query = """
        DELETE 
        FROM meeting 
        WHERE mid = %s;
        """
        cursor.execute(query, (mid,))
        # Check if a row was deleted
        if cursor.rowcount == 0:
            return -1  # Not found
        self.conn.commit()
        return mid
