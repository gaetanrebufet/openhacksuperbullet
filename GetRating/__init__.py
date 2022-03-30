import logging
import json
import azure.functions as func


def main(req: func.HttpRequest, ratings: func.DocumentList) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if ratings:
        return func.HttpResponse(func.Document.to_json(ratings[0]))
    else:
        return func.HttpResponse(
             "New code for failure",
             status_code=200
        )
