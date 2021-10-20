import time
from sqlite3 import Connection, connect


DB_NAME ="UAV.db"
flight_number = 0;

def start_flight(con: Connection):
    global flight_number
    res = con.execute("INSERT into flights(start_time) values(?) RETURNING *", (time.time()*1e3, ))
    flight_number = res.fetchone()[0]
    con.commit()

def do(con):
    res = con.execute("SELECT * FROM flights")
    for row in res:
        print(row)

if __name__ == '__main__':
    db = connect(DB_NAME)
    start_flight(db)
    # do(db)