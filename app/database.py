from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor

from config import (
    MYSQL_CHARSET,
    MYSQL_DATABASE,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
    UPLOAD_FOLDER,
)


def get_connection(use_database=True):
    connection_settings = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "charset": MYSQL_CHARSET,
        "cursorclass": DictCursor,
        "autocommit": False,
    }
    if use_database:
        connection_settings["database"] = MYSQL_DATABASE
    return pymysql.connect(**connection_settings)


def initialize_database():
    Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

    server_connection = get_connection(use_database=False)
    try:
        with server_connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` "
                f"CHARACTER SET {MYSQL_CHARSET} COLLATE {MYSQL_CHARSET}_unicode_ci"
            )
        server_connection.commit()
    finally:
        server_connection.close()

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id VARCHAR(32) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(80) NOT NULL,
                    event_date DATE NOT NULL,
                    event_time VARCHAR(20) NOT NULL,
                    venue VARCHAR(255) NOT NULL,
                    organizer VARCHAR(255) NOT NULL,
                    description TEXT,
                    max_part INT NULL,
                    deadline DATE NULL,
                    status VARCHAR(40) NOT NULL DEFAULT 'Upcoming',
                    banner LONGTEXT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS participants (
                    id VARCHAR(32) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    cls VARCHAR(80) NOT NULL,
                    section VARCHAR(20) NOT NULL,
                    roll VARCHAR(80) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    event_id VARCHAR(32) NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    CONSTRAINT fk_participants_event
                        FOREIGN KEY (event_id) REFERENCES events(id)
                        ON DELETE CASCADE,
                    UNIQUE KEY unique_roll_event (roll, event_id)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS app_meta (
                    meta_key VARCHAR(100) PRIMARY KEY,
                    meta_value VARCHAR(255) NOT NULL
                )
                """
            )
        connection.commit()
    finally:
        connection.close()
