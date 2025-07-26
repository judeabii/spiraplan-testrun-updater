import requests


class GetTestSet:
    def __init__(self, username, password):

        self.url1 = (
            'https://companyname.spiraservice.net/SpiraPlan/Services/v5_0/RestService.svc/projects/{project_id}/test-sets'
            '?starting_row=1&number_of_rows=1000&'
            f'sort_field=Name&sort_direction=asc&release_id={release_id}')
        self.test_set_list = {}
        self.username = username
        self.password = password

    def getTestSetList(self):
        response = requests.get(self.url1, auth=(self.username,
                                                 self.password), verify=False)

        print(response.status_code)
        if response.status_code == 200:
            test_sets = response.json()
            self.test_set_list = {}
            count = 0
            for test_set in test_sets:
                test_set_name = test_set['Name'].strip().lower() #Store test set name
                test_set_id = test_set['TestSetId'] # Store test set ID
                self.test_set_list[test_set_name] = test_set_id #Create a dictionary for easy look up
                count += 1
            print(f"Count is {count}")
            return self.test_set_list
        else:
            print(f"Error fetching test sets: {response.status_code}")
            return None

    def getTestSetTestcases(self, testSetId):
        """
        Retrieve all the testcases linked to a particular test set
        :param testSetId:
        :return: the response that contains all the testcases in the test set
        """
        url = ("https://companyname.spiraservice.net/SpiraPlan/Services/v5_0/RestService.svc/"
               f"projects/{project_id}/test-sets/{testSetId}/test-cases")
        response = requests.get(url, auth=(self.username,
                                           self.password), verify=False)
        print(response.status_code)
        if response.status_code == 200:
            return response.json()

    def getTestSetPayload(self, testSetId):
        """
        Get the test set payload so that this can be altered with the new execution values from the tracker
        :param testSetId:
        :return: Payload response
        """
        url = (f"https://companyname.spiraservice.net/SpiraPlan/Services/v5_0/RestService.svc/"
               f"projects/{project_id}/test-runs/create/test_set/{testSetId}")
        response = requests.post(url, auth=(self.username,
                                            self.password), verify=False)
        print(response.status_code)
        if response.status_code == 200:
            return response.json()