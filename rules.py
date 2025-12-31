from config import client

def add(database, collection, data):
    db = client[database]
    collection = db[collection]
    collection.insert_one(data)

def get(database, collection, query):
    db = client[database]
    collection = db[collection]
    return collection.find_one(query)

def get_all(database, collection, query):
    db = client[database]
    collection = db[collection]
    return list(collection.find(query))

def update(database, collection, query, data):
    db = client[database]
    collection = db[collection]
    collection.update_one(query, {"$set": data})

def update_all(database, collection, query, data):
    db = client[database]
    collection = db[collection]
    collection.update_many(query, {"$set": data})

def delete(database, collection, query):
    db = client[database]
    collection = db[collection]
    collection.delete_one(query)