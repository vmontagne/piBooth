from os import path
import json


class Store:
    storeFile = "/data/pictures/store.json"

    def __init__(self):
        if not path.exists(self.storeFile):
            f = open(self.storeFile, "w+")
            json.dump([], f)
            f.close()

    def addFile(self, filename):
        with open(self.storeFile, "r") as jsonFileR:
            data = json.load(jsonFileR)
            jsonFileR.close()
            data.insert(0, filename)
            with open(self.storeFile, "w") as jsonFileW:
                json.dump(data, jsonFileW)
                jsonFileW.close()
