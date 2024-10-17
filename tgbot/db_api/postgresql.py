from typing import Union

import asyncpg
from asyncpg import Pool, Connection

from tgbot.config import load_config

config = load_config(".env")


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.db.user,
            password=config.db.password,
            host=config.db.host,
            database=config.db.database,
            max_inactive_connection_lifetime=3
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):

        async with self.pool.acquire() as connection:
            connection: Connection()
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS IQ_users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username VARCHAR(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE, 
        phone BIGINT NOT NULL UNIQUE
        );
        """
        await self.execute(sql, fetch=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    @staticmethod
    def format_args2(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=2)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id, phone):
        sql = "INSERT INTO IQ_users (full_name, username, telegram_id, phone) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, full_name, username, telegram_id, phone, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM IQ_users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM IQ_users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_user(self, telegram_id, **kwargs):
        sql = "UPDATE IQ_users SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f"WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, *parameters, execute=True)

    async def count_users(self):
        return await self.execute("SELECT COUNT(*) FROM IQ_users;", fetchval=True, execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE IQ_users", execute=True)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_admins(self):
        sql = """
        CREATE TABLE IF NOT EXISTS IQ_admins (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL UNIQUE, 
        name VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, fetch=True)

    async def add_administrator(self, telegram_id, name):
        sql = "INSERT INTO IQ_admins (telegram_id, name) VALUES ($1, $2) returning *"
        return await self.execute(sql, telegram_id, name, fetchrow=True)

    async def select_all_admins(self):
        sql = "SELECT * FROM IQ_admins"
        return await self.execute(sql, fetch=True)

    async def select_id_admins(self):
        sql = "SELECT telegram_id FROM IQ_admins"
        return await self.execute(sql, fetch=True)

    async def select_admin(self, **kwargs):
        sql = "SELECT * FROM IQ_admins WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def delete_admin(self, telegram_id):
        await self.execute("DELETE FROM IQ_admins WHERE telegram_id=$1", telegram_id, execute=True)

    async def drop_admins(self):
        await self.execute("DROP TABLE IQ_admins", execute=True)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_students(self):
        sql = """
        CREATE TABLE IF NOT EXISTS IQ_Students (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL UNIQUE, 
        registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
        remaining_lessons INT NOT NULL
        );
        """
        await self.execute(sql, fetch=True)

    async def add_student(self, telegram_id, registration_date, remaining_lessons):
        sql = "INSERT INTO IQ_Students (telegram_id, registration_date, remaining_lessons) VALUES($1, $2, $3) RETURNING *"
        return await self.execute(sql, telegram_id, registration_date, remaining_lessons, fetchrow=True)

    async def select_all_students(self):
        sql = "SELECT * FROM IQ_Students"
        return await self.execute(sql, fetch=True)

    async def select_id_students(self):
        sql = "SELECT telegram_id FROM IQ_Students"
        return await self.execute(sql, fetch=True)

    async def select_student(self, **kwargs):
        sql = "SELECT * FROM IQ_Students WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_student(self, id, **kwargs):
        sql = "UPDATE IQ_Students SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f"WHERE id=$1"
        return await self.execute(sql, id, *parameters, execute=True)

    async def count_students(self):
        return await self.execute("SELECT COUNT(*) FROM IQ_Students;", fetchval=True, execute=True)

    async def delete_student(self, id):
        await self.execute("DELETE FROM IQ_Students WHERE id=$1", id, execute=True)

    async def drop_students(self):
        await self.execute("DROP TABLE IQ_Students", execute=True)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_teachers(self):
        sql = """
        CREATE TABLE IF NOT EXISTS IQ_Teachers (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL UNIQUE, 
        description VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, fetch=True)

    async def add_teacher(self, telegram_id, description):
        sql = "INSERT INTO IQ_Teachers (telegram_id, description) VALUES($1, $2) RETURNING *"
        return await self.execute(sql, telegram_id, description, fetchrow=True)

    async def select_all_teachers(self):
        sql = "SELECT * FROM IQ_Teachers"
        return await self.execute(sql, fetch=True)

    async def select_id_teachers(self):
        sql = "SELECT telegram_id FROM IQ_Teachers"
        return await self.execute(sql, fetch=True)

    # async def select_teachers(self, teacher_id):
    #     sql = "SELECT * FROM Teachers WHERE teacher_id=$1"
    #     return await self.execute(sql, teacher_id, fetch=True)

    async def select_teacher(self, **kwargs):
        sql = "SELECT * FROM IQ_Teachers WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_teacher(self, telegram_id, **kwargs):
        sql = "UPDATE IQ_Teachers SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f"WHERE telegram_id=$1"
        return await self.execute(sql, telegram_id, *parameters, execute=True)

    async def delete_teacher(self, id):
        await self.execute("DELETE FROM IQ_Teachers WHERE id=$1", id, execute=True)

    async def count_teachers(self):
        return await self.execute("SELECT COUNT(*) FROM IQ_Teachers;", fetchval=True, execute=True)

    async def drop_teachers(self):
        await self.execute("DROP TABLE IQ_Teachers", execute=True)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_teacher_group(self):
        sql = """
        CREATE TABLE IF NOT EXISTS IQ_Teacher_Groups (
        id SERIAL PRIMARY KEY,
        type_id INTEGER NOT NULL,
        type VARCHAR(255) NOT NULL,
        subject_id INTEGER NOT NULL,
        subject VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        day_id INTEGER NOT NULL,
        day VARCHAR(255) NOT NULL,
        time_id INTEGER NOT NULL,
        time VARCHAR(255) NOT NULL,
        teacher_id INTEGER NOT NULL REFERENCES IQ_Teachers(id)
        );
        """
        await self.execute(sql, fetch=True)

    async def add_teacher_group(self, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id):
        sql = "INSERT INTO IQ_Teacher_Groups (type_id, type, subject_id, subject, description, day_id, day, time_id, " \
              "time, teacher_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING *"
        return await self.execute(sql, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id, fetchrow=True)

    async def select_all_teacher_groups(self):
        sql = "SELECT * FROM IQ_Teacher_Groups"
        return await self.execute(sql, fetch=True)

    async def select_in_teachers(self, teacher_id):
        sql = "SELECT * FROM IQ_Teacher_Groups WHERE teacher_id=$1"
        return await self.execute(sql, teacher_id, fetch=True)

    async def select_in_types_teach(self, teacher_id, type_id):
        sql = "SELECT * FROM IQ_Teacher_Groups WHERE teacher_id=$1 AND type_id=$2"
        return await self.execute(sql, teacher_id, type_id, fetch=True)

    async def select_in_subjects_teach(self, teacher_id, type_id, subject_id):
        sql = "SELECT * FROM IQ_Teacher_Groups WHERE teacher_id=$1 AND type_id=$2 AND subject_id=$3"
        return await self.execute(sql, teacher_id, type_id, subject_id, fetch=True)

    async def select_in_days_teach(self, teacher_id, type_id, subject_id, day_id):
        sql = "SELECT * FROM IQ_Teacher_Groups WHERE teacher_id=$1 AND type_id=$2 AND subject_id=$3 AND day_id=$4"
        return await self.execute(sql, teacher_id, type_id, subject_id, day_id, fetch=True)

    async def select_in_types(self, type_id):
        sql = "SELECT * FROM IQ_Teacher_Groups WHERE type_id=$1"
        return await self.execute(sql, type_id, fetch=True)

    async def select_in_subjects(self, type_id, subject_id):
        sql = "SELECT * FROM IQ_Teacher_Groups WHERE type_id=$1 AND subject_id=$2"
        return await self.execute(sql, type_id, subject_id, fetch=True)

    async def select_in_subjects_row(self, type_id, subject_id):
        sql = "SELECT * FROM IQ_Teacher_Groups WHERE type_id=$1 AND subject_id=$2"
        return await self.execute(sql, type_id, subject_id, fetchrow=True)

    async def select_in_subjects2(self, subject_id):
        sql = "SELECT * FROM IQ_Teacher_Groups WHERE subject_id=$1"
        return await self.execute(sql, subject_id, fetch=True)

    async def select_in_days(self, type_id, subject_id, day_id):
        sql = "SELECT * FROM IQ_Teacher_Groups WHERE type_id=$1 AND subject_id=$2 AND day_id=$3"
        return await self.execute(sql, type_id, subject_id, day_id, fetch=True)

    async def select_in_times(self, type_id, subject_id, day_id, time_id):
        sql = "SELECT * FROM IQ_Teacher_Groups WHERE type_id=$1 AND subject_id=$2 AND day_id=$3 AND time_id=$4"
        return await self.execute(sql, type_id, subject_id, day_id, time_id, fetch=True)

    # async def select_all_teacher_groups(self, **kwargs):
    #     sql = "SELECT * FROM Teacher_Groups WHERE "
    #     sql, parameters = self.format_args(sql, parameters=kwargs)
    #     return await self.execute(sql, *parameters, fetch=True)

    async def select_teacher_group(self, **kwargs):
        sql = "SELECT * FROM IQ_Teacher_Groups WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_ids_in_teachers(self, teacher_id):
        sql = "SELECT id FROM IQ_Teacher_Groups WHERE teacher_id=$1"
        return await self.execute(sql, teacher_id, fetch=True)

    async def select_teacher_group_id(self, day):
        sql = "SELECT id FROM IQ_Teacher_Groups WHERE day LIKE $1"
        return await self.execute(sql, day, fetch=True)

    async def update_teacher_group(self, id, **kwargs):
        sql = "UPDATE IQ_Teacher_Groups SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f"WHERE id=$1"
        return await self.execute(sql, id, *parameters, execute=True)

    async def delete_teacher_group(self, id):
        await self.execute("DELETE FROM IQ_Teacher_Groups WHERE id=$1", id, execute=True)

    async def count_teacher_groups(self):
        return await self.execute("SELECT COUNT(*) FROM IQ_Teacher_Groups;", fetchval=True, execute=True)

    async def drop_teacher_group(self):
        await self.execute("DROP TABLE IQ_Teacher_Groups", execute=True)

    async def get_max_type_id(self):
        sql = "SELECT MAX(type_id) FROM IQ_Teacher_Groups"
        max_type_id = await self.execute(sql, fetch=True)
        if max_type_id[0]["max"] is not None:
            return max_type_id[0]["max"]
        else:
            return 0

    async def get_max_subject_id(self):
        sql = "SELECT MAX(subject_id) FROM IQ_Teacher_Groups"
        max_subject_id = await self.execute(sql, fetch=True)
        if max_subject_id[0]["max"] is not None:
            return max_subject_id[0]["max"]
        else:
            return 0

    async def get_max_day_id(self):
        sql = "SELECT MAX(day_id) FROM IQ_Teacher_Groups"
        max_day_id = await self.execute(sql, fetch=True)
        if max_day_id[0]["max"] is not None:
            return max_day_id[0]["max"]
        else:
            return 0

    async def get_max_time_id(self):
        sql = "SELECT MAX(time_id) FROM IQ_Teacher_Groups"
        max_time_id = await self.execute(sql, fetch=True)
        if max_time_id[0]["max"] is not None:
            return max_time_id[0]["max"]
        else:
            return 0

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_groups(self):
        sql = """
        CREATE TABLE IF NOT EXISTS IQ_Groups (
        id SERIAL PRIMARY KEY,
        teacher_group_id INTEGER NOT NULL REFERENCES IQ_Teacher_Groups(id),
        student_id INTEGER NOT NULL REFERENCES IQ_Students(id)
        );
        """
        await self.execute(sql, fetch=True)

    async def add_group(self, teacher_group_id, student_id):
        sql = "INSERT INTO IQ_Groups (teacher_group_id, student_id) VALUES ($1, $2) RETURNING *"
        return await self.execute(sql, teacher_group_id, student_id, fetchrow=True)

    async def select_groups(self, teacher_group_id):
        sql = "SELECT * FROM IQ_Groups WHERE teacher_group_id=$1"
        return await self.execute(sql, teacher_group_id, fetch=True)

    async def select_id_groups(self, teacher_group_id):
        sql = "SELECT id FROM IQ_Groups WHERE teacher_group_id=$1"
        return await self.execute(sql, teacher_group_id, fetch=True)

    async def select_groups2(self, student_id):
        sql = "SELECT teacher_group_id FROM IQ_Groups WHERE student_id=$1"
        return await self.execute(sql, student_id, fetch=True)

    async def select_groups3(self, student_id):
        sql = "SELECT id FROM IQ_Groups WHERE student_id=$1"
        return await self.execute(sql, student_id, fetch=True)

    async def select_all_groups(self):
        sql = "SELECT * FROM IQ_Groups"
        return await self.execute(sql, fetch=True)

    async def select_group(self, **kwargs):
        sql = "SELECT * FROM IQ_Groups WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_group(self, tgs_id, **kwargs):
        sql = "UPDATE IQ_Groups SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f"WHERE id=$1"
        return await self.execute(sql, tgs_id, *parameters, execute=True)

    async def delete_group(self, id):
        await self.execute("DELETE FROM IQ_Groups WHERE id=$1", id, execute=True)

    async def count_groups(self):
        return await self.execute("SELECT COUNT(*) FROM IQ_Groups;", fetchval=True, execute=True)

    async def drop_groups(self):
        await self.execute("DROP TABLE IQ_Groups", execute=True)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_attendance(self):
        sql = """
        CREATE TABLE IF NOT EXISTS IQ_Attendance (
        id SERIAL PRIMARY KEY,
        teacher_group_id INTEGER NOT NULL REFERENCES IQ_Teacher_Groups(id),
        student_id INTEGER NOT NULL REFERENCES IQ_Students(id), 
        lesson_date DATE NOT NULL,
        attendance BOOLEAN NULL, 
        marks INTEGER NULL
        );
        """
        await self.execute(sql, fetch=True)

    async def add_attendance_record(self, teacher_group_id, student_id, lesson_date, attendance, marks):
        sql = "INSERT INTO IQ_Attendance (teacher_group_id, student_id, lesson_date, attendance, marks) VALUES ($1, $2, $3, $4, $5) RETURNING *"
        return await self.execute(sql, teacher_group_id, student_id, lesson_date, attendance, marks, fetchrow=True)

    async def select_all_attendance_records(self):
        sql = "SELECT * FROM IQ_Attendance"
        return await self.execute(sql, fetch=True)

    async def select_attendances(self, teacher_group_id):
        sql = "SELECT * FROM IQ_Attendance WHERE teacher_group_id=$1"
        return await self.execute(sql, teacher_group_id, fetch=True)

    async def select_attendances_2(self, teacher_group_id, lesson_date):
        sql = "SELECT * FROM IQ_Attendance WHERE teacher_group_id=$1 AND lesson_date=$2"
        return await self.execute(sql, teacher_group_id, lesson_date, fetch=True)

    async def select_attendances_3(self, student_id):
        sql = "SELECT id FROM IQ_Attendance WHERE student_id=$1"
        return await self.execute(sql, student_id, fetch=True)

    async def select_attendances_4(self, teacher_group_id):
        sql = "SELECT id FROM IQ_Attendance WHERE teacher_group_id=$1"
        return await self.execute(sql, teacher_group_id, fetch=True)

    async def select_attendance_record(self, **kwargs):
        sql = "SELECT * FROM IQ_Attendance WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_id_attendance_record(self, teacher_group_id):
        sql = "SELECT id FROM IQ_Attendance WHERE teacher_group_id=$1"
        return await self.execute(sql, teacher_group_id, fetch=True)

    async def update_attendance_record(self, id, **kwargs):
        sql = "UPDATE IQ_Attendance SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f"WHERE id=$1"
        return await self.execute(sql, id, *parameters, execute=True)

    async def select_marks_for_student_in_last_two_months(self, student_id, two_months_ago):
        sql = "SELECT * FROM IQ_Attendance WHERE student_id=$1 AND lesson_date>=$2"
        return await self.execute(sql, student_id, two_months_ago, fetch=True)

    async def delete_attendance_record(self, id):
        await self.execute("DELETE FROM IQ_Attendance WHERE id=$1", id, execute=True)

    async def count_attendance_records(self):
        return await self.execute("SELECT COUNT(*) FROM IQ_Attendance;", fetchval=True, execute=True)

    async def drop_attendance(self):
        await self.execute("DROP TABLE IQ_Attendance", execute=True)

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_skips(self):
        sql = """
        CREATE TABLE IF NOT EXISTS IQ_Skips (
        id SERIAL PRIMARY KEY,
        student_id INTEGER NOT NULL REFERENCES IQ_Students(id), 
        lesson_date DATE NOT NULL
        );
        """
        await self.execute(sql, fetch=True)

    async def add_skip(self, student_id, lesson_date):
        sql = "INSERT INTO IQ_Skips (student_id, lesson_date) VALUES ($1, $2) RETURNING *"
        return await self.execute(sql, student_id, lesson_date, fetchrow=True)

    async def select_all_skips(self):
        sql = "SELECT * FROM IQ_Skips"
        return await self.execute(sql, fetch=True)

    async def select_skips_3(self, student_id):
        sql = "SELECT id FROM IQ_Skips WHERE student_id=$1"
        return await self.execute(sql, student_id, fetch=True)

    async def select_skips_for_student_in_last_two_months(self, student_id, two_months_ago):
        sql = "SELECT * FROM IQ_Skips WHERE student_id=$1 AND lesson_date>=$2"
        return await self.execute(sql, student_id, two_months_ago, fetch=True)

    async def select_skip(self, **kwargs):
        sql = "SELECT * FROM IQ_Skips WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_skip(self, id, **kwargs):
        sql = "UPDATE IQ_Skips SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f"WHERE id=$1"
        return await self.execute(sql, id, *parameters, execute=True)

    async def delete_skip(self, student_id, lesson_date):
        await self.execute("DELETE FROM IQ_Skips WHERE student_id=$1 And lesson_date=$2", student_id, lesson_date, execute=True)

    async def delete_skip2(self, id):
        await self.execute("DELETE FROM IQ_Skips WHERE id=$1", id, execute=True)

    async def count_skips(self):
        return await self.execute("SELECT COUNT(*) FROM IQ_Skips;", fetchval=True, execute=True)

    async def drop_skip(self):
        await self.execute("DROP TABLE IQ_Skips", execute=True)

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def create_table_deep_links(self):
        sql = """
        CREATE TABLE IF NOT EXISTS IQ_Deep_links (
        id SERIAL PRIMARY KEY,
        is_used BOOLEAN NOT NULL 
        );
        """
        await self.execute(sql, fetch=True)

    async def add_deep_link(self, is_used):
        sql = "INSERT INTO IQ_Deep_links (is_used) VALUES ($1) RETURNING *"
        return await self.execute(sql, is_used, fetchrow=True)

    async def select_deep_link(self, **kwargs):
        sql = "SELECT * FROM IQ_Deep_links WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_deep_link(self, id, **kwargs):
        sql = "UPDATE IQ_Deep_links SET "
        sql, parameters = self.format_args2(sql, parameters=kwargs)
        sql += f"WHERE id=$1"
        return await self.execute(sql, id, *parameters, execute=True)

    async def delete_deep_link(self, id):
        await self.execute("DELETE FROM IQ_Deep_links WHERE id=$1", id, execute=True)

    async def drop_deep_link(self):
        await self.execute("DROP TABLE IQ_Deep_links", execute=True)


text = """
    INSERT INTO IQ_users (id, full_name, username, telegram_id, phone) VALUES
    (999, 'Vlad Anatol', 'sobachka', 163479610, 998999987800),
    (888, 'Alex Mihail', 'ne_sobachka', 173479610, 998999987801),
    (71, 'Ислам', 'username1', 163479611, 998999987851),
    (72, 'Бунёд', 'username2', 163479612, 998999987852),
    (73, 'Дима', 'username3', 163479613, 998999987853),
    (74, 'Ровш', 'username4', 163479614, 998999987854),
    (75, 'Толик', 'username5', 163479615, 998999987855),
    (76, 'Чечня', 'username6', 163479616, 998999987856),
    (77, 'Луна', 'username7', 163479617, 998999987857);

    INSERT INTO IQ_Teachers (id, telegram_id, description) VALUES
    (777, 163479610, 'Dmitriy Anatol ochen lubit mathematical'),
    (555, 173479610, 'Alex Mihail ochen lubit pythics');

    INSERT INTO IQ_StudentsIQ_Students (id, telegram_id) VALUES
    (51, 163479611, 12),
    (52, 163479612, 12),
    (53, 163479613, 12),
    (54, 163479614, 12),
    (55, 163479615, 12),
    (56, 163479616, 12),
    (57, 163479617, 12);
    
    INSERT INTO IQ_Teacher_Groups (type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id) VALUES
    (1, 'Подготовительные', 1, 'Математика', 'Математика номер 1', 1, 'Пн-Ср-Пт', 1, '10:00', 777),
    (1, 'Подготовительные', 1, 'Математика', 'Математика номер 1', 2, 'Пн-Ср', 1, '10:00', 777),
    (1, 'Подготовительные', 2, 'Физика', 'Физика номер 2', 3, 'Вт-Чт-Сб', 2, '14:00', 555),
    (1, 'Подготовительные', 2, 'Физика', 'Физика номер 2', 3, 'Вт-Чт-Сб', 3, '16:00', 555);

    INSERT INTO IQ_Groups (teacher_group_id, student_id) VALUES
    (1, 51),
    (1, 52),
    (2, 53),
    (2, 54),
    (3, 55),
    (3, 56),
    (4, 57);
    """
