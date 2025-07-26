import excelData
from getTestSet import GetTestSet
from testRun import TestRun
import excelFromSharePoint
import json
from dotenv import load_dotenv
import os

load_dotenv()

with open('config.json') as config_file:
    config = json.load(config_file)


def batch_payload(payload, batch_size):
    """
    Used to send status updates in batches of 50 to avoid rate limits and improve performance.
    :param payload:
    :param batch_size:
    :return:
    """
    for i in range(0, len(payload), batch_size):
        yield payload[i:i + batch_size]


spira_user = os.getenv("SPIRA_USERNAME")
spira_password = os.getenv("SPIRA_PASSWORD")

obj_GetTestSet = GetTestSet(spira_user, spira_password)
obj_testRun = TestRun(spira_user, spira_password)


def update_test_case_status(payload_testcase, execution_status):
    """
    Used to upload the execution status according to the status, and to update all corresponding test steps
    :param payload_testcase:
    :param execution_status:
    :return:
    """
    status_map = {
        "Passed": 2,
        "Blocked": 5,
        "Failed": 1,
        "": 3
    }

    status_id = status_map.get(execution_status, 3)

    payload_testcase["ExecutionStatusId"] = status_id

    if payload_testcase.get('TestRunSteps'):
        for test_step in payload_testcase['TestRunSteps']:
            test_step['ExecutionStatusId'] = status_id


def process_status(test_set_list, test_results, batch_size=50):
    batch_size = 50 # batch size set to 50
    incident_step_map = {}
    case_to_incident = {}
    for testcases in test_results.values():
        for case in testcases:
            testcase_id = case.get("TestCaseId")
            incident_id = case.get("IncidentId")
            if testcase_id and incident_id:
                case_to_incident[testcase_id] = str(incident_id).strip()

    for subfunction, testSetId in test_set_list.items():
        if not test_results or subfunction not in test_results:
            continue

        excel_testcases = test_results[subfunction]
        testcase_data = obj_GetTestSet.getTestSetTestcases(
            testSetId)
        payload = obj_GetTestSet.getTestSetPayload(testSetId)

        if not payload:
            # print(f"No testcases found in test set: {testSetId}")
            continue

        if not testcase_data:
            # print(f"Test Set is empty")
            continue

        payload_lookup = {tc["TestCaseId"]: tc for tc in payload}
        testcase_lookup = {tc["TestCaseId"]: tc for tc in testcase_data}
        updated_payload = []

        for case in excel_testcases:
            testcase_id = case.get("TestCaseId")
            status = case.get("ExecutionStatus")
            incident_id = case.get("IncidentId")

            if not testcase_id or not status:
                continue

            if testcase_id not in testcase_lookup:
                # print(f"TestCase {testcase_id} not found in TestSet")
                continue

            if testcase_id not in payload_lookup:
                # print(f"TestCaseId {testcase_id} not found in TestSet {testSetId}")
                continue

            """
            The below logic is to ensure that testcases having the same status as the one picked from the tracker are skipped to prevent duplicate test runs
            """
            payload_testcase = payload_lookup[testcase_id]
            testset_testcase = testcase_lookup[testcase_id]
            current_status = testset_testcase.get("ExecutionStatusId", -1)
            status_map = {
                "Passed": 2,
                "Blocked": 5,
                "Failed": 1,
                "": 3
            }
            new_status = status_map.get(status.strip(), 3)

           """ print(f"Testcase ID: {testcase_id}")
            print(f"Current status: {current_status}")
            print(f"New Status: {new_status}")
            print(f"incident linked: {incident_id}")"""

            if new_status == 1 and not incident_id or new_status == 5 and not incident_id:
                # print(f"Skipping testcase {testcase_id} because it is marked as Failed/Blocked but has no incident ID.")
                continue

            if new_status == current_status:
                # print(f"Skipping testcase {testcase_id}")
                continue

            update_test_case_status(payload_testcase, status)
            updated_payload.append(payload_testcase)

        for batch in batch_payload(updated_payload, batch_size):
            json_payload = json.dumps(batch)
            try:
                test_run_data = obj_testRun.updateStatus(
                    json_payload)

                for updated_case in test_run_data:
                    testcase_id = updated_case.get("TestCaseId")
                    exec_status_id = updated_case.get("ExecutionStatusId")

                    '''
                    Below is the process of linking incidents to failed/blocked testcases
                    '''
                    if exec_status_id not in (1, 5):
                        continue
                    else:
                        incident_id = case_to_incident.get(testcase_id)
                        if not incident_id:
                            continue
                        step_ids = [
                            step["TestRunStepId"]
                            for step in updated_case.get("TestRunSteps", [])
                            if "TestRunStepId" in step
                        ]
                        if step_ids:
                            if incident_id not in incident_step_map:
                                incident_step_map[incident_id] = []
                            incident_step_map[incident_id].extend(step_ids)

            except Exception as e:
                print(f"Error updating batch: {e}")

        for incident_id, step_ids in incident_step_map.items():
            if not step_ids:
                continue
            try:
                incident_payload = obj_testRun.getIncident(
                    incident_id)
                incident_payload["TestRunStepIds"] = incident_payload.get("TestRunStepIds") or []
                incident_payload["TestRunStepIds"].extend(step_ids)
                incident_payload["ConcurrencyDate"] = incident_payload["LastUpdateDate"]
                obj_testRun.updateIncident(incident_id,
                                           incident_payload)
            except Exception as e:
                print(f"Failed to update incident {incident_id}: {e}")


def main():
    print(config['site_url'])
    print(config['sharepoint_path'])
    file_stream = excelFromSharePoint.read_excel_results_from_sharepoint(config['site_url'], config['sharepoint_path'],
                                                                        os.getenv('SP_USERNAME'),
                                                                         os.getenv('SP_PASSWORD'))
    test_results = excelFromSharePoint.process_excel_file(file_stream)

    test_set_list = obj_GetTestSet.getTestSetList()
    process_status(test_set_list, test_results)


if __name__ == "__main__":
    main()