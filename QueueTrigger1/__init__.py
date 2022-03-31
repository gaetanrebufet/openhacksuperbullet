import logging
import json
import azure.functions as func
import azure.storage.blob as azureblob
import requests
import os
import re

def getBatch(url):
    rex = re.compile(".*\/(.*)-.*")
    match = rex.match(url)
    logging.info("rex: "+ str(match.groups))
    return match.group(1)

def getParams(batch):
    params = {}
    prefix = "https://gaetanstoragev2.blob.core.windows.net/bloborders/"
    params["header"] = prefix + batch + "-OrderHeaderDetails.csv"
    params["lineitems"] = prefix + batch + "-OrderLineItems.csv"
    params["productinfo"] = prefix + batch + "-ProductInformation.csv"
    return params

def combineOrderContent(paramdict):
    logging.info("starting combineOrderContent with: " + str(paramdict))
    param = {}
    param["orderHeaderDetailsCSVUrl"] = paramdict["header"]
    param["orderLineItemsCSVUrl"] = paramdict["lineitems"]
    param["productInformationCSVUrl"] = paramdict["productinfo"]
    url = "https://serverlessohmanagementapi.trafficmanager.net/api/order/combineOrderContent"
    logging.info("calling combineorders with: "+ str(param))
    req = requests.post(url, data=json.dumps(param))
    data = req.json()
    logging.info("request for combineorders: " + str(data))
    return data

def deleteAll():
    connect_str = os.getenv('gaetanstoragev2_STORAGE')
    container_client = azureblob.BlobServiceClient.from_connection_string(connect_str)
    container = container_client.get_container_client("bloborders")
    container

def checkFiles(msg: func.QueueMessage):
    event = msg.get_json()

    url = event["data"]["url"]
    logging.info("url: "+ str(url))
    
    batchtoprocess = getBatch(url)
    logging.info("Batch to process: "+ batchtoprocess)

    #logging.info("\nListing blobs...")
    # List the blobs in the container
    connect_str = os.getenv('gaetanstoragev2_STORAGE')
    container_client = azureblob.BlobServiceClient.from_connection_string(connect_str)
    container = container_client.get_container_client("bloborders")
    blob_list = container.list_blobs()
    batches= {}
    for blob in blob_list:
        #logging.info("\t" + blob.name)
        key = blob.name.split("-")[0]
        if key in batches:
            batches[key].append(blob.name)
        else:
            batches[key] = []
            batches[key].append(blob.name)
    logging.info("number of keys: " + str(len(batches.keys())))

    if len(batches[batchtoprocess]) == 3:
        logging.info("OK for batch: " + str(batchtoprocess))
        params = getParams(batchtoprocess)
        data = combineOrderContent(params)
        return data
    else:
        logging.info("Batch not complete!")
    return {}

def saveOrder(order):
    url = "https://gaetanbatchprocess.azurewebsites.net/api/saveorder"
    req = requests.post(url, data=json.dumps(order))
    logging.info("request for saving data: " + str(req.text))

def main(msg: func.QueueMessage) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))
    data = checkFiles(msg)
    if data:
        for order in data:
            logging.info("saving order "+ str(order["headers"]["salesNumber"]))
            saveOrder(order)

    logging.info("Ending")