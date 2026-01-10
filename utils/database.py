import sqlite3

STARTING_MONEY: int = 50

def create_database():
    with sqlite3.connect('database.db') as connection:
        c = connection.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS members (
                     user_id INTEGER PRIMARY KEY,
                     money INTEGER DEFAULT 0,
                     experience INTEGER DEFAULT 0)''')

def get_user(user_id):
    with sqlite3.connect('database.db') as connection:
        c = connection.cursor()
        c.execute('SELECT * FROM members WHERE user_id = ?', (user_id,))
        user_data = c.fetchone()

        if user_data is None:
            c.execute('''INSERT INTO members (user_id, money) VALUES (?, ?)''', (user_id, STARTING_MONEY))
            return User(user_id, STARTING_MONEY, 0)
        return User(user_data[0], user_data[1], user_data[2])

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


class User:
    def __init__(self, user_id, money, experience):
        self.user_id = user_id
        self.money = money
        self.experience = experience

    def change_money(self, amount):
        database_change_money(self.user_id, amount)
        self.money += amount

    def change_experience(self, amount):
        database_change_experience(self.user_id, amount)
        self.experience += amount