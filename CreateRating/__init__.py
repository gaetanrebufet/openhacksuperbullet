import logging
import uuid
import azure.functions as func
import time
import requests

def validateUser(user):
    logging.info('user ' + user)
    usercall = requests.get('https://serverlessohapi.azurewebsites.net/api/GetUser', params = {'userId': str(user)})
    return usercall.status_code == requests.codes.ok


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
        if self.isValidRating() and validateUser(self.userId):
            return True
        return False
    

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    userId = getParam(req, 'userId')
    productId = getParam(req, 'productId')
    locationName = getParam(req, 'locationName')
    rating = getParam(req, 'rating')
    userNotes = getParam(req, 'userNotes')

    rating = Rating(userId, productId, locationName, rating, userNotes)

    if rating.isValid():
        return func.HttpResponse(f"Hello this seems valid: " + str(vars(rating)))
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
