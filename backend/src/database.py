""" TODO: 
        - error handling for commands
""" 
import pymongo
import sys

DB_NAME = 'mongodb'
DB_PORT = 27017
HOST = 'localhost'

# Code created with reference to
# https://medium.com/analytics-vidhya/setting-up-a-database-class-mongodb-for-interactions-in-python-6a16417cd58e

class Database(object):
    DATABASE = None

    def connect():
        try:
            client = pymongo.MongoClient(HOST, DB_PORT)
            Database.DATABASE = client[DB_NAME]
            print("-----CONNECTED TO MONGODB DB-----")
        
        except pymongo.errors.ConnectionFailure as err:
            print("ERROR! Could not connect to database {self.db_name} failed with error: {err}")
            sys.exit(1)
            
    def insert(collection, data):
        """
            Insert data document into collection
        """
        Database.DATABASE[collection].insert(data)

    def find(collection, select=None, project=None):
        """
            Returns a cursor instance
            - can specifiy the selection and projection of attributes
        """
        return Database.DATABASE[collection].find(select, project)
    
    def find_one(collection, select=None, project=None):
        """
            Returns the first document in the collection
            - can specifiy the selection and projection of attributes
        """
        return Database.DATABASE[collection].find_one(select, project)

    def update_one(collection, project=None, select=None):
        """
            Updates one document in the collection
            - can specifiy the selection and projection of attributes
        """
        return Database.DATABASE[collection].update_one(project, select)

    def aggregate(collection, project=None):
        """
            Organizes data in embedded document arrays
        """
        return Database.DATABASE[collection].aggregate(project)

    def remove(collection, data=None, option=None):
        """
            Remove data document from collection
        """
        Database.DATABASE[collection].remove(data, option)