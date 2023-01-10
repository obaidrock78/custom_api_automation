from datetime import timedelta
from datetime import datetime
import pytz
import requests

from seven_shift_integration.models import CronJobRecord


def get_start_and_end():
    tz = pytz.timezone('UTC')
    today = datetime.now(tz=tz)
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(1)

    return start, end


def migrate_data():
    """
    This function is called by the scheduler to migrate data from the SevenShift API to the database.
    :return:
    """
    cron_record = CronJobRecord.objects.create(status="started")
    login_url = "https://api.posveloce.com/users/authenticate"
    body = {
        "email": "api@mandys.ca",
        "password": "Api12345"
    }
    response = requests.post(login_url, json=body)
    token = response.json()['token']

    from_date, end_date = get_start_and_end()
    new_from_date = datetime.strftime(from_date, '%Y-%m-%dT%H:%M:%S') + "Z"
    new_end_date = datetime.strftime(end_date, '%Y-%m-%dT') + "23:59:59Z"
    sales_urls = f"https://api.posveloce.com/sales/locations?from={new_from_date}&to={new_end_date}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    sale_response = requests.get(sales_urls, headers=headers, timeout=600)
    sales_data = sale_response.json()

    # location_url = "https://api.7shifts.com/v2/company/244806/locations"
    # headers = {
    #     "Authorization": f"Bearer 63306662353062352d383637662d346639382d613861612d393235393664376131666136"
    # }
    # location_response = requests.get(location_url, headers=headers, timeout=600)
    # location_data = location_response.json()

    final_dict = [
        {
            'getid': "11e9f0ee-803f-7174-9e69-aa79da50e0ab",
            'id': "308509",
            'sales': '0'
        }
        , {
            'getid': "11e9813a-6c25-22a4-9923-722bc9e43bfa",
            'id': "308503",
            'sales': '0'
        },
        {
            'getid': "11e9813b-b108-e7c7-8042-f689a59258f9",
            'id': "308505",
            'sales': '0'
        },
        {
            'getid': "11e9813c-d518-505b-8042-f689a59258f9",
            'id': "308504",
            'sales': '0'
        },
        {
            'getid': "11e9813a-7146-604f-9923-722bc9e43bfa",
            'id': "308507",
            'sales': '0'
        },
        {
            'getid': "11e9813a-6314-765c-9923-722bc9e43bfa",
            'id': "308502",
            'sales': '0'
        },
        {
            'getid': "11e96c05-a13e-2b76-be63-863527f80061",
            'id': "308508",
            'sales': '0'
        },
        {
            'getid': "11e9813b-cfd9-3f27-8042-f689a59258f9",
            'id': "308506",
            'sales': '0'
        }

    ]
    for obj in sales_data:
        location_data = [x for x in final_dict if x['getid'] == obj['id']]
        if location_data:
            body = {
                    "location_id": location_data[0]['id'],
                    "date": str(datetime.now().date()),
                    "department_id": None,
                    "actual_sales": int(obj['netSales']) * 100,
                    "labor_target": 0,
                }
            headers = {
                    "Authorization": "Bearer 63306662353062352d383637662d346639382d613861612d393235393664376131666136"
                }

            url = "https://app.7shifts.com/api/v1/daily_reports"
            response = requests.post(url, json=body, headers=headers, timeout=600)
            print(response.json())
    cron_record.status = "completed"
    cron_record.save()
