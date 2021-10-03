import pymongo


class ConnectError(Exception):
    pass


def mongo_client(host="127.0.0.1", port=27017, username="nick", password="abc123456"):

    try:
        client = pymongo.MongoClient(host=host, port=port)
        client.admin.authenticate(username, password)
        return client
    except Exception:
        raise ConnectError(
            "Connection error, may be account authentication problem, "
            "please check your credentials..."
        )
