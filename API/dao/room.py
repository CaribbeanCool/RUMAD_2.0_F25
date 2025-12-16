from API.config.pgconfig import pg_config
import psycopg2

class RoomDAO:
    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s port=%d host=%s" % (
            pg_config["dbname"],
            pg_config["user"],
            pg_config["password"],
            pg_config["port"],
            pg_config["host"],
        )
        self.conn = psycopg2.connect(connection_url)
    def getAllRooms(self):
        cursor=self.conn.cursor()
        query="""
        SELECT rid,building,room_number,capacity
        FROM room
        ORDER BY rid;
        """
        cursor.execute(query)
        result=[row for row in cursor]
        return result
    def getRoomByID(self,rid):
        cursor=self.conn.cursor()
        query="""
        SELECT rid,building,room_number,capacity
        FROM room
        WHERE rid=%s;
        """
        cursor.execute(query,(rid,))
        result=cursor.fetchone()
        self.conn.commit()
        return result
    def getRoomByBuildingNumber(self,building,room_number):
        cursor=self.conn.cursor()
        query="""
        SELECT rid,building,room_number,capacity
        FROM room
        WHERE building=%s AND room_number=%s;
        """
        cursor.execute(query,(building,room_number))
        result=cursor.fetchone()
        self.conn.commit()
        return result
    def insertRoom(self,building,room_number,capacity):
        cursor=self.conn.cursor()
        query="""
        INSERT INTO room(building,room_number,capacity)
        VALUES(%s,%s,%s)
        RETURNING rid;
        """
        cursor.execute(query,(building,room_number,capacity))
        rid=cursor.fetchone()[0]
        self.conn.commit()
        return rid
    def updateRoom(self,rid,building,room_number,capacity):
        cursor=self.conn.cursor()
        query="""
        UPDATE room
        SET building=%s,room_number=%s,capacity=%s
        WHERE rid=%s
        """
        cursor.execute(query,(building,room_number,capacity,rid))
        self.conn.commit()
        return rid
    def deleteRoom(self,rid):
        cursor=self.conn.cursor()
        query="""
        SELECT 1
        FROM section
        WHERE roomid=%s
        LIMIT 1;
        """
        cursor.execute(query,(rid,))
        if cursor.fetchone():
            return -2
        query="""
        DELETE FROM room
        WHERE rid = %s;
        """
        cursor.execute(query,(rid,))
        if cursor.rowcount==0:
            return -1
        self.conn.commit()
        return rid
    