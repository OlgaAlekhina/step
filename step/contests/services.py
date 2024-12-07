import time
from datetime import datetime
from typing import Union, Tuple, List, Dict

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
status_id_task_completed = settings.STATUS_ID_TASK_COMPLETED
status_id_task_new = settings.STATUS_ID_TASK_NEW

jwt_public_key = settings.ACCESS_TOKEN_PUBLIC_KEY
jwt_algorithm = settings.JWT_ALGORITHM

#   Статус конкурса
status_id_done = settings.STATUS_ID_DONE


def get_token():
    """
    Получить или обновить токен доступа для аутентификации пользователя.

    Эта функция использует кэш для хранения токена доступа и времени его последнего обновления.
    Если токен отсутствует или срок его действия истек (более 1 часа с последнего обновления),
    функция выполняет запрос на получение нового токена. В противном случае возвращает
    текущий токен из кэша.
    """
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


def get_user_task(token: str, contest_id: str, user_id: str) -> dict:
    """
    Проверка статуса заявки пользователя на участие в конкурсе.
    Эта функция отправляет POST-запрос к API для получения статуса заявки пользователя на участие в указанном конкурсе.
    Она проверяет наличие заявки и ее статус, возвращая соответствующий код и сообщение.
    """
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/rql/{node_id_default}"
    try:
        response = requests.post(url, headers=headers, json={
            "rql": f"process.id = '{process_docontests_id}' AND cf_konkurs_id = '{contest_id}' AND cf_userid = '{user_id}'",
            "fields": []})
        response_data = response.json().get('data', [])
        if response_data:
            for response in response_data:
                status = response.get('status').get('name', None)
                if status == 'Задание выполнено':
                    task_status = {'code': 'TASK_COMPLETED', 'message': 'Решение отправлено'}
                    user_task = response.get('id', None)
                    break
                elif status in ('Новая', 'Одобрена'):
                    task_status = {'code': 'TASK_UNCOMPLETED', 'message': 'Решение не отправлено'}
                    user_task = response.get('id', None)
                    break
            else:
                user_task = None
                task_status = {'code': 'TASK_DOES_NOT_EXIST', 'message': 'Нет заявки на участие'}
        else:
            user_task = None
            task_status = {'code': 'TASK_DOES_NOT_EXIST', 'message': 'Нет заявки на участие'}
        return {
            'user_task': user_task,
            'task_status': task_status
        }

    except requests.exceptions.HTTPError as err:
        return {'code': 'HTTP_ERROR', 'message': f'Ошибка HTTP: {str(err)}'}

    except requests.exceptions.RequestException as err:
        return {'code': 'REQUEST_ERROR', 'message': f'Ошибка запроса: {str(err)}'}

    except ValueError as err:
        return {'code': 'VALUE_ERROR', 'message': f'Ошибка обработки данных: {str(err)}'}

    except Exception as err:
        return {'code': 'NOT_DEFINED', 'message': f'Не определен: {str(err)}'}


def datetime_convert(date, format_date='%d.%m.%Y') -> str | None:
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


def get_contest(token: str, contest_id: str) -> Tuple[Dict, int] | list:
    """Получение данных одного конкурса по его id."""
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/{node_id_default}/{contest_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
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


def patch_task(token: str, task_id: str) -> Tuple[Dict, int] | None:
    """Изменение статуса заявки на участие в конкурсе на 'Отказ'."""
    access_token = token
    # проверяем, что есть такая заявка на участие в конкурсе
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/{node_id_default}/{task_id}"
    try:
        response = requests.get(url, headers=headers)
        response_data = response.json().get('data', [])
        # Если заявка есть, меняем статус
        if response_data and response_data.get('process').get('name') == 'Участие в конкурсе':
            headers = {"Authorization": f'Bearer {access_token}'}
            url = f"{base_url}/api/tasks/{node_id_default}/{task_id}"
            data = {"status_id": status_id_rejection}
            try:
                response = requests.patch(url, headers=headers, json=data)
                response.raise_for_status()
                response_data = response.json().get('data', [])
                if response_data:
                    result_data = {
                        "detail": {
                            "code": "OK",
                            "message": "Статус заявки изменен на 'Отказ'"
                        },
                        "info": {
                            "api_version": "0.0.1",
                            # "compression_algorithm": "lossy"
                        }
                    }
                    return result_data, response.status_code
                return None

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
        return None
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


def contest_exists(token: str, contest_id: str) -> bool:
    """Проверяет, существует ли конкурс с данным contest_id"""
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/{node_id_default}/{contest_id}"
    response = requests.get(url, headers=headers)
    response_data = response.json().get('data', [])
    if response_data and response_data.get('process').get('name') == 'Конкурс':
        return True
    return False


def create_task(token, contest_id, user_id):
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/tasks/{node_id_default}/{process_docontests_id}"
    task = {
            "title": "",
            "description": "",
            "author": None,
            "assignee": None,
            "status_id": status_id_task_new,
            "custom_fields": {
                            "cf_konkurs_link": "",
                            "cf_award": "",
                            "cf_brief": "",
                            "cf_startdate": "",
                            "cf_konkurs_category": "",
                            "cf_konkurs_id": str(contest_id),
                            "cf_userid": user_id
                        }
    }
    try:
        response = requests.post(url, json=task, headers=headers)
        response_data = response.json().get('data')
        result_data = {
            "task_id": response_data.get('id', None),
            "status": "Новая",
            "contest_id": contest_id,
            "user_id": user_id
        }
        return {
            "detail": {
                "code": "OK",
                "message": "Задача создана"
            },
            "data": result_data,
            "info": {
                "api_version": "0.0.1",
                # "compression_algorithm": "lossy"
            }
        }

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
        response.raise_for_status()

        response_data = response.json().get('data', [])
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
                    'description': contest.get('description', None),
                    'status_id': status_id,
                    'status_name': status_name,
                    'deadline': datetime_convert(cf_deadline),
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


def check_task(
        url: str,
        process_id: str,
        contest_id: str,
        user_id: str,
        status_condition: str,
        headers: Dict
) -> Union[Dict, None]:
    """Функция для проверки есть ли у данного конкурса задача с текущим пользователем или нет."""
    tasks = {
        "rql": f"process.id = '{process_id}' AND cf_konkurs_id = '{contest_id}' AND cf_userid = '{user_id}' {status_condition}"
    }
    response = requests.post(url, json=tasks, headers=headers)
    result = response.json().get('data', [])
    if result:
        status = result[0].get('status').get('name', None)
        application_id = result[0].get('id', None)
        solution_link = result[0].get('custom_fields').get('cf_konkurs_link', None)
        if status == 'Задание выполнено':
            application_status = {'code': 'TASK_COMPLETED', 'message': 'Решение отправлено'}
        else:
            application_status = {'code': 'TASK_UNCOMPLETED', 'message': 'Решение не отправлено'}
        return {
            'application_id': application_id,
            'application_status': application_status,
            'solution_link': solution_link
        }

    return None


def get_attachments(token: str, task_id: str) -> dict | None:
    """Функция для получения загруженных данных к задаче."""
    access_token = token
    headers = {"Authorization": f'Bearer {access_token}'}
    url = f"{base_url}/api/attachments/{node_id_default}/{task_id}"
    response = requests.get(url, headers=headers)
    response_data = response.json().get('data', [])
    if response_data:
        return {
            "id": response_data[0].get('id'),
            "name": response_data[0].get('name'),
            "url": response_data[0].get('url'),
            "content_type": response_data[0].get('content_type'),
        }
    return None


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
                status_condition=f"AND status.id != '{status_id_rejection}'",
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
                        'application_status': task.get('application_status'),

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


def get_history(
        token: str,
        process_id: str,
        status_ids: Union[Tuple[str, ...], List[str], str, None],
        projects_ids: Union[Tuple[str, ...], List[str], str, None],
        user_id: str,
        message: str = "Список всех конкурсов/задач по заданному статусу или статусам"
) -> Tuple[Dict, int]:
    """Получение всех конкурсов, где участвовал пользователь и загрузил решение."""
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
                # "custom_fields.cf_deadline",
            ]
        }

        response = requests.post(url, json=completed_contests, headers=headers)
        response.raise_for_status()  # Это вызовет исключение для статусов 4xx и 5xx

        response_data = response.json().get('data', [])
        result_data = []

        for contest in response_data:

            task = check_task(
                url=url,
                process_id=process_participation_contest_id,
                contest_id=contest.get('id'),
                user_id=user_id,
                status_condition=f"AND status.name = 'Задание выполнено'",
                # f"AND status.id = '{status_id_task_completed}'",
                headers=headers
            )

            if task:

                custom_fields = contest.get('custom_fields', {})
                cf_deadline = custom_fields.get('cf_deadline')
                application_id = task.get('application_id')
                attachments = get_attachments(token, application_id)

                result_data.append(  # contest)
                    {
                        'id': contest.get('id', None),
                        'title': contest.get('title', None),
                        'created_at': datetime_convert(contest.get('created_at', None), format_date='%d %B %Y'),
                        'deadline': datetime_convert(cf_deadline, format_date='%d %B %Y'),
                        'solution_link': task.get('solution_link'),
                        'attachments': attachments,
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
