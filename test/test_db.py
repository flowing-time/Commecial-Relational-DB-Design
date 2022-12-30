import logging
import os
import pathlib
from unittest import TestCase

import pymysql
from pymysql.err import IntegrityError, OperationalError

from lsrs.db import execute_multi_commands, execute_sql_script
from lsrs.sql.queries import (
    get_childcare_info,
    get_holiday_names,
    get_states,
    update_childcare,
)

logger = logging.getLogger(__name__)


class DBTest(TestCase):

    def setUp(self):
        self.connection = pymysql.connect(
            host=os.getenv('MYSQL_DATABASE_HOST'),
            user=os.getenv('MYSQL_DATABASE_USER'),
        )
        self.cursor = self.connection.cursor()

        name = os.getenv('MYSQL_DATABASE_DB_TEST')
        self.connection.database = name
        try:
            execute_multi_commands(
                self.cursor,
                f"DROP DATABASE IF EXISTS `{name}`;"
                f"CREATE DATABASE {name} "
                f"DEFAULT CHARACTER SET 'utf8';"
                f"USE {name};"
            )
            self.connection.commit()
        except OperationalError as exc:
            logger.error("Failed creating database: {}".format(exc))
            exit(1)

        self.connection.database = name

        # Create tables
        dir_path = os.path.dirname(os.path.realpath(__file__))
        path = pathlib.Path(dir_path) / '../lsrs/sql/schema.sql'
        try:
            execute_sql_script(self.cursor, path)
            self.connection.commit()
        except OperationalError as exc:
            logger.error("Failed creating table: {}".format(exc))

        # Add data
        try:
            execute_multi_commands(self.cursor, self.insert_data())
            self.connection.commit()
        except IntegrityError as exc:
            logger.error("Failed inserting data: {}".format(exc))
            exit(1)

    def tearDown(self):
        name = os.getenv('MYSQL_DATABASE_DB_TEST')
        self.cursor.execute(
            f"DROP DATABASE IF EXISTS `{name}`;"
        )
        self.connection.commit()
        self.connection.close()

    @staticmethod
    def insert_data():
        # Insert test data in database
        return """
            INSERT INTO State(name) VALUES ('state1');
            INSERT INTO State(name) VALUES ('state2');

            insert into City (name, state, population)
             value ("cool city", "state1", 100);
            insert into City (name, state, population)
             value ("great city", "state2", 500);
            insert into City (name, state, population)
             value ("bad city", "state2", 404);

            insert into date (date, is_holiday) values ("2021-02-02", 1);
            insert into DateName (date, name)
             value ("2021-02-02", "special holiday");

            insert into store (
            store_number, phone_number, street_address, restaurant, city_id)
             value ("cc1", "234", "Rd 123", "Burger King", 1);
            insert into store (
            store_number, phone_number, street_address, restaurant, snack_bar,
             city_id)
             value ("cc3", "23", "Rd 456", "KFC", "Subway", 2);
            insert into store (store_number, phone_number, street_address,
             snack_bar, city_id)
             value ("cc6", "08", "Rd 789", "Subway", 2);
            insert into store (store_number, phone_number, street_address,
             snack_bar, city_id)
             value ("cc7", "200", "Rd 111", "MacDonald", 3);

            insert into Childcare (store_number, childcare_limit)
             value ("cc1", 30);
            insert into Childcare (store_number, childcare_limit)
             value ("cc3", 45);
            insert into Childcare (store_number, childcare_limit)
             value ("cc6", 50);
        """

    def test_holiday(self):
        with self.subTest("Test get_holidays"):
            self.cursor.execute(get_holiday_names())
            result = self.cursor.fetchall()

            # Compare the obtained results and expected results
            self.assertEqual(len(result), 1)
            self.assertEqual(len(result[0]), 1)
            self.assertEqual(result[0][0], 'special holiday')

    def test_report1(self):
        # TODO add test here
        pass

    def test_report2(self):
        # TODO add test here
        pass

    def test_report3(self):
        with self.subTest("Test get_states"):
            self.cursor.execute(get_states())
            result = self.cursor.fetchall()

            self.assertEqual(len(result), 2)
            for i in range(2):
                self.assertEqual(len(result[i]), 1)
                self.assertEqual(result[i][0], f'state{i+1}')

        with self.subTest("Test get_store_revenue"):
            # TODO add test here
            pass

    def test_childcare(self):
        with self.subTest('Test get_childcare'):
            self.cursor.execute(get_childcare_info())
            result = self.cursor.fetchall()

            self.assertEqual(len(result), 4)
            self.assertEqual(len(result[0]), 2)

        with self.subTest('Test update_childcare'):
            self.cursor.execute(update_childcare('cc1', 500))
            self.connection.commit()

            self.cursor.execute(get_childcare_info())
            results = self.cursor.fetchall()

            for result in results:
                if result[0] == 'cc1':
                    self.assertEqual(result[1], 500)
