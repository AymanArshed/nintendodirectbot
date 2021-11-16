import pickle
import random
import firebase_admin
import json

from firebase_admin import credentials
from firebase_admin import db
from nltk import word_tokenize
from nltk.corpus import stopwords

from flask import Flask, request, jsonify

cred_obj = firebase_admin.credentials.Certificate('C:\\Users\\ayman\\Downloads\\peppy-glyph-331801-firebase-adminsdk-9950x-94d25c3c95.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL': 'https://peppy-glyph-331801-default-rtdb.firebaseio.com/'
	})

directDict = pickle.load(open('knowledgebase.p', 'rb'))
app = Flask(__name__)


@app.route('/')
def hello():
    return 'Webhooks test'


currTopic = None
@app.route('/intentIssue', methods=['POST'])
def intentIssue():
    data = request.json
    #print(f'UserMsg: {data["queryResult"]["queryText"]}')
    #print(f'intent {data["queryResult"]["intent"]["displayName"]}')
    userMessage = data["queryResult"]["queryText"]
    intent = data["queryResult"]["intent"]["displayName"]
    if intent == "Specific game":
        topics = getSpecificGameTopics(userMessage, directDict.keys())
        topic = random.choice(topics)
        global currTopic
        currTopic = topic
        fact = random.choice(directDict.get(topic))
        response = fact + " Do you want to know more about " + topic + "?"
    elif intent == "Specific game - yes":
        topic = currTopic
        fact = random.choice(directDict.get(topic))
        response = fact + " Feel free to ask me more questions about Nintendo Direct!"
    elif intent =="Specific game - no":
        response = "Ok! Do you have any other questions about Nintendo Direct?"
    elif intent == "Summary":
        response = "Nintendo Direct covered a lot of topics like: Mario, Zelda, Metroid, Pokemon, Super Monkey Ball, Fire Emblem, and the Nintendo Switch"
    elif intent == "name.default":
        userName = data["queryResult"]["parameters"]["name"]
        response = dbWrite(userName)
    responseData = {
        "fulfillmentText": response,
    }
    webhookResponse = jsonify(responseData)
    return webhookResponse

def getSpecificGameTopics(userMessage, keys):
    userMessage = userMessage.lower()
    tokens = word_tokenize(userMessage)
    stop_words = set(stopwords.words('english'))
    content = [t for t in tokens if t not in stop_words]
    countsDict = {x: content.count(x) for x in content}
    # print([x for x in countsDict.items()])
    multipleItems = [x for x in countsDict.items() if x[1] > 1]
    # print(multipleItems)
    if multipleItems:
        topics = [x[0] for x in multipleItems if x[0] in keys]
    else:
        topics = [x[0] for x in countsDict.items() if x[0] in keys]
    # print(topics)
    return topics

def dbWrite(name):
    ref = db.reference('/User/')
    user = ref.get()
    print('I am in the function')
    print(user)
    for dict in user:
        key, val = list(dict.items())[0]
        print(key, val)
        if(val == name):
            response = 'Welcome back, ' + name + '! What did you want to know about Nintendo Direct?'
            return response
    data = {}
    data['User'] = []
    for dict in user:
        data['User'].append(dict)
    data['User'].append({
        'first': name
    })
    with open('write.txt', 'w') as f:
        json.dump(data,f)
    with open('write.txt') as json_file:
        content = json.load(json_file)
    ref = db.reference('/')
    ref.set(content)
    response = 'Nice to meet you ' + name + '! What did you want to know about Nintendo Direct?'
    return response


if __name__ == '__main__':
    app.run(debug=True)
    # main()
