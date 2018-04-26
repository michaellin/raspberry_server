# /usr/bin/env python
import redis
from flask import Flask, request, url_for, jsonify
from twilio.twiml.messaging_response import MessagingResponse

flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'top-secret!'

# Redis client
r = redis.StrictRedis(host='localhost', port=6379, db=0)
p = r.pubsub()

@flask_app.route("/", methods=['GET','POST'])
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

actions = { "Hi"	 : sms_ahoy_reply,   \
			"Status" : plant_status,	 \
			"Water chili" : water_chili }


if __name__ == "__main__":
	flask_app.run(debug=False)
