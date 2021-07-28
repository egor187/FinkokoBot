import random
import datetime
import os

import pytz
import sqlite3

tz = pytz.timezone("Europe/Moscow")
now = datetime.datetime.now(tz=tz)

con = sqlite3.connect(os.path.join("db", "finance.db"))
con.execute("PRAGMA foreign_keys = 1")  # enable FK support for sqlite engine. Need each time when you connecting to db
cur = con.cursor()


test_payment_data = (
    (
        random.randint(1, 9),
        random.randint(1, 100000),
        now - datetime.timedelta(days=random.randint(1, 60))
    ) for _ in range(100)
)

cur.executemany("INSERT INTO Payment(category, amount, paid_at) values(?, ?, ?)", test_payment_data)
con.commit()
