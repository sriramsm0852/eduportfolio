# reset_db.py
import os
import database

if os.path.exists("smart_classroom.db"):
    os.remove("smart_classroom.db")
    print("Old database removed")
    
database.init_db()
print("New database created with updated schema")