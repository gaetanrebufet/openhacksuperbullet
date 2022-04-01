import logging
import json
import azure.functions as func
import requests
import os

def getSentiment(notes):
    url = "https://languageparser.cognitiveservices.azure.com/text/analytics/v3.2-preview.1/sentiment?opinionMining=true"
    payload = {}
    payload["documents"] = []
    document = {}
    document["id"] = "1"
    document["text"] = notes
    payload["documents"].append(document)

    params = {}
    params["Ocp-Apim-Subscription-Key"] = os.getenv("Ocp-Apim-Subscription-Key")
    req = requests.post(url, headers=params, data=json.dumps(payload))
    output = req.json()
    logging.info("result: "+ str(output))

    sentiment = {}
    #result = json.loads(output)
    sentiment["scores"] = output["documents"][0]["confidenceScores"]
    sentiment["sentimentScore"] = output["documents"][0]["sentiment"]
    if (sentiment["scores"]["negative"] > 0.7):
        sentiment["sentimentFlag"] = "Alert"
    else:
        sentiment["sentimentFlag"] = "Normal"
    return sentiment


def main(req: func.HttpRequest, ratings: func.DocumentList) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if ratings:
        json_rating = func.Document.to_json(ratings[0])
        rating = json.loads(json_rating)
        scores = getSentiment(rating["userNotes"])
        rating["sentiment"] = scores
        logging.info("scores: " + str(scores))
        return func.HttpResponse(func.Document.to_json(rating))
    else:
        return func.HttpResponse(
             "Not found",
             status_code=404
        )
