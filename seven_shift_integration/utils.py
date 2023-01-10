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
    new_end_date = datetime.strftime(end_date, '%Y-%m-%dT%H:%M:%S') + "Z"
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

    location_dict = [
        {
            'id': "308509"
        },
        {
            'id': "308503"
        },
        {
            'id': "308505"
        },
        {
            'id': "308504"
        },
        {
            'id': "308507"
        },
        {
            'id': "308502"
        },
        {
            'id': "308508"
        },
        {
            'id': "308506"
        },

    ]
    sales_data_count = len(sales_data)
    location_data_count = len(location_dict)

    loop_count = sales_data_count if sales_data_count < location_data_count else location_data_count
    from_date = datetime.strftime(from_date, '%Y-%m-%d %H:%M:%S')

    for i in range(loop_count):
        body = {
            "location_id": location_dict[i]['id'],
            "date": str(datetime.now().date()),
            "department_id": None,
            "actual_sales": sales_data[i]['netSales'],
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
