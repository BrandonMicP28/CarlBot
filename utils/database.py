from __future__ import annotations
from datetime import datetime, UTC
import sqlite3

STARTING_MONEY: int = 50

def create_database():
    with sqlite3.connect('database.db') as connection:
        c = connection.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS members (
                     user_id INTEGER PRIMARY KEY,
                     money INTEGER DEFAULT 0,
                     experience INTEGER DEFAULT 0,
                     wordle_streak INTEGER DEFAULT 0,
                     last_wordle_date TEXT DEFAULT NULL)''')

def get_user(user_id) -> User:
    with sqlite3.connect('database.db') as connection:
        c = connection.cursor()
        c.execute('SELECT * FROM members WHERE user_id = ?', (user_id,))
        user_data = c.fetchone()

        if user_data is None:
            c.execute('''INSERT INTO members (user_id, money) VALUES (?, ?)''', (user_id, STARTING_MONEY))
            return User(user_id, STARTING_MONEY, 0, 0, 0)

        return User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])

def get_all_users_xp():
    with sqlite3.connect('database.db') as connection:
        c = connection.cursor()
        c.execute('SELECT user_id, experience FROM members')
        data = c.fetchall()

        return {row[0]: row[1] for row in data}

def database_change_money(user_id, amount):
    with sqlite3.connect('database.db') as connection:
        c = connection.cursor()
        c.execute("""UPDATE members SET money = money + ? WHERE user_id = ?""", (amount,user_id))


def database_change_experience(user_id, amount):
    with sqlite3.connect('database.db') as connection:
        c = connection.cursor()
        c.execute("""UPDATE members SET experience = experience + ? WHERE user_id = ?""", (amount, user_id))

def set_wordle_state(user_id: int, new_wordle_streak: int, new_wordle_date):
    with sqlite3.connect('database.db') as connection:
        c = connection.cursor()
        c.execute("UPDATE members SET wordle_streak = ?, last_wordle_date = ? WHERE user_id = ?", (new_wordle_streak, new_wordle_date, user_id))

def get_leaderboard(size: int, category: str) -> list[User]:
    with sqlite3.connect('database.db') as connection:
        valid_categories = ['experience', 'money']
        if category not in valid_categories:
            raise ValueError(f'Invalid category {category}')
        c = connection.cursor()
        c.execute(f"SELECT user_id, money, experience, wordle_streak, last_wordle_date FROM members ORDER BY {category} DESC LIMIT ?", (size,))
        data = c.fetchall()
        return [User(member_data[0], member_data[1], member_data[2], member_data[3], member_data[4]) for member_data in data]

class User:
    def __init__(self, user_id, money, experience, wordle_streak, last_wordle_date):
        self.id = user_id
        self.money = money
        self.experience = experience
        self.__wordle_streak = wordle_streak
        self.__last_wordle_date = last_wordle_date

    def change_money(self, amount):
        database_change_money(self.id, amount)
        self.money += amount

    def change_experience(self, amount):
        database_change_experience(self.id, amount)
        self.experience += amount

    def get_wordle_streak(self) -> tuple[int, str | None]:
        now = datetime.now(UTC)

        if not self.__last_wordle_date:
            return self.__wordle_streak, self.__last_wordle_date

        last_played = datetime.strptime(self.__last_wordle_date, '%Y-%m-%d')
        diff = (now.date() - last_played.date()).days

        if diff > 1:
            set_wordle_state(self.id, 0, None)
            self.__last_wordle_date = None
            self.__wordle_streak = 0

        return self.__wordle_streak, self.__last_wordle_date

    def won_wordle_streak(self) -> bool:
        now = datetime.now(UTC)

        self.__wordle_streak, self.__last_wordle_date = self.get_wordle_streak()
        if self.__last_wordle_date:
            last_played = datetime.strptime(self.__last_wordle_date, '%Y-%m-%d')
            diff = (now.date() - last_played.date()).days
        else:
            diff = 1

        if diff == 1:
            self.__wordle_streak += 1
            self.__last_wordle_date = now.strftime('%Y-%m-%d')
            set_wordle_state(self.id, self.__wordle_streak, self.__last_wordle_date)
            return True

        return False