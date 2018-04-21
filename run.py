# /usr/bin/env python
# Download the twilio-python library from twilio.com/docs/libraries/python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/", methods=['GET','POST'])
def sms_service_request():
    """Respond to incoming messages with a friendly SMS."""

    recvd_msg = request.form['Body']

    # Start our response
    resp = MessagingResponse()

    in_dic = actions.get(recvd_msg)
    
    # if command is present in dictionary
    if (in_dic == None):
        action_msg = "I only understand the following commands: " + str(actions.keys())
    else:
        action_msg = actions[recvd_msg]()

    # Add a message
    resp.message("Ahoy! Thanks so much for your message. " + action_msg)

    return str(resp)

def sms_ahoy_reply():
    return "waterPIC will keep your plants moisty and tasty"

def plant_status():
    return "plants are alright"

def water_chili():
    return "watering chili plant!"

actions = { "Hi"     : sms_ahoy_reply,   \
            "Status" : plant_status,     \
            "Water chili" : water_chili }


if __name__ == "__main__":
    app.run(debug=True)
