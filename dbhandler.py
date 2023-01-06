import sqlite3
from time import time
import random
class DBHandler:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name,check_same_thread=False)
        cur = self.conn.cursor()
        # Table for the queues
        # ID | Title | Description | Display Current | CODE | AUTH_CODE | TOTAL_ENTRIES | CURRENT_ENTRY | SURVEY_ID
        cur.execute("CREATE TABLE IF NOT EXISTS queue (id INTEGER PRIMARY KEY, title TEXT, description TEXT, display_current INTEGER, code TEXT, auth_code TEXT, total_entries INTEGER, current_entry INTEGER DEFAULT -1)")

        # Table for the queue questions
        # ID | queue_id | text | subtext | Type (0 = text, 1 = multiple choice, 2 = checkbox, 3 = dropdown) | Options (separated by newlines) | Required (0 = no, 1 = yes) | order
        cur.execute("CREATE TABLE IF NOT EXISTS queue_form (id INTEGER PRIMARY KEY, queue_id INTEGER, text TEXT, subtext TEXT, type INTEGER, options TEXT, required INTEGER, form_order INTEGER)")
        
        # Table for the queue entries
        # ID | Queue ID | Data | Timestamp | Status (0 = waiting, 1 = being answered, 2 = answered) | Handler Name
        cur.execute("CREATE TABLE IF NOT EXISTS queue_entries (id INTEGER PRIMARY KEY, queue_id INTEGER, data TEXT, timestamp INTEGER, status INTEGER, handler_name TEXT)")
        self.conn.commit()
        
    
    def create_queue(self, title, description, display_current):
        cur = self.conn.cursor()

        # generate a 6 character code
        code = ''
        authcode = ''
        for i in range(6):
            # Include a-z, A-Z, 0-9
            code += chr(random.choice([random.randint(48, 57), random.randint(65, 90), random.randint(97, 122)]))
        for i in range(12):
            authcode += chr(random.choice([random.randint(48, 57), random.randint(65, 90), random.randint(97, 122)]))
        cur.execute("INSERT INTO queue VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (title, description, display_current, code, authcode, 0, -1))
        self.conn.commit()
        # return ID
        return cur.lastrowid, authcode, code
    
    def get_queue(self, id):
        cur = self.conn.cursor()

        # If the ID is an integer, get the queue by ID
        try:
            id = int(id)
        except:
            pass
        if isinstance(id, int):
            cur.execute("SELECT * FROM queue WHERE id=?", (id,))
            return cur.fetchone()
        # If the ID is a string, get the queue by code
        else:
            cur.execute("SELECT * FROM queue WHERE code=?", (id,))
            return cur.fetchone()

    def get_auth_queue(self, authcode):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM queue WHERE auth_code=?", (authcode,))
        return cur.fetchone()

    def get_queues(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM queue")
        return cur.fetchall()
    
    def get_queue_entries(self, id, status=None):
        cur = self.conn.cursor()
        if status is not None:
            cur.execute("SELECT * FROM queue_entries WHERE queue_id=? AND status=?", (id, status))
        else:
            cur.execute("SELECT * FROM queue_entries WHERE queue_id=?", (id,))
        entries = cur.fetchall()
        entries_json = []
        for entry in entries:
            entry_json = {}
            entry_json['id'] = entry[0]
            entry_json['queue_id'] = entry[1]
            entry_json['data'] = entry[2]
            entry_json['timestamp'] = entry[3]
            entry_json['status'] = entry[4]
            entry_json['handler_name'] = entry[5]
            entries_json.append(entry_json)
        return entries_json
    

    def add_queue_entry(self, queue_id, data):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO queue_entries VALUES (NULL, ?, ?, ?, ?, ?)", (queue_id, data, int(time()), 0, "Nobody"))
        # Update the queue's total entries
        cur.execute("UPDATE queue SET total_entries=? WHERE id=?", (self.get_queue(queue_id)[6] + 1, queue_id))
        self.conn.commit()
        # return ID
        return cur.lastrowid

    def change_queue_entry_status(self, id, status, handler_name=None):
        cur = self.conn.cursor()
        if status == -1:
            self.add_queue_entry(self.get_queue_entry(id)[1], self.get_queue_entry(id)[2], self.get_queue_entry(id)[3], self.get_queue_entry(id)[4])
            self.delete_queue_entry(id)
            return
        else:
            cur.execute("UPDATE queue_entries SET status=?, handler_name=? WHERE id=?", (status, handler_name, id))
            # Update the queue's current entry by incrementing it
            cur.execute("UPDATE queue SET current_entry=? WHERE id=?", (self.get_queue(self.get_queue_entry(id)[1])[7] + 1, self.get_queue_entry(id)[1]))
            self.conn.commit()
            return

    def get_queue_entry(self, id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM queue_entries WHERE id=?", (id,))
        return cur.fetchone()
    
    def delete_queue_entry(self, id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM queue_entries WHERE id=?", (id,))
        self.conn.commit()

    def get_next_queue_entry(self, id):
        cur = self.conn.cursor()
        # Returns the lowest ID entry with status 0
        cur.execute("SELECT * FROM queue_entries WHERE queue_id=? AND status=0 ORDER BY id ASC LIMIT 1", (id,))
        entry = cur.fetchone()
        entry_json = {}
        entry_json['id'] = entry[0]
        entry_json['queue_id'] = entry[1]
        entry_json['data'] = entry[2]
        entry_json['timestamp'] = entry[3]
        entry_json['status'] = entry[4]
        entry_json['handler_name'] = entry[5]
        return entry_json


    def verify_auth_code(self, queue_id, authcode):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM queue WHERE auth_code=? AND id=?", (authcode, queue_id))
        return cur.fetchone()

    def add_queue_form(self, queue_id, text, subtext, type, options, required, order):
        cur = self.conn.cursor()
        # Check if the order is already taken
        cur.execute("SELECT * FROM queue_form WHERE queue_id=? AND form_order=?", (queue_id, order))
        if cur.fetchone() is not None:
            # If it is, increment the order of all the other entries
            cur.execute("UPDATE queue_form SET form_order=form_order+1 WHERE queue_id=? AND form_order>=?", (queue_id, order))
        
        cur.execute("INSERT INTO queue_form VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (queue_id, text, subtext, type, options, required, order))
        self.conn.commit()
        return cur.lastrowid
    
    def remove_queue_form(self, id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM queue_form WHERE id=?", (id,))
        self.conn.commit()

    def get_queue_forms(self, queue_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM queue_form WHERE queue_id=? ORDER BY form_order ASC", (queue_id,))
        return cur.fetchall()