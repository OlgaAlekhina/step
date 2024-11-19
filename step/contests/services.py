import time
from datetime import datetime
from typing import Union, Tuple, List, Dict

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

process_participation_contest_id = settings.PROCESS_PARTICIPATION_CONTEST_ID

process_contests_id = settings.PROCESS_CONTESTS_ID
process_docontests_id = settings.PROCESS_DOCONTESTS_ID

status_id_rejection = settings.STATUS_ID_REJECTION

jwt_public_key = settings.ACCESS_TOKEN_PUBLIC_KEY
jwt_algorithm = settings.JWT_ALGORITHM

#   Статус конкурса
status_id_done = settings.STATUS_ID_DONE


#   расшифровывает JWT-токен, пришедший в заголовке авторизации
def get_user(token):
    public_key = jwt_public_key.replace("\\n", "\n").encode()
    try:
        payload = jwt.decode(token, public_key, jwt_algorithm)
        data = {
            'user_id': payload.get('sub').get('user_id', None),
            'profile_id': payload.get('sub').get('profile_id', None),
            'account_id': payload.get('sub').get('account_id', None)
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


#   проверяет статус заявки пользователя на участие в конкурсе
def get_application_status(token, contest_id, user_id):
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/rql/{node_id_default}"
    try:
        response = requests.post(url, headers=headers, json={
            "rql": f"process.id = '{process_docontests_id}' AND cf_konkurs_id = '{contest_id}' AND cf_userid = '{user_id}'",
            "fields": []})
        response_data = response.json().get('data', [])
        if response_data:
            status = response_data[0].get('status').get('name', None)
            if status in ('Новая', 'Одобрено'):
                return 'Решение не отправлено'
            elif status == 'Задание выполнено':
                return 'Решение отправлено'
        return None
    except:
        return None


def datetime_convert(date, format_date='%d.%m.%Y'):
    """Преобразование даты в заданный формат."""

    if date is None or not date:
        result = date
    else:
        result = datetime.fromisoformat(date.rstrip("Z") + "+00:00").strftime(format_date)
    return result


def get_condition(parameters_ids: Union[Tuple[str, ...], List[str], str, None], construction: str) -> str:
    """Вспомогательная функция для получения условия поиска в Raida."""
    if isinstance(parameters_ids, (tuple, list)):
        parameter_condition = f" {construction} IN {parameters_ids}"
    elif isinstance(parameters_ids, str):
        parameter_condition = f" {construction} = '{parameters_ids}'"
    else:
        parameter_condition = ""
    return parameter_condition


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


def get_contests(
        token: str,
        process_id: str,
        status_ids: Union[Tuple[str, ...], List[str], str, None],
        projects_ids: Union[Tuple[str, ...], List[str], str, None],
        message: str = "Список всех конкурсов/задач по заданному статусу или статусам"
) -> Tuple[Dict, int]:
    """Получение всех конкурсов по переданным параметрам."""
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/rql/{node_id_default}"

    try:

        status_condition = get_condition(
            parameters_ids=status_ids,
            construction='AND status.id'
        )

        # Если передавать name а не id
        # status_condition = get_condition(
        #     parameters_ids=status_ids,
        #     construction='AND status.name'
        # )

        project_condition = get_condition(
            parameters_ids=projects_ids,
            construction='AND cf_projects'
        )

        completed_contests = {
            "rql": f"process.id = '{process_id}'{status_condition}{project_condition}",
            "fields": [
                # "id",
                # "title",
                # "description",
                # "status.id",
                # "status.name",
                # "custom_fields.cf_deadline",
                # "custom_fields.cf_award",
                # "custom_fields.cf_brief",
                # "custom_fields.cf_konkurs_category",
                # "custom_fields.cf_projects",
                # "custom_fields.cf_profession",
            ]
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
                "message": message
            },
            "data": result_data,
            "info": {
                "api_version": "0.0.1",
                "count": len(result_data),
                # "compression_algorithm": "lossy"
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


def check_task(url: str, process_id: str, contest_id: str, user_id: str, headers: Dict) -> bool:
    """Функция для проверки есть ли у данного конкурса задача с текущим пользователем или нет."""
    tasks = {
        "rql": f"process.id = '{process_id}' AND cf_konkurs_id = '{contest_id}' AND cf_userid = '{user_id}' AND status.id != '{status_id_rejection}'"
    }
    response = requests.post(url, json=tasks, headers=headers)
    result = response.json().get('data', [])

    return bool(result)


def get_tasks(
        token: str,
        process_id: str,
        status_ids: Union[Tuple[str, ...], List[str], str, None],
        projects_ids: Union[Tuple[str, ...], List[str], str, None],
        user_id: str,
        message: str = "Список всех конкурсов/задач по заданному статусу или статусам"
) -> Tuple[Dict, int]:
    """Получение всех конкурсов по переданным параметрам для раздела мои задачи."""
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/rql/{node_id_default}"

    try:

        status_condition = get_condition(
            parameters_ids=status_ids,
            construction='AND status.id'
        )

        # Если передавать name а не id
        # status_condition = get_condition(
        #     parameters_ids=status_ids,
        #     construction='AND status.name'
        # )

        project_condition = get_condition(
            parameters_ids=projects_ids,
            construction='AND cf_projects'
        )

        completed_contests = {
            "rql": f"process.id = '{process_id}'{status_condition}{project_condition}",
            "fields": [
                # "id",
                # "title",
                # "description",
                # "status.id",
                # "status.name",
                # "custom_fields.cf_deadline",
                # "custom_fields.cf_award",
                # "custom_fields.cf_brief",
                # "custom_fields.cf_konkurs_category",
                # "custom_fields.cf_projects",
                # "custom_fields.cf_profession",
            ]
        }

        response = requests.post(url, json=completed_contests, headers=headers)
        response.raise_for_status()  # Это вызовет исключение для статусов 4xx и 5xx

        response_data = response.json().get('data', [])
        # result_data = response_data
        result_data = []
        for contest in response_data:

            task = check_task(
                url=url,
                process_id=process_participation_contest_id,
                contest_id=contest.get('id'),
                user_id=user_id,
                headers=headers
            )

            if task:
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
            else:
                continue

        result_data = {
            "detail": {
                "code": "OK",
                "message": message
            },
            "data": result_data,
            "info": {
                "api_version": "0.0.1",
                "count": len(result_data),
                # "compression_algorithm": "lossy"
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
