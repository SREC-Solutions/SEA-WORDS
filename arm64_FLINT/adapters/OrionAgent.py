#
# Copyright (c) 2021 imec-idlab-ugent
#
# SPDX-License-Identifier: LGPL-3.0
#
# Authors: Vincent Sercu (vincent.sercu@ugent.be) and Bart Moons (bamoons.moons@ugent.be)

import string
import random
from datetime import datetime

from agents._packages.HTTP.BasicHttpAgent import *
from agents.Agent import Agent

from http.client import HTTPSConnection, HTTPConnection

class OrionAgent(Agent):
	def __init__(self):
		super().__init__("OrionAgent")

		self.arg_config = self.parse_arguments()
		self.logger = self.get_logger()

		# connect to the sink over the socket
		self.sink_client = self.connect_sink_socket()
		
		self.http_client = BasicHttpAgent(self.config, self.http_receive_callback)
		res = self.http_client.send_message("version", "", "GET")
		if res[0] != 200:
			self.logger.debug("no response from server")
			exit()
		else:
			info = res[1].decode('utf-8')
			self.logger.debug("Orion info: " + info)

		self.shop4cf_data_model_uri = "https://raw.githubusercontent.com/shop4cf/data-models/master/docs/shop4cfdefinitions.jsonld#definitions/"
		self.smart_data_models_uri = "https://smart-data-models.github.io/data-models/terms.jsonld#/definitions/"
		
	def http_receive_callback(self, msg):
		msg = json.loads(msg)
		self.logger.info(msg)

	def socket_receive_callback(self, msg):
		# received a message from FLINT (the MSSQL Agent)
		msg_str = json.dumps(msg) ## CVR
		msg = json.loads(msg_str) ## CVR
		print (" CVR: \t msg: ", msg) #, "\n   \t string: ", msg_str)
		device_ctrl = msg["device-ctrl"]["device-custom-ctrl"]
		if "type" in device_ctrl:
			if device_ctrl["type"] == "work_status":
				self.process_work_status(device_ctrl)
		else: # list
			print(" CVR device_ctrl: ", device_ctrl)
			self.process_measurement(device_ctrl)

	def process_measurement(self, msg):
		# loop over all sensors
		for m in msg:
			# check if measurement for the current sensor exists
			measurement = self.measurement_exists(msg)

			if not measurement: # make a new one
				self.make_measurement(msg)
			else: # update the old one
				value = {
					"name": {"type": "Text", "value": "{}".format(msg["rxInfo"][0]["name"])},
					"rssi": {
						"type": "Integer",
						"value": "{}".format(msg["rxInfo"][0]["rssi"]),
						}
				}
				value = json.dumps(value)
				url = "v2/entities/urn:ngsi-ld:Noise:{}".format(msg["txInfo"]["measurement"])
				print ("CVR: value", value, " url: ", url)
				ret = self.do_PATCH(url + "/attrs", value)
				
				self.logger.debug("{value}".format(value=value))
				self.logger.debug("Update existing sensor instance returned: {response}".format(response=ret))

	def make_measurement(self, msg):
		measurement = {
			"id": "urn:ngsi-ld:Noise:{}".format(msg["txInfo"]["measurement"]),
            "type": "Noise",
            "name": {"type": "Text", "value": "{}".format(msg["rxInfo"][0]["name"])},
            "rssi": {"type": "Integer","value": 0},
            "refStore": {"type": "Relationship","value": "urn:ngsi-ld:Room:001"}
	    	}
		measurement = json.dumps(measurement)
		print("CVR measure",measurement)
		ret = self.do_POST("v2/entities", measurement)
		print ("CVR make measurement: ", ret)

		self.logger.debug("{measurement}".format(measurement=measurement))
		self.logger.debug("No sensor instance exists; created a new one for {resource}, returned {response}".format(resource=msg["txInfo"]["measurement"], response=ret))

	def measurement_exists(self, work_status):
		measurements = self.do_GET("v2/entities/urn:ngsi-ld:Noise:{}".format(work_status["txInfo"]["measurement"]))
		if measurements:
			measurements = json.loads(measurements)
		
		return measurements

	def process_work_status(self, msg):		
		car_body_task = self.task_exists(msg)
		
		if msg["in_out"]["value"] == "CREATED":
			progress = "pending"
		elif msg["in_out"]["value"] == "IN":
			progress = "inProgress"
		elif msg["in_out"]["value"] == "OUT":
			progress = "completed"

		if not car_body_task:
			self.make_task(msg, progress)
		else:
			status = {
				"status" : {
					"type": "Property",
					"value": progress,
					"observedAt": msg["timestamp"]["value"]
				}
			}
			status = json.dumps(status)
			ret = self.do_PATCH("ngsi-ld/v2/entities/" + car_body_task["id"] + "/" + "attrs", status)

			self.logger.debug("{status}".format(status=status))
			self.logger.debug("Update existing Task with id {id} returned: {response}".format(id=car_body_task["id"], response=ret))

	def make_task(self, msg, progress):
		rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
		uuid = "urn:ngsi-ld:Task:" + rand
		task = {
			"id": uuid,
			"type": "Task",
			"isDefinedBy": {
				"type": "Relationship",
				"object": "urn:ngsi-ld:TaskDefinition:skid-" + str(msg["skid_id"]["value"])
			},
			"workParameters": {
				"type": "Property",
				"value": {
		    		"skidId": msg["skid_id"]["value"],
					"pendulumId": msg["pendulum_id"]["value"],
					"carBodyId": msg["car_body_id"]["value"],
					"carBodyType": msg["car_body_type"]["value"],
					"voltageProgramType": msg["voltage_program_type"]["value"]
				}
			},
			"status": {
				"type": "Property",
				"value": progress,
				"observedAt": msg["timestamp"]["value"]
			},
			"@context": [
			    "https://smartdatamodels.org/context.jsonld",
			    "https://raw.githubusercontent.com/shop4cf/data-models/master/docs/shop4cfcontext.jsonld"
			]
		}
		task = json.dumps(task)
		self.do_POST("ngsi-ld/v2/entities", task)

		self.logger.debug("{task}".format(task=task))
		self.logger.debug("Created a new task for car body {car_body}".format(car_body=msg["car_body_id"]["value"]))

	def task_exists(self, work_status):
		tasks = self.do_GET("ngsi-ld/v2/entities?type=Task")
		tasks = json.loads(tasks)
		for task in tasks:
			work_param = self.shop4cf_data_model_uri + "workParameters"
			if work_param in task:
				if "carBodyId" in task[work_param]["value"]:
					if task[work_param]["value"]["carBodyId"] == work_status["car_body_id"]["value"]:
						return task
						
	def do_PATCH(self, uri, msg):
		prev = datetime.now()
		headers = { 'Content-type': "application/json" }
		self.http_client.set_headers(headers)
		res = self.http_client.send_message(uri, msg, "PUT")
		curr = datetime.now()
		diff = (curr-prev).total_seconds()
		
		self.logger.debug("Query took {time} seconds to complete".format(time=diff))
		print ("  CVR Patch res: ", res)
		return res[1]

	def do_GET(self, uri):
		prev = datetime.now()
		headers = {}
		self.http_client.set_headers(headers)
		res = self.http_client.send_message(uri, "", "GET")
		curr = datetime.now()
		diff = (curr-prev).total_seconds()
		
		self.logger.debug("Query took {time} seconds to complete".format(time=diff))
		print ("  CVR Get res: ", res)

		if res[0] == 200:
			return res[1]
		else:
			return {}

	def do_POST(self, uri, msg):
		prev = datetime.now()
		headers = { 'Content-type': "application/json" }
		self.http_client.set_headers(headers)
		self.http_client.send_message(uri, msg, "POST")
		curr = datetime.now()
		diff = (curr-prev).total_seconds()
		
		self.logger.debug("Query took {time} seconds to complete".format(time=diff))

	def do_DELETE(self, uri):
		prev = datetime.now()
		headers = {}
		self.http_client.set_headers(headers)
		res = self.http_client.send_message(uri, "", "DELETE")
		curr = datetime.now()
		diff = (curr-prev).total_seconds()
		
		self.logger.debug("Query took {time} seconds to complete".format(time=diff))

		return res[1]

	def make_json_ld_device(self, msg):
		return msg

if __name__ == "__main__":
	OrionAgent().run()
