CREATE TABLE IF NOT EXISTS class (
    cid SERIAL PRIMARY KEY,
    -- cid starts from 2
    CHECK (cid >= 2),
    cname VARCHAR(250) NOT NULL,
    ccode VARCHAR(20) NOT NULL,
    UNIQUE (cname, ccode),
    cdesc VARCHAR(250),
    term VARCHAR(50),
    years VARCHAR(50),
    cred INT,
    csyllabus VARCHAR(250)
);

CREATE TABLE IF NOT EXISTS room (
    rid SERIAL PRIMARY KEY,
    building VARCHAR(8) NOT NULL,
    room_number VARCHAR(3) NOT NULL,
    capacity INT CHECK (capacity > 0)
);

CREATE TABLE IF NOT EXISTS meeting (
    mid SERIAL PRIMARY KEY,
    ccode VARCHAR(5),
    starttime TIMESTAMP,
    endtime TIMESTAMP,
    cdays VARCHAR(5) CHECK (cdays in ('MJ', 'LWV'))
    -- Classes are MJ and LWV only
);

CREATE TABLE IF NOT EXISTS section (
    sid SERIAL PRIMARY KEY,
    roomid INT REFERENCES room (rid),
    cid INT REFERENCES class (cid),
    mid INT REFERENCES meeting (mid),
    semester VARCHAR(10),
    years VARCHAR(9),
    capacity INT,
    UNIQUE (roomid, mid, semester, years),
    UNIQUE (cid, mid, semester, years)
);

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS syllabus (
    chunkid SERIAL PRIMARY KEY,
    courseid INT REFERENCES class (cid),
    embedding_text vector (768),
    chunk TEXT
);

CREATE TABLE IF NOT EXISTS requisite (
    classid INT REFERENCES class (cid),
    reqid INT REFERENCES class (cid),
    prereq BOOLEAN,
    PRIMARY KEY (classid, reqid)
);

CREATE TABLE IF NOT EXISTS db_user (
    uid SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);