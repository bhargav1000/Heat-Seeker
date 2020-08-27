# Load Packages
from __future__ import unicode_literals, print_function

import pandas as pd
import numpy as np
import plac #  wrapper over argparse
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
from tqdm import tqdm # loading bar
import mysql.connector
from spacy.matcher import PhraseMatcher
from annotator import dataset_annotation
nlp=spacy.load("en_core_web_sm")

# # Import Data
test=pd.read_csv("/path/to/your/dataset")
test['accountid']=test['account_id']
# test['txn_date']=test['date']
# test=test.drop(columns=['account_id', 'Unnamed: 0', 'date'])
test['balance']=test['balance']

# annotate and produce training dataset
training_data=dataset_annotation(test)
print("ANNOTATION DONE!")

# # Train function

import warnings
from spacy.util import minibatch, compounding
def main(model=None, output_dir=None, n_iter=100, training_data=None):
    """Load the model, set up the pipeline and train the entity recognizer."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")
    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")
    # add labels
    for _, annotations in training_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    # get names of other pipes to disable them during training
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    # only train NER
    with nlp.disable_pipes(*other_pipes) and warnings.catch_warnings():
        # show warnings for misaligned entity spans once
        warnings.filterwarnings("ignore", category=UserWarning, module='spacy')
        # reset and initialize the weights randomly – but only if we're
        # training a new model
        if model is None:
            optimizer = nlp.begin_training()
        else:
            optimizer = nlp.resume_training()
        for itn in range(n_iter):
            print(itn)
            random.shuffle(training_data)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(training_data, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                try:
                    nlp.update(
                        texts,  # batch of texts
                        annotations,  # batch of annotations
                        drop=0.5,  # dropout - make it harder to memorise data
                        losses=losses,
                        sgd=optimizer
                    )
                except:
                    pass
            print("Losses", losses) # print in same line
    
    # save model to output directory
    if output_dir is not None:
        output_dir = output_dir
    if not output_dir.exists():
        output_dir.mkdir()
    with nlp.use_params(optimizer.averages):
        print("Saving best model")
        nlp.to_disk(output_dir) # save best model to disk
    print("Saved model to", output_dir)

# # Train model

import time
start_time=time.time()
main(output_dir=Path("/path/to/save/model"), training_data=training_data, n_iter=100)
elapsed_time = time.time() - start_time
print("Training time:")
print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
