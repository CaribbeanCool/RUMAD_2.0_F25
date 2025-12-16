from API.config.pgconfig import pg_config
import psycopg2

class StatsDAO:
    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s port=%d host=%s" % (
            pg_config["dbname"],
            pg_config["user"],
            pg_config["password"],
            pg_config["port"],
            pg_config["host"],
        )
        self.conn = psycopg2.connect(connection_url)

    def getSectionsByDay(self, semester, years):
        cursor = self.conn.cursor()
        query = """
        SELECT m.cdays
        FROM section s
        NATURAL JOIN meeting m
        WHERE (%s IS NULL OR s.semester = %s)
          AND (%s IS NULL OR s.years = %s);
        """
        cursor.execute(query, (semester, semester, years, years))
        rows = cursor.fetchall()
        return rows

    def getTopDepartments(self, semester, years, limit=1):
        cursor = self.conn.cursor()
        query = """
        SELECT SUBSTRING(c.cname FROM 1 FOR 4) AS dept, COUNT(*) AS count
        FROM section s
        JOIN class c ON s.cid = c.cid
        WHERE (%s IS NULL OR s.semester = %s)
          AND (%s IS NULL OR s.years = %s)
        GROUP BY dept
        ORDER BY count DESC
        LIMIT %s;
        """
        cursor.execute(query, (semester, semester, years, years, limit))
        rows = cursor.fetchall()
        return rows
    
    def getTopRoomsByUtilization(self,year=None,semester=None,limit=5):
        cursor=self.conn.cursor()
        query="""
        SELECT 
        r.rid, 
        r.building, 
        r.room_number,
        ROUND(AVG(CAST(s.capacity AS NUMERIC) / NULLIF(r.capacity, 0)), 2) AS utilization
        FROM 
        room r
        JOIN section s ON r.rid = s.roomid
        WHERE 1=1"""
        params=[]
        if year is not None:
            query+=" AND s.years=%s::text"
            params.append(year)
        if semester is not None:
            query+=" AND s.semester=%s"
            params.append(semester)
        query+="""
        GROUP BY r.rid,r.building,r.room_number
        HAVING COUNT(s.sid) > 0
        ORDER BY utilization DESC
        LIMIT %s;
        """
        params.append(limit)
        cursor.execute(query,tuple(params))
        result=cursor.fetchall()
        self.conn.commit()
        return result

    def getMultiRoomClasses(self, year=None, semester=None, limit=5,orderby="desc"):
        cursor = self.conn.cursor()
        query="""
        SELECT
        c.cid,
        c.cname||c.ccode as fullcode,
        COUNT( DISTINCT s.roomid) as distinct_room_count
        FROM
        class c
        JOIN section s ON c.cid = s.cid
        WHERE 1=1"""

        params=[]
        if year is not None:
            query+=" AND s.years=%s::text"
            params.append(year)
        if semester is not None:
            query+=" AND s.semester=%s"
            params.append(semester)
        query+="""
        GROUP BY c.cid,fullcode
        ORDER BY distinct_room_count{}
        LIMIT %s;
        """.format(" ASC " if orderby.lower()=="asc" else " DESC ")
        params.append(limit)

        cursor.execute(query,tuple(params))
        result=cursor.fetchall()
        self.conn.commit()
        return result
    

    def getLongestAverageMeetingDuration(self, year=None, semester=None, limit=5):
        cursor = self.conn.cursor()
        query = """
            SELECT
                c.cid,
                c.cname || c.ccode AS fullcode,
                AVG(EXTRACT(EPOCH FROM (m.endtime - m.starttime))/ 60) AS avg_minutes
                FROM class c
                JOIN section s ON c.cid = s.cid
                JOIN meeting m ON s.mid = m.mid
                WHERE 1=1
                """
        params = []

        if year is not None:
            query += "AND s.years = %s::text"
            params.append(year)

        if semester is not None:
            query += " AND s.semester = %s"
            params.append(semester)

        query += """
            GROUP BY c.cid, fullcode
            ORDER BY avg_minutes DESC
            LIMIT %s;
        """
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        self.conn.commit()
        return rows
    
    def getClassesWithoutPrereqs(self):
        cursor = self.conn.cursor()
        query = """
            SELECT
                c.cid,
                (c.cname || c.ccode) AS fullcode
            FROM class c
            WHERE NOT EXISTS (
                SELECT 1
                FROM requisite r
                WHERE r.classid = c.cid
                AND r.prereq = TRUE
            )
            ORDER BY fullcode;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        self.conn.commit()
        return rows
    