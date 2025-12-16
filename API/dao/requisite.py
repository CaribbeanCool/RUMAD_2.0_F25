from API.config.pgconfig import pg_config
import psycopg2

class RequisiteDAO:
    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s port=%d host=%s" % (
            pg_config["dbname"],
            pg_config["user"],
            pg_config["password"],
            pg_config["port"],
            pg_config["host"]
        )
        self.conn = psycopg2.connect(connection_url)


# CRUD Operations for Requisites 


    def getAllRequisites(self):
        cursor = self.conn.cursor()
        query = """
            SELECT classid, reqid, prereq
            FROM requisite
            ORDER BY classid;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
        

    def getRequisite(self,classid,reqid):
        cursor = self.conn.cursor()
        query = """
            SELECT classid, reqid, prereq
            FROM requisite
            WHERE classid = %s AND reqid = %s;
        """
        cursor.execute(query, (classid, reqid))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def insertRequisite(self,classid,reqid,prereq):
        cursor = self.conn.cursor()
        query = """
            INSERT INTO requisite (classid, reqid, prereq)
            VALUES (%s, %s, %s)
            RETURNING classid, reqid, prereq;
        """
        cursor.execute(query, (classid, reqid, prereq))
        result = cursor.fetchone()
        self.conn.commit()
        return result 
    
    def deleteRequisite(self, classid, reqid):
        cursor = self.conn.cursor()
        query = """
            DELETE FROM requisite
            WHERE classid = %s AND reqid = %s 
            RETURNING classid;
        """
        cursor.execute(query, (classid, reqid))
        result = cursor.fetchone()
        self.conn.commit()
        return result
    
    #Validation

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
    
    def pairExists(self, classid, reqid):
        cursor = self.conn.cursor()
        query = """
            SELECT 1
            FROM requisite
            WHERE classid = %s AND reqid = %s; 
        """
        cursor.execute(query,(classid, reqid))
        result = cursor.fetchone()
        return result 
    
    def twoCycleExist(self,classid, reqid):
        cursor = self.conn.cursor()
        query = """
            SELECT 1
            FROM requisite
            WHERE classid = %s AND reqid = %s;
        """
        cursor.execute(query, (reqid, classid))
        result = cursor.fetchone()
        cursor.close()
        return result   