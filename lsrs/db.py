import logging
import os
import pathlib

from dotenv import load_dotenv
import pymysql
from pymysql.err import OperationalError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
load_dotenv()


def execute_multi_commands(cursor, commands):
    sql_commands = [
        command.strip() for command in commands.split(';')
        if not command.strip().startswith('#')
    ]
    # Remove empty query
    sql_commands.pop()
    for command in sql_commands:
        try:
            cursor.execute(command)
            logger.info(f'SQL: {command}')
        except OperationalError as exc:
            logger.warning(f'SQL: {command} is skipped: {exc}')


def execute_sql_script(cursor, path):
    with open(path, 'r') as f:
        sql_schema = f.read()
    execute_multi_commands(cursor, commands=sql_schema)


class DBService:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, create_database=False):
        if create_database:
            self.init_db()

        self.connection = pymysql.connect(
            host=os.getenv('MYSQL_DATABASE_HOST'),
            user=os.getenv('MYSQL_DATABASE_USER'),
            database=os.getenv('MYSQL_DATABASE_DB')
        )
        self.cursor = self.connection.cursor()

    @classmethod
    def init_db(cls, path=None):
        if path is None:
            path = pathlib.Path(cls.dir_path) / 'sql/schema.sql'

        db_name = os.getenv('MYSQL_DATABASE_DB')
        create_database = f"""DROP DATABASE IF EXISTS `{db_name}`;
            SET default_storage_engine=InnoDB;
            SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

            CREATE DATABASE IF NOT EXISTS {db_name}
                DEFAULT CHARACTER SET utf8mb4
                DEFAULT COLLATE utf8mb4_unicode_ci;
            USE {db_name};
            """

        logger.info(f"Create db {db_name} and tables from {path}")
        connection = pymysql.connect(
            host=os.getenv('MYSQL_DATABASE_HOST'),
            user=os.getenv('MYSQL_DATABASE_USER'),
        )
        cursor = connection.cursor()
        execute_multi_commands(commands=create_database, cursor=cursor)
        execute_sql_script(path=path, cursor=cursor)
        connection.commit()
        connection.close()

    def drop_db(self):
        self.cursor.execute(f'DROP DATABASE {os.getenv("MYSQL_DATABASE_DB")};')
        self.connection.commit()

    def delete_table(self, table):
        self.cursor.execute(f"DELETE FROM {table};")
        self.connection.commit()

    def insert_data(self, path=None):
        if path is None:
            path = pathlib.Path(self.dir_path) / 'sql/test_data_insert.sql'

        logger.info("Insert example data")
        execute_sql_script(path=path, cursor=self.cursor)
        self.connection.commit()
