import logging
import uuid
import azure.functions as func
import time
import requests
import json
import os

def validateUser(userId):
    logging.info('userId ' + userId)
    call = requests.get('https://serverlessohapi.azurewebsites.net/api/GetUser', params = {'userId': userId})
    return call.status_code == requests.codes.ok

def validateProduct(productId):
    logging.info('productId ' + productId)
    call = requests.get('https://serverlessohapi.azurewebsites.net/api/GetProduct', params = {'productId': productId})
    return call.status_code == requests.codes.ok

def getParam(req, text):
    param = req.params.get(text)
    if not param:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            param = req_body.get(text)
    return param

class Rating:
    def __init__(self, userId, productId, locationName, rating, userNotes):
        self.userId = userId
        self.productId = productId
        self.locationName = locationName
        self.rating = rating
        self.userNotes = userNotes
        self.id = str(uuid.uuid4())
        self.timestamp = time.time()

    def isValidRating(self):
        rating = self.rating
        if int(rating) >=0 and int(rating) <=5:
            return True
        return False

    def isValid(self):
        if  self.isValidRating() \
            and validateUser(self.userId) \
            and validateProduct(self.productId):
            return True
        return False

    def printJson(self):
        json_data = {}
        json_data["userId"] = self.userId
        json_data["productId"] = self.productId
        json_data["locationName"] = self.locationName
        json_data["rating"] = str(self.rating)
        json_data["userNotes"] = self.userNotes
        json_data["id"] = self.id
        json_data["timestamp"] = str(self.timestamp)
        return json.dumps(json_data)

    def checkAlert(self):
        url = "https://languageparser.cognitiveservices.azure.com/text/analytics/v3.2-preview.1/sentiment?opinionMining=true"
        payload = {}
        payload["documents"] = []
        document = {}
        document["id"] = "1"
        document["text"] = self.userNotes
        payload["documents"].append(document)

        params = {}
        params["Ocp-Apim-Subscription-Key"] = os.getenv("Ocp-Apim-Subscription-Key")
        req = requests.post(url, headers=params, data=json.dumps(payload))
        output = req.json()
        logging.info("result: "+ str(output))

        sentiment = {}
        #result = json.loads(output)
        sentiment["scores"] = output["documents"][0]["confidenceScores"]
        if (sentiment["scores"]["negative"] > 0.7):
            logging.warning("Negative userNotes")


def main(req: func.HttpRequest, doc: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    userId = getParam(req, 'userId')
    productId = getParam(req, 'productId')
    locationName = getParam(req, 'locationName')
    rating = getParam(req, 'rating')
    userNotes = getParam(req, 'userNotes')

    rating = Rating(userId, productId, locationName, rating, userNotes)

    if rating.isValid():
        rating.checkAlert()
        json_doc = rating.printJson()
        doc.set(func.Document.from_json(json_doc))
        return func.HttpResponse(json_doc)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
