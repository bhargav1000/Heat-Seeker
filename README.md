# Heat-Seeker
A Named Entity Recognition algorithm with a companion REST API to detect entities of interest in a SMS. 


# About
A REST API which detects specific entities in a SMS (it can also work on any given text for that matter) via a Named Entity Recognition algorithm written in python using the [spaCy](https://spacy.io/) package. It simplifies the process of identifying key elements in a given SMS where it can be mined to reveal information without the use of regular expressions or keyword search. The API is written using [Flask](https://flask.palletsprojects.com/en/1.1.x/) and accepts a message list in a POST request and outputs the corresponding entities it has detected in a message.


# Get started
- Install the requirements via ```pip install requirements.txt```
(creating a virutal environment is recommended, I have used a conda environment here)

- Annotate the dataset. It is already done via ```annotator.py``` which is specific to SMSs. The dataset must contain the message and the requisite fields: `accountid`, `amount` and `balance` as present in the message. Take a look at the [sample dataset](https://github.com/bhargav1000/Heat-Seeker/blob/master/sample_dataset.csv) to get started.
	- It is written to detect the following fields:
		- accountid - The account number of the transaction, generally follows this format `XXXX1234` (other formats may also be detected).
		- amount - The amount in the transaction (currently detects integer values for simplicity).
		- balance - The balance of the account in the message.

	- The training code, ```ner_train.py``` automatically annotates the messages before training.

	- You can also add custom annotations to your dataset, please ensure that they follow this format:
	```
	[("<text>", {"entities": [(<starting string index>, <ending string index>, "<entity name>")]})]
	```

	- Check out this example:
	```
	TRAIN_DATA = [
        ("Uber blew through $1 million a week", {"entities": [(0, 4, "ORG")]}),
        ("Google rebrands its business apps", {"entities": [(0, 6, "ORG")]})]
	```

	- You can read more about annotations [here](https://spacy.io/usage/training#training-simple-style).
	(For a more detailed explanation, see this [link](https://spacy.io/api/annotation#named-entities).)


- Add the paths to your dataset and model output location.
Now run ```python ner_train.py```. This will start training the model.


- Once the model is trained, you can start the API.
Run ```python main.py``` and start sending requests!


- The API currently accepts POST requests only. 
This is the request format:
```json
{
	"msglist":[
		{
			"msg":"The message you want to send",
			"id":"the id of the message (can be a number or a string, helps you keep track of the message)"
		}
	] 
}
```

The output has the following format:
```json
{
	"msg_response":[
		{
			"id": "the id of the message",
			"ner_output":{
				"accountId": "<value>",
				"balance": "<value>",
				"amount": "<value>"
			}
		}
	]
}
```



# Troubleshooting
- If the API does not start immediately, try changing the `port` parameter in **line 132** of `main.py` to a port of your choice.
- If you receive any errors in the message response, please check `msg_list` to correct any typos or errors.   


# Tips and tricks:
- You can use the requests library to send your requests to the api. This can help with request automation. 
Send the request using the `json` parameter in `requests.post()` and use ```requests.post("localhost:8080/predict", json=msg_request).text``` to receive the text output in the response. Learn more about requests [here](https://requests.readthedocs.io/en/master/).

- If you wish to use a GUI based method, use [Postman](https://www.postman.com/).



