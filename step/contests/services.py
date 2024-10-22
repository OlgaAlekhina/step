import requests
from datetime import datetime
import time
from django.conf import settings

token_cache = {'access_token': None, 'last_update': 0}

base_url = settings.BASE_URL
username = settings.USERNAME
password = settings.PASSWORD
node_id = settings.NODE_ID
raida_task_url = settings.RAIDA_TASK_URL

process_id_contests = settings.PROCESS_ID_CONTESTS
process_id_docontests = settings.PROCESS_ID_DOCONTESTS

#   Статусы конкурса
status_id_voting = settings.STATUS_ID_VOTING
status_id_active = settings.STATUS_ID_ACTIVE
status_id_result = settings.STATUS_ID_RESULT

#   Статусы заявки
status_id_access = settings.STATUS_ID_ACCESS
status_id_denied = settings.STATUS_ID_DENIED
status_id_newcontest = settings.STATUS_ID_NEWCONTEST
status_id_inworkcontest = settings.STATUS_ID_INWORKCONTEST


def get_token():
    current_time = time.time()

    if (token_cache['access_token'] is None or
            current_time - token_cache['last_update'] > 3600):

        url = f"{base_url}/api/users/token/"
        data = {'username': username, 'password': password}

        response = requests.post(url, data=data)

        if response.status_code == 200:
            token_cache['access_token'] = response.json().get('access_token')
            token_cache['last_update'] = current_time
            return token_cache['access_token']
        else:
            print(f'Ошибка: {response.status_code} - {response.text}')
            return None

    else:
        return token_cache['access_token']


def get_contests(token):
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/{node_id}?process_id={process_id_contests}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        tasks = response.json()['data']
        result = []

        status_ids = {status_id_voting, status_id_active, status_id_result};

        for task in tasks:
            status = task.get('status', {}).get('id')
            if status in status_ids:
                task_id = task.get('id', None)
                title = task.get('title', None)
                cf_brief = task['custom_fields'].get('cf_brief', None)
                category = task['custom_fields'].get('cf_konkurs_category', None)
                deadline = task['custom_fields']['cf_deadline']
                formatted_deadline = datetime.fromisoformat(deadline).strftime(
                    '%d.%m.%Y') if deadline and deadline.strip() else None
                project = task['custom_fields'].get('cf_projects', None)
                profession = task['custom_fields'].get('cf_profession', None)

                result.append({
                    'id': task_id,
                    'title': title,
                    'brief': cf_brief,
                    'category': category,
                    'deadline': formatted_deadline,
                    'award': task['custom_fields']['cf_award'],
                    'project': project if project and project.strip() else None,
                    'profession': profession if profession and profession.strip() else None
                })

        return result

    else:
        return f'Ошибка: {response.status_code} - {response.text}'


def get_solution_contests(token):
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/{node_id}?process_id={process_id_contests}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        tasks = response.json()['data']
        result = []

        status_ids = {status_id_denied}

        for task in tasks:
            status = task.get('status', {}).get('id')
            if status not in status_ids:
                task_id = task.get('id', None)
                title = task.get('title', None)

                result.append({
                    'id': task_id,
                    'title': title
                })

        return result

    else:
        return f'Ошибка: {response.status_code} - {response.text}'
