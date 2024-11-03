import time
from datetime import datetime

import requests
from django.conf import settings
from requests.exceptions import RequestException, HTTPError
from .serializers import ContestsSerializer

token_cache = {'access_token': None, 'last_update': 0}

base_url = settings.BASE_URL
username = settings.USERNAME
password = settings.PASSWORD
node_id = settings.NODE_ID

process_contests_id = settings.PROCESS_CONTESTS_ID

#   Статус конкурса
status_id_done = settings.STATUS_ID_DONE


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
            return None

    else:
        return token_cache['access_token']


def datetime_convert(date, format_date='%d.%m.%Y'):
    """Преобразование даты в заданный формат."""
    if date is not None:
        result = datetime.fromisoformat(date.rstrip("Z") + "+00:00").strftime(format_date)
    else:
        result = date
    return result


def get_archive_contests(token):
    """Получение всех конкурсов со статусом завершен. Реализация функционала Архив конкурсов."""
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/rql/{node_id}"

    try:
        completed_contests = {
            "rql": f"process.id = '{process_contests_id}' AND status.id = '{status_id_done}'"
        }

        response = requests.post(url, json=completed_contests, headers=headers)
        response.raise_for_status()  # Это вызовет исключение для статусов 4xx и 5xx

        response_data = response.json().get('data', [])

        result_data = []
        for contest in response_data:
            status_contest = contest['status'].get('name', None) if contest.get('status', None) is not None else None

            custom_fields = contest.get('custom_fields', None)
            if custom_fields is not None:
                cf_deadline = custom_fields.get('cf_deadline', None)
                cf_award = custom_fields.get('cf_award', None)
                cf_brief = custom_fields.get('cf_brief', None)
                cf_title = custom_fields.get('cf_title', None)
                cf_konkurs_category = custom_fields.get('cf_konkurs_category', None)

            else:
                cf_deadline = None
                cf_award = None
                cf_brief = None
                cf_title = None
                cf_konkurs_category = None

            result_data.append({
                'id': contest.get('id', None),
                'title': contest.get('title', None),
                'description': contest.get('description', None),
                'status': status_contest,
                'cf_deadline': datetime_convert(cf_deadline),
                'cf_award': cf_award,
                'cf_brief': cf_brief,
                'cf_title': cf_title,
                'cf_konkurs_category': cf_konkurs_category,

            }
            )

        # Эта часть нужна, чтобы использовать сериализаторы для обработки данных из Райды:
        # contest_serializer = ContestsSerializer(data=response_data, many=True)
        # contest_serializer.is_valid()
        # contests = contest_serializer.save()
        # result_data = []
        # for contest in contests:
        #     result_data.append(contest.__dict__)

        result_data = {
            "detail": {
                "code": "OK",
                "message": "Список всех конкурсов со статусом Завершен"
            },
            "data": result_data,
            "info": {
                "api_version": "0.0.1",
                "count": len(result_data),
                "compression_algorithm": "lossy"
            }
        }

        return result_data, response.status_code

    except HTTPError as http_err:
        result_data = {
            "detail": {
                "code": f"HTTP_ERROR - {response.status_code}",
                "message": str(http_err)
            }
        }
        return result_data, response.status_code

    except RequestException as err:
        result_data = {
            "detail": {
                "code": f"REQUEST_ERROR - {response.status_code}",
                "message": str(err)
            }
        }
        return result_data, response.status_code


def get_contest(token, contest_id):
    """Получение данных одного конкурса по его id."""
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/{node_id}/{contest_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Это вызовет исключение для статусов 4xx и 5xx
        response_data = response.json().get('data', [])
        contest_serializer = ContestsSerializer(data=response_data)
        contest_serializer.is_valid()
        contest = contest_serializer.save()
        result_data = contest.__dict__

        result_data = {
            "detail": {
                "code": "OK",
                "message": "Данные конкурса"
            },
            "data": result_data,
            "info": {
                "api_version": "0.0.1",
                "compression_algorithm": "lossy"
            }
        }

        return result_data, response.status_code

    except HTTPError as http_err:
        result_data = {
            "detail": {
                "code": f"HTTP_ERROR - {response.status_code}",
                "message": str(http_err)
            }
        }
        return result_data, response.status_code

    except RequestException as err:
        result_data = {
            "detail": {
                "code": f"REQUEST_ERROR - {response.status_code}",
                "message": str(err)
            }
        }
        return result_data, response.status_code

