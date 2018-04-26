# /usr/bin/env python
import redis
from flask import Flask, request, url_for, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import time
import re

flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'top-secret!'

# Redis client
r = redis.StrictRedis(host='localhost', port=6379, db=0)
p = r.pubsub()
p.subscribe('broadcast_rsp')

# Constants
TIMEOUT = 20
patt = re.compile('Water (.*)')

@flask_app.route("/", methods=['GET','POST'])
def sms_service_request():
	"""Respond to incoming messages with a friendly SMS."""
		
	rcv_msg = request.form['Body']

	# Start our response
	resp = MessagingResponse()

	match = patt.search(rcv_msg)

	if (match):
		rcv_msg = "Water"

	in_dic = actions.get(rcv_msg)
	
	# if command is present in dictionary
	if (in_dic == None):
 	   action_msg = "I only understand the following commands: " + str(actions.keys())
	else:
		if (match):
			action_msg = actions[rcv_msg](match.group(1))
		else:
			action_msg = actions[rcv_msg]()

	# Add a message
	resp.message("Ahoy! Thanks so much for your message. " + action_msg)

	return str(resp)

def sms_ahoy_reply():
	return "waterPIC will keep your plants moisty and tasty"

def plant_status():
	r.publish('to_broadcast', 'status')
	t_start = time.time()
	msg = p.get_message()
	while(not msg and (time.time()-t_start) < TIMEOUT):
		msg = p.get_message()
	return "plants status\n" + msg['data']

def water(plant):
	r.publish('to_broadcast', 'water ' + plant)
	return "watering " + plant + " plant!"

actions = { "Hi"	 : sms_ahoy_reply,   \
			"Status" : plant_status,	 \
			"Water" : water}


if __name__ == "__main__":
	flask_app.run(debug=False)
