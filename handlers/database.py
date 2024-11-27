from typing import Iterable, Any
import sqlite3



class DB:
    def __init__(self, db_path=".data.db"):
        self.db_path = db_path
        
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()
        
        self.history = []
        
        
    def execute(self, query: str,
                data: Any = (),
                many: bool = False):
        
        res = None
        
        if many:
            res = self.cur.executemany(query, data)
        else:
            res = self.cur.execute(query, data)
            
        self.history.append(res)
        
        return res
        
        
    def fetchone(self):
        return self.history[-1].fetchone()
    
    
    def fetchall(self):
        return self.history[-1].fetchall()
    
    
    def fetchmany(self, size: int | None = 1):
        return self.history[-1].fetchmany(size)
    
    
    def commit(self):
        self.con.commit()