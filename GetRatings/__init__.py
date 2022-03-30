import logging
import json
import azure.functions as func


def main(req: func.HttpRequest, ratings: func.DocumentList) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if ratings:
        logging.info(str(ratings))
        jsondocs = []
        for rating in ratings:
            jsondoc = func.Document.to_json(rating)
            logging.info(str(jsondoc))
            jsondocs.append(jsondoc)
        finaljson = json.dumps(jsondocs)
        return func.HttpResponse(finaljson)
    else:
        return func.HttpResponse(
             "Not found",
             status_code=404
        )
