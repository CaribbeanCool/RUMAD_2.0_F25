from API.config.pgconfig import pg_config
import psycopg2
import bcrypt

class UserDAO:
    def __init__(self):
        connection_url = "dbname=%s user=%s password=%s port=%d host=%s" % (
            pg_config["dbname"],
            pg_config["user"],
            pg_config["password"],
            pg_config["port"],
            pg_config["host"],
        )
        self.conn = psycopg2.connect(connection_url)

    def getAllUsers(self):
        cursor = self.conn.cursor()
        query = """
        SELECT uid, username, password
        FROM db_user;
        """
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getUserByID(self, uid):
        cursor = self.conn.cursor()
        query = """
        SELECT uid, username, password
        FROM db_user
        WHERE uid = %s;
        """
        cursor.execute(query, (uid,))
        result = cursor.fetchone()
        self.conn.commit()
        return result

    def getUserByUsername(self, username):
        cursor = self.conn.cursor()
        query = """
        SELECT uid, username, password
        FROM db_user
        WHERE username = %s;
        """
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        self.conn.commit()
        return result

    def insertUser(self, username, password):
        cursor = self.conn.cursor()

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        query = """
        INSERT INTO db_user (username, password)
        VALUES (%s, %s)
        RETURNING uid;
        """
        cursor.execute(query, (username, hashed.decode('utf-8')))
        uid = cursor.fetchone()[0]
        self.conn.commit()
        return uid

    def updateUser(self, uid, username, password):
        cursor = self.conn.cursor()

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        query = """
        UPDATE db_user
        SET username = %s, password = %s
        WHERE uid = %s;
        """
        cursor.execute(query, (username, hashed.decode('utf-8'), uid))
        self.conn.commit()
        return uid

    def deleteUser(self, uid):
        cursor = self.conn.cursor()

        # Check if exists
        check_query = "SELECT uid FROM db_user WHERE uid = %s;"
        cursor.execute(check_query, (uid,))
        user = cursor.fetchone()

        if user is None:
            return -1

        delete_query = "DELETE FROM db_user WHERE uid = %s;"
        cursor.execute(delete_query, (uid,))
        self.conn.commit()
        return uid

    def verifyUser(self, username, password):
        cursor = self.conn.cursor()
        query = """
        SELECT uid, username, password
        FROM db_user
        WHERE username = %s;
        """
        cursor.execute(query, (username,))
        row = cursor.fetchone()

        if row is None:
            return None

        stored_hash = row[2]

        # Compare submitted password with stored hash
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return row[0]  # return user id if OK
        else:
            return -1     # incorrect password