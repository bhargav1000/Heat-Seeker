# Flask Packages
from __future__ import unicode_literals, print_function
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import json

# Load Packages
import re
import pandas as pd
import numpy as np
import plac #  wrapper over argparse
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
from dateutil import parser
from spacy.matcher import PhraseMatcher
#nlp=spacy.load("en_core_web_sm")

app = Flask(__name__)

path_to_model=Path("/path/to/model")
print("Loading model from", path_to_model)
nlp2=spacy.load(path_to_model)
print("Model loaded...")

@app.route("/test",methods=["POST"])
def home():
    return "ner api running"

@app.route("/isAlive",methods=["POST"])
def isAlive():
    return "TRUE"

@app.route("/predict",methods=["POST"])
def detect_entity():
    
    request_data=request.json
    if 'msg_list' not in request_data:
        return 'msg_list not in request, please ensure that messageList attribute is \"msg_list\"'
    
    else:
        response_dict={}
        msg_list=request_data['msg_list']
        ner_output_list=[]
        
        for msg_request in msg_list:
            ner_output={}
        
            if 'id' not in msg_request:
                ner_output['id_error']="'id' attribute not found"
                ner_output['msg_error']="msg not processed"
            
            else:
                ner_output['id']=msg_request['id']
            
                if 'msg' not in msg_request:
                    ner_output['msg_error']="'msg' attribute not found"
                
                else:
                    final_entities={}
                    msg=msg_request['msg']
                    msg=msg.lower()
                    msg=msg.replace(",", "")
                    msg=msg.replace(".", " ")
                    msg=msg.replace(":", " ")
                    doc=nlp2(msg)
                    
                    entities={"balance":None, "amount":None, "account":None}
                    
                    # covert entity tags to lower case
                    for ent in doc.ents:
                        label=ent.label_.lower()
                        entities[label]=ent.text
                        
                    
                    # Basic entities
                    if entities['account'] is not None:
                        final_entities['accountId']=entities['account'] 
                    else:
                        final_entities['accountId']=None
                    
                    if entities['balance'] is not None:
                        final_entities['balance']=str(entities['balance']).replace("rs","") # removes rs if picked up
                    else:
                        final_entities['balance']=None

                    if entities['amount'] is not None:
                        final_entities['amount']=str(entities['amount']).replace("rs", "") # removes rs if picked up
                    else:
                        final_entities['amount']=None
                        
                    # convert dict to list and add to ner_output dict
                    ner_output['ner_output']=final_entities
                
                
            ner_output_list.append(ner_output)
        
        response_dict['msg_response']=ner_output_list
        
        return jsonify(response_dict)
                
        
                    
        
# Error handlers
@app.errorhandler(404)
def error404(e):
    return "404 Not Found\n(You might be looking for /predict)", 404

@app.errorhandler(405)
def error405(e):
    return "405 Method Not Allowed\n(use POST requests only)", 405

@app.errorhandler(403)
def error403(e):
    return '403 Forbidden'

@app.errorhandler(500)
def error500(e):
    return '500 Internal Server Error'

@app.errorhandler(502)
def error502(e):
    return '502 Bad Gateway'

@app.errorhandler(504)
def error504(e):
    return '504 Gateway Timeout'

if __name__ == "__main__":
    app.run(port=8080, debug=False, threaded=True)
        
