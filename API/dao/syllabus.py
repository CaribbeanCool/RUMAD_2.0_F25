from API.config.pgconfig import pg_config
import psycopg2

class SyllabusDAO:
    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s port=%d host=%s" % (
            pg_config["dbname"],
            pg_config["user"],
            pg_config["password"],
            pg_config["port"],
            pg_config["host"],
        )
        self.conn = psycopg2.connect(connection_url)
    
    def insertChunk(self,courseid,chunk,embedding):
        cursor=self.conn.cursor()
        query="""
        INSERT INTO syllabus(courseid,chunk,embedding_text )
        VALUES(%s,%s,%s)
        RETURNING chunkid;
        """
        cursor.execute(query,(courseid,chunk,embedding))
        chunkid=cursor.fetchone()[0]
        self.conn.commit()
        return chunkid
    def getChunkByID(self,chunkid):
        cursor=self.conn.cursor()
        query="""
        SELECT chunkid,courseid,chunk,embedding_text 
        FROM syllabus
        WHERE chunkid=%s;
        """
        cursor.execute(query,(chunkid,))
        result=cursor.fetchone()
        return result

    def getChunksByCourseID(self,courseid):
        cursor=self.conn.cursor()
        query="""
        SELECT chunkid,courseid,chunk,embedding_text 
        FROM syllabus
        WHERE courseid=%s;
        """
        cursor.execute(query,(courseid,))
        result=cursor.fetchall()
        return result
    
    def getFragments(self,embedding,limit=5):
        cursor=self.conn.cursor()
        embedding_str="["+",".join(map(str,embedding))+"]"
        query=f"""
        SELECT chunkid,courseid,chunk,embedding_text
        FROM syllabus
        ORDER BY embedding_text <-> %s::vector
        LIMIT %s;
        """
        cursor.execute(query,(embedding_str,limit))
        return cursor.fetchall()
    def getFragmentsByCourseAndEmbedding(self,courseid,embedding,limit=5):
        cursor=self.conn.cursor()
        embedding_str="["+",".join(map(str,embedding))+"]"
        query=f"""
        SELECT chunkid,courseid,chunk,embedding_text
        FROM syllabus
        WHERE courseid=%s
        ORDER BY embedding_text <-> %s::vector
        LIMIT %s;
        """
        cursor.execute(query,(courseid,embedding_str,limit))
        return cursor.fetchall()
    
    def deleteChunksByCourseID(self,courseid):
        cursor=self.conn.cursor()
        try:
            query="""
            DELETE FROM syllabus
            WHERE courseid=%s;
            """
            cursor.execute(query,(courseid,))
            if cursor.rowcount==0:
                self.conn.rollback()
                return -1
            self.conn.commit()
            return courseid
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cursor.close()