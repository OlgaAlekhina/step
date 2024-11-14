import time
from datetime import datetime

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

import requests
from django.conf import settings
from requests.exceptions import RequestException, HTTPError
from .serializers import ContestsSerializer

token_cache = {'access_token': None, 'last_update': 0}

base_url = settings.BASE_URL
username = settings.USERNAME
password = settings.PASSWORD
node_id_default = settings.NODE_ID

process_contests_id = settings.PROCESS_CONTESTS_ID

jwt_public_key = settings.ACCESS_TOKEN_PUBLIC_KEY
jwt_algorithm = settings.JWT_ALGORITHM

#   Статус конкурса
status_id_done = settings.STATUS_ID_DONE


def get_user(token):
    public_key = jwt_public_key.replace("\\n", "\n").encode()
    try:
        payload = jwt.decode(token, public_key, jwt_algorithm)
        data = {
            'user_id': payload.get('user_id', None),
            'profile_id': payload.get('profile_id', None),
            'account_id': payload.get('account_id', None)
        }
        return data, 200
    except ExpiredSignatureError:
        data = {
            "detail": {
                "code": "TOKEN_EXPIRED",
                "message": "Токен устарел"
            }
        }
        return data, 401
    except InvalidTokenError as e:
        data = {
            "detail": {
                "code": "TOKEN_INCORRECT",
                "message": "Некорректный токен"
            }
        }
        return data, 401


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


def get_application_status(token, contest_id, user_id):
    return 'Test'


def datetime_convert(date, format_date='%d.%m.%Y'):
    """Преобразование даты в заданный формат."""

    if date is None or not date:
        result = date
    else:
        result = datetime.fromisoformat(date.rstrip("Z") + "+00:00").strftime(format_date)
    return result


def get_condition(parameters_ids, construction):
    if parameters_ids:
        formatted_parameter_ids = "', '".join(parameters_ids)

        parameter_condition = f" {construction}('{formatted_parameter_ids}')"
    else:
        parameter_condition = ""
    return parameter_condition


def get_archive_contests(token):
    """Получение всех конкурсов со статусом завершен. Реализация функционала Архив конкурсов."""
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/rql/{node_id_default}"

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
    url = f"{base_url}/api/tasks/{node_id_default}/{contest_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Это вызовет исключение для статусов 4xx и 5xx
        response_data = response.json().get('data', [])
        if not response_data:
            return []
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


def get_contests(token, process_id, status_ids, projects_ids):
    """Получение всех конкурсов по переданным параметрам."""
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/rql/{node_id_default}"

    try:

        status_condition = get_condition(
            parameters_ids=status_ids,
            construction='AND status.id IN '
        )
        project_condition = get_condition(
            parameters_ids=projects_ids,
            construction='AND custom_fields.cf_projects IN '
        )

        completed_contests = {
            "rql": f"process.id = '{process_id}'{status_condition}{project_condition}"
            #     "fields": [
            #         "id",
            #         "title",
            #         "description",
            #         "status.id",
            #         "status.name",
            #         "custom_fields.cf_deadline",
            #         "custom_fields.cf_award",
            #         "custom_fields.cf_brief",
            #         "custom_fields.cf_konkurs_category",
            #         "custom_fields.cf_projects",
            #         "custom_fields.cf_profession",
            #     ]
        }

        response = requests.post(url, json=completed_contests, headers=headers)
        response.raise_for_status()  # Это вызовет исключение для статусов 4xx и 5xx

        response_data = response.json().get('data', [])
        # result_data = response_data
        result_data = []
        for contest in response_data:
            status_name = contest['status'].get('name', None) if contest.get('status', None) is not None else None
            status_id = contest['status'].get('id', None) if contest.get('status', None) is not None else None

            custom_fields = contest.get('custom_fields', {})
            cf_deadline = custom_fields.get('cf_deadline')
            cf_award = custom_fields.get('cf_award')
            cf_brief = custom_fields.get('cf_brief')
            cf_profession = custom_fields.get('cf_profession')
            cf_projects = custom_fields.get('cf_projects')
            cf_konkurs_category = custom_fields.get('cf_konkurs_category')

            result_data.append(
                {
                    'id': contest.get('id', None),
                    'title': contest.get('title', None),
                    'description': contest.get('description', None),  # под вопросом
                    'status_id': status_id,  # под вопросом
                    'status_name': status_name,
                    'deadline': datetime_convert(cf_deadline),  # под вопросом
                    'award': cf_award,
                    'brief': cf_brief,
                    'profession': cf_profession,
                    'projects': cf_projects,
                    'konkurs_category': cf_konkurs_category,

                }
            )

        result_data = {
            "detail": {
                "code": "OK",
                "message": "Список всех конкурсов/задач по заданному статусу или статусам"
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
