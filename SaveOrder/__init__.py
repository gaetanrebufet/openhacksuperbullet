import logging
import json
import azure.functions as func


def main(req: func.HttpRequest, doc: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    body = req.get_json()
    
    if body:
        json_doc = json.dumps(body)
        doc.set(func.Document.from_json(json_doc))
        return func.HttpResponse(json_doc)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
