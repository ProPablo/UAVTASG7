import threading, queue
from sqlite3 import Connection, connect
from flask_socketio import SocketIO

class Job():
    def __init__(self, sql_func, name, data) -> None:
        self.sql_func = sql_func
        self.name = name
        self.data = data
        print(f"got {name} job")
        pass
    def run_sql(self, con):
        self.sql_func(self, con)

q = queue.Queue()

class QueueWorker(threading.Thread):
    def __init__(self, db_con:Connection, socket: SocketIO) -> None:
        threading.Thread.__init__(self)
        self.con = db_con
        self.sock = socket
    
    def run(self):
        while True:
            item = q.get()
            try:
                item.run_sql(self.con)
                # self.con.execute("begin")
                # for i, s in enumerate(item.sqls):
                #     self.con.execute(s, item.tuples[i])
                # self.con.execute("commit")
            except Exception as e:
                print(e)
            self.sock.emit(item.name, item.data)
            q.task_done()
            print(f"Job done: {item.name}")

def worker():
    while True:
        item = q.get()
        print(f'Working on {item}')
        print(f'Finished {item}')
        q.task_done()

# turn-on the worker thread
# threading.Thread(target=worker, daemon=True).start()

# send thirty task requests to the worker
# for item in range(30):
#     q.put(item)
# print('All task requests sent\n', end='')

# block until all tasks are done
# q.join()
# print('All work completed')