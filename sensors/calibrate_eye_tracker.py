"""
Script for calibrating the Tobii pro glasses 2.
Mostly copy pasted from the examples given with the API, modified to work with python3, using requests package
"""

import urllib.request
import json
import time
import requests

GLASSES_IP = "192.168.71.50"  # IPv4 address
PORT = 49152
base_url = 'http://' + GLASSES_IP
timeout = 1


def post_request(api_action, data=None):
    url = base_url + api_action
    response = requests.post(url, json=data)
    json_data = response.json()
    return json_data


def wait_for_status(api_action, key, values):
    url = base_url + api_action
    running = True
    json_data = None
    while running:
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req, None)
        data = response.read()
        json_data = json.loads(data)
        if json_data[key] in values:
            running = False
        time.sleep(1)
    return json_data[key]


def create_project():
    json_data = post_request('/api/projects')
    return json_data['pr_id']


def create_participant(project_id):
    data = {'pa_project': project_id}
    json_data = post_request('/api/participants', data)
    return json_data['pa_id']


def create_calibration(project_id, participant_id):
    data = {'ca_project': project_id, 'ca_type': 'default', 'ca_participant': participant_id}
    json_data = post_request('/api/calibrations', data)
    return json_data['ca_id']


def start_calibration(calibration_id):
    post_request('/api/calibrations/' + calibration_id + '/start')


if __name__ == '__main__':
    project_id = create_project()
    participant_id = create_participant(project_id)
    calibration_id = create_calibration(project_id, participant_id)

    print("Project: " + project_id, ", Participant: ", participant_id, ", Calibration: ", calibration_id, " ")

    input_var = input("Press enter to calibrate")
    print('Calibration started...')
    start_calibration(calibration_id)
    status = wait_for_status('/api/calibrations/' + calibration_id + '/status', 'ca_state', ['failed', 'calibrated'])

    if status == 'failed':
        print('Calibration failed, using default calibration instead')
    else:
        print('Calibration successful')
