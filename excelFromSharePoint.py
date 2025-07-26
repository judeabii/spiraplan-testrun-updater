from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from io import BytesIO
import os
from dotenv import load_dotenv
import openpyxl

load_dotenv()


def read_excel_results_from_sharepoint(site_url, sharepoint_path, email, password):
    credentials = UserCredential(email, password)
    context = ClientContext(site_url).with_credentials(credentials)

    file_stream = BytesIO()
    context.web.get_file_by_server_relative_url(sharepoint_path).download(file_stream).execute_query()
    file_stream.seek(0)

    return file_stream


def process_excel_file(file_stream, execution_status_filter=None, subfunction_filter=None):
    test_results = {}
    workbook = openpyxl.load_workbook(file_stream)
    sheet = workbook["Sheet1"]
    rows = sheet.iter_rows(values_only=True)
    headers_row = next(rows)
    headers = {col_name: idx for idx, col_name in enumerate(headers_row)}

    try:
        test_case_id_col = headers["Test case ID"]
        execution_status_col = headers["Execution Status"]
        subfunction_col = headers["Subfunction"]
        incident_col = headers["Incident ID"]
    except KeyError as e:
        raise ValueError(f"Missing required column in Excel: {e}")

    for row in rows:
        test_case_id = row[test_case_id_col]
        execution_status = row[execution_status_col]
        subfunction = row[subfunction_col]
        incident_id = row[incident_col]

        if not test_case_id or not subfunction or not execution_status:
            continue
        if execution_status_filter and execution_status != execution_status_filter:
            continue
        if subfunction_filter and subfunction != subfunction_filter:
            continue

        subfunction_key = subfunction.strip().lower()

        if subfunction_key not in test_results:
            test_results[subfunction_key] = []

        test_results[subfunction_key].append({"TestCaseId":test_case_id,
                                              "ExecutionStatus":execution_status.strip() if execution_status else None,
                                              "IncidentId":incident_id})

    return test_results