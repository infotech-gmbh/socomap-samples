
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import base64
import json
import argparse
import logging
from enum import Enum

insecure = False
host = ""
headers = {
    "Accept": "text/plain",
    "Content-Type": "application/json; charset=utf-8"
}

session = requests.Session()

def secureData(data, sourceCertKey, targetCert):
    
    return data

def createTransaction(target_party):
    data = {"party": target_party}

    r = session.post(host + "/v1/transmissions/create", data=json.dumps(data), headers=headers, verify=not insecure, timeout=5)
    if r.status_code != 200:
        raise Exception("createTransaction " + str(r.status_code) + " " +  r.reason)
    
    res = r.json()
    return res["tid"]

def uploadTransmission(tid, data):

    b64data = str(base64.b64encode(data), 'ascii')
    
    data = {
        "message": b64data
    }
    r = session.post(host + "/v1/transmissions/" + tid + "/upload", data=json.dumps(data), headers=headers, verify=not insecure, timeout=5)
    if r.status_code != 200:
        raise Exception("uploadTransmission " + str(r.status_code) + " " +  r.reason)

class TransmissionState(Enum):
    UNKNOWN = 0
    CREATED = 1
    TRANSFERRED = 2
    DELIVERED = 3

def getTransmissionState(tid):

    r = session.get(host + "/v1/transmissions/" + tid + "/state", headers=headers, verify=not insecure, timeout=5)
    if r.status_code != 200:
        raise Exception("getTransmissionState " + str(r.status_code) + " " +  r.reason)

    res = r.json()
    if res["delivered"] is not None:
        return TransmissionState.DELIVERED
    if res["transferred"] is not None:
        return TransmissionState.TRANSFERRED
    if res["created"] is not None:
        return TransmissionState.CREATED
    
    return TransmissionState.UNKNOWN

if __name__ == "__main__":
    
    logging.basicConfig(format='%(asctime)s[%(levelname)s][%(name)s][%(lineno)d]:%(message)s', level=logging.INFO)
    try:
        parser = argparse.ArgumentParser(description='simple socomap sender client', usage='%(prog)s [options]')

        requiredNamed = parser.add_argument_group('required arguments')
        requiredNamed.add_argument('--host', required=False, default="https://socomap.infotech.de",  help='message broker host system, includes port and protocol (Sample: https://localhost:8080)')
        requiredNamed.add_argument('party', help='target party for the transmission')

        group = parser.add_mutually_exclusive_group(required=True)
        # either of both arguments
        group.add_argument('--file', type=argparse.FileType('rb', ), help='input file to send')
        group.add_argument('--data', type=str, help='data to send')

        parser.add_argument("--insecure", default=False, action='store_true',  help="disables the cert verification of the remote host")

        args = parser.parse_args()

        # set the host globally
        host = args.host
        insecure = args.insecure

        data = bytes()
        # todo full files should not parsed into strings
        if args.file is not None:
            data = args.file.read() # TODO!
        else:
            data = bytes(args.data, 'utf-8')

        # does nothing yet, but later it will encrypt the data
        data = secureData(data, "certKey", "cert")

        tid = createTransaction(args.party)
        logging.info("TransmissionCreated: " + tid)

        uploadTransmission(tid, data)
        logging.info("DataUploaded: " + tid)

        state = getTransmissionState(tid)
        logging.info("State is: " + str(state))

    except Exception as ex:
        logging.info(ex)
