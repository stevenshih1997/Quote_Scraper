"""SQLite3 database operations for quotes"""
import sqlite3

class DatabaseOps(object):
    """docstring for DatabaseOps"""
    def __init__(self, keyword):
        super(DatabaseOps, self).__init__()
        self.keyword = keyword
