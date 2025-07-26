import requests
import json


class TestRun:
    def __init__(self, username, password):
        self.url = (
            "https://companyname.spiraservice.net/SpiraPlan/Services/v5_0/RestService.svc/projects/{project_id}/test-runs"
            "?end_date=null")
        self.username = username
        self.password = password

    def updateStatus(self, payload):
        """
        Update the test run based on the payload
        """
        response = requests.put(self.url, data=payload, headers={'Content-Type': 'application/json'},
                                auth=(self.username,
                                      self.password), verify=False)
        print(response.status_code)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Fail")

    def updateIncident(self, incident_id, payload):
        """
        Update the incident with the updated payload with the linked test runs if failed/blocked
        :param incident_id:
        :param payload:
        :return:
        """
        url = f"https://companyname.spiraservice.net/SpiraPlan/Services/v5_0/RestService.svc/projects/{project_id}/incidents/{incident_id}"
        response = requests.put(url, auth=(self.username,
                                           self.password), json=payload, verify=False,
                                headers={'Content-Type': 'application/json'})
        print(response.status_code)
        if response.status_code == 200:
            print(f"{incident_id} updated with steps")

    def getIncident(self, incident_id):
        """
        Get the details of a particular incident
        :param incident_id:
        :return:
        """
        url = f"https://companyname.spiraservice.net/SpiraPlan/Services/v5_0/RestService.svc/projects/{project_id}/incidents/{incident_id}"
        response = requests.get(url, auth=(self.username,
                                           self.password), verify=False)
        print(response.status_code)
        if response.status_code == 200:
            return response.json()
