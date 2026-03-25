from db.config import client

def add(data_base, collection, data):
    try:
        client[data_base][collection].insert_one(data)
        return True
    except Exception as e:
        print(e)
        return False

def get(data_base, collection, query):
    try:
        return client[data_base][collection].find_one(query)
    except Exception as e:
        print(e)
        return None

def get_all(data_base, collection, query):
    try:
        return list(client[data_base][collection].find(query))
    except Exception as e:
        print(e)
        return None

def delete(data_base, collection, query, data):
    try:
        client[data_base][collection].update_one(query, {"$unset": data})
        return True
    except Exception as e:
        print(e)
        return False

def update(data_base, collection, query, data):
    try:
        client[data_base][collection].update_one(query, {"$set": data})
        return True
    except Exception as e:
        print(e)
        return False