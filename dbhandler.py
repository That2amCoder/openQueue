import sqlite3
from time import time
import random
class DBHandler:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name,check_same_thread=False)
        self.cur = self.conn.cursor()
        # ID | Title | Description | Display Current | CODE | AUTH_CODE | TOTAL_ENTRIES | CURRENT_ENTRY
        self.cur.execute("CREATE TABLE IF NOT EXISTS queue (id INTEGER PRIMARY KEY, title TEXT, description TEXT, display_current INTEGER, code TEXT, auth_code TEXT, total_entries INTEGER, current_entry INTEGER)")
        #Table for the queue entries
        # ID | Queue ID | Name | Question | Extra | Timestamp | Status (0 = waiting, 1 = being answered, 2 = answered) | Handler Name
        self.cur.execute("CREATE TABLE IF NOT EXISTS queue_entries (id INTEGER PRIMARY KEY, queue_id INTEGER, name TEXT, question TEXT, extra TEXT, timestamp INTEGER, status INTEGER, handler_name TEXT)")
        self.conn.commit()
        
    
    def create_queue(self, title, description, display_current):
        # generate a 6 character code
        code = ''
        authcode = ''
        for i in range(6):
            # Include a-z, A-Z, 0-9
            code += chr(random.choice([random.randint(48, 57), random.randint(65, 90), random.randint(97, 122)]))
        for i in range(12):
            authcode += chr(random.choice([random.randint(48, 57), random.randint(65, 90), random.randint(97, 122)]))
        self.cur.execute("INSERT INTO queue VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (title, description, display_current, code, authcode, 0, -1))
        self.conn.commit()
        # return ID
        return self.cur.lastrowid, authcode, code
    
    def get_queue(self, id):
        # If the ID is an integer, get the queue by ID
        try:
            id = int(id)
        except:
            pass
        if isinstance(id, int):
            self.cur.execute("SELECT * FROM queue WHERE id=?", (id,))
            return self.cur.fetchone()
        # If the ID is a string, get the queue by code
        else:
            self.cur.execute("SELECT * FROM queue WHERE code=?", (id,))
            return self.cur.fetchone()
            
    def get_auth_queue(self, authcode):
        self.cur.execute("SELECT * FROM queue WHERE auth_code=?", (authcode,))
        return self.cur.fetchone()

    def get_queues(self):
        self.cur.execute("SELECT * FROM queue")
        return self.cur.fetchall()
    
    def get_queue_entries(self, id, status=None):
        if status is not None:
            self.cur.execute("SELECT * FROM queue_entries WHERE queue_id=? AND status=?", (id, status))
        else:
            self.cur.execute("SELECT * FROM queue_entries WHERE queue_id=?", (id,))
        return self.cur.fetchall()
    

    def add_queue_entry(self, queue_id, name, question, extra=None):
        self.cur.execute("INSERT INTO queue_entries VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (queue_id, name, question, extra, int(time()), 0, None))
        # Update the queue's total entries
        self.cur.execute("UPDATE queue SET total_entries=? WHERE id=?", (self.get_queue(queue_id)[6] + 1, queue_id))
        self.conn.commit()
        # return ID
        return self.cur.lastrowid

    def change_queue_entry_status(self, id, status, handler_name=None):
        if status == -1:
            self.add_queue_entry(self.get_queue_entry(id)[1], self.get_queue_entry(id)[2], self.get_queue_entry(id)[3], self.get_queue_entry(id)[4])
            self.delete_queue_entry(id)
            return
        else:
            self.cur.execute("UPDATE queue_entries SET status=?, handler_name=? WHERE id=?", (status, handler_name, id))
            # Update the queue's current entry by incrementing it
            self.cur.execute("UPDATE queue SET current_entry=? WHERE id=?", (self.get_queue(self.get_queue_entry(id)[1])[7] + 1, self.get_queue_entry(id)[1]))
            self.conn.commit()
            return
    
    def delete_queue_entry(self, id):
        self.cur.execute("DELETE FROM queue_entries WHERE id=?", (id,))
        self.conn.commit()

    def get_next_queue_entry(self, id):
        # Returns the lowest ID entry with status 0
        self.cur.execute("SELECT * FROM queue_entries WHERE queue_id=? AND status=0 ORDER BY id ASC LIMIT 1", (id,))
        return self.cur.fetchone()

    def verify_auth_code(self, queue_id, authcode):
        self.cur.execute("SELECT * FROM queue WHERE auth_code=? AND id=?", (authcode, queue_id))
        return self.cur.fetchone()

    