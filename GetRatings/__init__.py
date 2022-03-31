import logging
import json
import azure.functions as func
import requests

def getSentiment(notes):
    url = "https://languageparser.cognitiveservices.azure.com/text/analytics/v3.2-preview.1/sentiment?opinionMining=true"
    payload = {}
    payload["documents"] = []
    document = {}
    document["id"] = "1"
    document["text"] = notes
    payload["documents"].append(document)

    params = {}
    params["Ocp-Apim-Subscription-Key"] = "cee4813143494a26854eb29e7f56ba77"
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
        logging.info(str(ratings))
        jsondocs = []
        for rating in ratings:
            jsondoc = func.Document.to_json(rating)

            data = json.loads(jsondoc)
            scores = getSentiment(rating["userNotes"])
            data["sentiment"] = scores

            #logging.info(str(jsondoc))
            jsondocs.append(json.dumps(data))
        finaljson = json.dumps(jsondocs)
        return func.HttpResponse(finaljson)
    else:
        return func.HttpResponse(
             "Not found",
             status_code=404
        )
