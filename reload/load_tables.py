import argparse
import pandas as pd
from pathlib import Path
from db import DB


def create_tables(cursor, sql_filepath: str = "create_tables.sql"):
    print(f"Executing SQL file: {sql_filepath}")
    try:
        with open(sql_filepath, "r") as file:
            sql_commands = file.read()
            cursor.execute(sql_commands)
            print(f"Successfully executed SQL from {sql_filepath}")
    except Exception as e:
        print(f"Error executing SQL file {sql_filepath}: {str(e)}")
        raise


def load_classes(courses, cursor):
    insert_query = """
            INSERT INTO class (cid, cname, ccode, cdesc, term, years, cred, csyllabus) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (cid) DO UPDATE SET 
                cname = EXCLUDED.cname,
                ccode = EXCLUDED.ccode,
                cdesc = EXCLUDED.cdesc,
                term = EXCLUDED.term,
                years = EXCLUDED.years,
                cred = EXCLUDED.cred,
                csyllabus = EXCLUDED.csyllabus;
        """
    # cleaned CSV uses columns: cid,cname,cdesc,term,years,cred,ccode,csyllabus
    for i, row in courses.iterrows():
        cursor.execute(
            insert_query,
            (
                row.get("cid"),
                row.get("cname"),
                row.get("ccode"),
                row.get("cdesc"),
                row.get("term"),
                row.get("years"),
                row.get("cred"),
                row.get("csyllabus"),
            ),
        )


def load_meeting(meetings, cursor):
    insert_query = """
            INSERT INTO meeting (mid, ccode, starttime, endtime, cdays) 
            VALUES (%s, %s, %s, %s, %s) 
            ON CONFLICT (mid) DO UPDATE SET 
                ccode = EXCLUDED.ccode,
                starttime = EXCLUDED.starttime,
                endtime = EXCLUDED.endtime,
                cdays = EXCLUDED.cdays;
        """
    # cleaned CSV uses: mid, ccode, starttime, endtime, cdays
    # convert to full timestamps (DB expects TIMESTAMP)
    meetings["starttime"] = pd.to_datetime(meetings["starttime"], format="%H:%M:%S")
    meetings["endtime"] = pd.to_datetime(meetings["endtime"], format="%H:%M:%S")
    for i, row in meetings.iterrows():
        cursor.execute(
            insert_query,
            (
                row.get("mid"),
                row.get("ccode"),
                row.get("starttime"),
                row.get("endtime"),
                row.get("cdays"),
            ),
        )


def load_requisite(requisites, cursor):
    insert_query = """
                INSERT INTO requisite (classid, reqid, prereq) 
                VALUES (%s, %s, %s)
                ON CONFLICT (classid, reqid) DO UPDATE SET prereq = EXCLUDED.prereq;
            """
    # cleaned CSV uses: classid, reqid, prereq
    if requisites.empty:
        return
    # normalize prereq to boolean (handles 'true'/'false' strings)
    if requisites["prereq"].dtype == object:
        requisites["prereq"] = (
            requisites["prereq"]
            .astype(str)
            .str.lower()
            .map({"true": True, "false": False})
        )
    else:
        requisites["prereq"] = requisites["prereq"].astype(bool)

    for i, row in requisites.iterrows():
        cursor.execute(
            insert_query,
            (
                row.get("classid"),
                row.get("reqid"),
                row.get("prereq"),
            ),
        )


def load_room(rooms, cursor):
    insert_query = """
                        INSERT INTO room (rid, building, room_number, capacity) 
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (rid) DO UPDATE SET 
                            building = EXCLUDED.building,
                            room_number = EXCLUDED.room_number,
                            capacity = EXCLUDED.capacity;
                    """
    for i, row in rooms.iterrows():
        cursor.execute(
            insert_query,
            (
                row["rid"],
                row["building"],
                row["room_number"],
                row["capacity"],
            ),
        )


def load_section(sections, cursor):
    insert_query = """
                        INSERT INTO section (sid, roomid, cid, mid, semester, years, capacity) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (sid) DO UPDATE SET 
                            roomid = EXCLUDED.roomid,
                            cid = EXCLUDED.cid,
                            mid = EXCLUDED.mid,
                            semester = EXCLUDED.semester,
                            years = EXCLUDED.years,
                            capacity = EXCLUDED.capacity;
                    """
    for i, row in sections.iterrows():
        cursor.execute(
            insert_query,
            (
                row.get("sid"),
                row.get("roomid"),
                row.get("cid"),
                row.get("mid"),
                row.get("semester"),
                row.get("years"),
                row.get("capacity"),
            ),
        )


def reset_sequences(cursor):
    """
    Resets serial sequences for all tables to align with the current maximum values.
    :param cursor: Database cursor
    """
    sequence_reset_queries = [
        "SELECT setval(pg_get_serial_sequence('class', 'cid'), COALESCE(MAX(cid), 1)) FROM class;",
        "SELECT setval(pg_get_serial_sequence('meeting', 'mid'), COALESCE(MAX(mid), 1)) FROM meeting;",
        "SELECT setval(pg_get_serial_sequence('room', 'rid'), COALESCE(MAX(rid), 1)) FROM room;",
        "SELECT setval(pg_get_serial_sequence('section', 'sid'), COALESCE(MAX(sid), 1)) FROM section;",
        "SELECT setval(pg_get_serial_sequence('syllabus', 'chunkid'), COALESCE(MAX(chunkid), 1)) FROM syllabus;",
    ]
    for query in sequence_reset_queries:
        cursor.execute(query)


def load_data(
    sql_filepath: str = "ETL/db/create_tables.sql",
):
    # Read cleaned CSVs directly from the repository root `data` folder
    data_dir = Path(__file__).resolve().parent / "data"
    try:
        courses = pd.read_csv(data_dir / "class.csv")
        meetings = pd.read_csv(data_dir / "meeting.csv")
        rooms = pd.read_csv(data_dir / "room.csv")
        sections = pd.read_csv(data_dir / "section.csv")
        requisites = pd.read_csv(data_dir / "requisite.csv")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Clean CSV file not found in {data_dir}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error reading cleaned CSV files from {data_dir}: {e}")

    print("\n--- Loading data into database ---")
    db = DB()
    conn = db.connection
    cursor = conn.cursor()

    # Create tables
    create_tables(cursor, sql_filepath=sql_filepath)

    # Load la data
    load_classes(courses, cursor)
    load_meeting(meetings, cursor)
    load_requisite(requisites, cursor)
    load_room(rooms, cursor)
    load_section(sections, cursor)
    reset_sequences(cursor)

    conn.commit()
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print(f"Data loaded successfully!")


def main():
    parser = argparse.ArgumentParser(
        description="Load transformed data into the database"
    )
    parser.add_argument(
        "--sql",
        default="ETL/db/create_tables.sql",
        help="Path to SQL schema file to execute (default: ETL/db/create_tables.sql)",
    )

    args = parser.parse_args()
    load_data(sql_filepath=args.sql)


if __name__ == "__main__":
    main()
