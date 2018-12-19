
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import os
import time
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
api_key = ""
session = requests.Session()

def decryptData(data, sourceCertKey, targetCert):
    
    return data

def createInbox(target_party, email):
    data = {
        "party_name": target_party,
        "email": email
    }

    r = session.post(host + "/v1/inboxes/create", data=json.dumps(data), headers=headers, verify=not insecure, timeout=5)
    if r.status_code != 200:
        raise Exception("createInbox " + str(r.status_code) + " " +  r.reason)
    
    res = r.json()
    return res["api_key"]

def getNextTransmission(party, api_key):
    head = headers
    head["api_key"] = api_key

    r = session.get(host + "/v1/inboxes/" + party  + "/transmissions/next", headers=head, verify=not insecure, timeout=5)
    if r.status_code != 200:
        raise Exception("getNextTransmission " + str(r.status_code) + " " +  r.reason)
    
    res = r.json()

    data = base64.b64decode(res["message"])
    
    return res["tid"], data

def confirmReceived(party, tid, api_key):
    head = headers
    head["api_key"] = api_key

    r = session.post(host + "/v1/inboxes/" + party  + "/transmissions/" + tid + "/confirm-received", headers=head, verify=not insecure, timeout=5)
    if r.status_code != 200:
        raise Exception("confirmReceived " + str(r.status_code) + " " +  r.reason)

class TransmissionState(Enum):
    UNKNOWN = 0
    CREATED = 1
    TRANSFERRED = 2
    DELIVERED = 3

def register(args):
    fname = "keys/" + args.party

    email = ""
    if args.email is not None:
        email = args.email

    api_key = createInbox(args.party, email)
    
    logging.info("Api Key: " + api_key)
    with open(fname, "w") as f:
        f.write(api_key)

def get(args):
    fname = "keys/" + args.party
    if args.api_key is not None:
        api_key = args.api_key
    else:
        # read the api key from file
        try:
            with open(fname, 'r') as f:
                api_key = f.read().replace('\n', '')
            
        except Exception as ex:
            logging.warn('no api key specified: ' + ex)

    tid, data = getNextTransmission(args.party, api_key)
    logging.info("new transmission received: " + tid)

    if args.dir is not None:
        if not os.path.exists(args.dir):
            raise Exception("directory for incoming transmissions does not exist")
        else:
            with open(args.dir + "/" + tid, 'wb') as f:
                f.write(data)
    else:
        logging.info("Data: " + data.decode("utf-8"))

    confirmReceived(args.party, tid, api_key)
    logging.info("transmission confirmed: " + tid)

if __name__ == "__main__":
    
    logging.basicConfig(format='%(asctime)s[%(levelname)s][%(name)s][%(lineno)d]:%(message)s', level=logging.INFO)
    try:
        parser = argparse.ArgumentParser(description='simple socomap receiver client', usage='%(prog)s [options]')
        parser.add_argument("--insecure", default=False, action='store_true',  help="disables the cert verification of the remote host")
        
        requiredNamed = parser.add_argument_group('required arguments')
        requiredNamed.add_argument('--host', required=False, default="https://socomap.infotech.de", help='message broker host system, includes port and protocol (Sample: https://localhost:8080)')

        subparsers = parser.add_subparsers(dest='subparser_name')
        register_cmd = subparsers.add_parser('register')
        register_cmd.add_argument('party', help="the name of the new party")
        register_cmd.add_argument('--email', help="contact email adress")

        get_cmd = subparsers.add_parser('get')
        get_cmd.add_argument('party', help='the name of the party')
        get_cmd.add_argument('--dir', help='directory where the transmissions are dumped')
        get_cmd.add_argument('--api_key', help='api_key for the party, defaults to content of the file "keys/<party>"')
        get_cmd.add_argument('--all', action='store_true', help='gets all available message')

        run_cmd = subparsers.add_parser('run', help="runs a periodically check for new messages")
        run_cmd.add_argument('party', help='the name of the party')
        run_cmd.add_argument('--dir', help='directory where the transmissions are dumped')
        run_cmd.add_argument('--api_key', help='api_key for the party, defaults to content of the file "keys/<party>"')

        args = parser.parse_args()

        if not os.path.exists("keys"):
            os.mkdir("keys")

        # set the host
        host = args.host
        insecure = args.insecure
        
        if args.subparser_name == "register":
            register(args)

        if args.subparser_name == "get":
            get(args)
            while args.all:
                get(args)

        if args.subparser_name == "run":
            # periodically check for new messages
            while True:
                try:
                    get(args)
                except Exception as ex:
                    time.sleep(5)
                    logging.warning(ex)

    except Exception as ex:
        logging.warning(ex)
