import os
import pytest
import requests
from django.conf import settings

from dotenv import load_dotenv

load_dotenv()

settings.configure()

BASE_URL = "http://127.0.0.1:8000" #"https://step.skroy.ru"
BASE_URL_1 = os.getenv('BASE_URL_UC')
USERNAME = os.getenv('USER_UC')
PASSWORD = os.getenv('PASSWORD_UC')
PROJECT_ID = os.getenv('PROJECT_ID_UC')

@pytest.fixture
def get_bearer_token():
    """
    Фикстура для получения Bearer Token.
    """
    url = f"{BASE_URL_1}/auth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Project-ID": PROJECT_ID
    }
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()

    return response.json()["access_token"]

def test_get_user_history_with_valid_token(get_bearer_token):
    url = f"{BASE_URL}/api/contests/user_history/"
    headers = {
        "Authorization": f"Bearer {get_bearer_token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == 200, "Не удалось получить список истории с валидным токеном"

def test_get_user_history_with_invalid_token():
    invalid_token = "invalid_token"
    url = f"{BASE_URL}/api/contests/user_history/"
    headers = {
        "Authorization": f"Bearer {invalid_token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == 403, "Статус ответа не соответствует при невалидном токене"
    response_json = response.json()
    assert response_json["detail"]["code"] == "TOKEN_INCORRECT", "Код ошибки не соответствует неправильному токену"
    assert response_json["detail"]["message"] == "Некорректный токен", "Сообщение об ошибке не соответствует"

def test_get_user_history_without_token():
    """
    Тест: Получение списка истории без Bearer Token.
    """
    url = f"{BASE_URL}/api/contests/user_history/"
    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == 403, "Статус ответа не соответствует при отсутствии токена"
    response_json = response.json()
    assert response_json.get("detail") == "Учетные данные не были предоставлены.", "Сообщение об ошибке не соответствует отсутствию токена"

def test_get_user_history_with_empty_token():
    empty_token = ""
    url = f"{BASE_URL}/api/contests/user_history/"
    headers = {
        "Authorization": f"Bearer {empty_token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == 403, "Статус ответа не соответствует при пустом токене"
    response_json = response.json()
    assert response_json["detail"]["code"] == "TOKEN_INCORRECT", "Код ошибки не соответствует отсутствию токена"

def test_post_request_instead_of_get(get_bearer_token):
    url = f"{BASE_URL}/api/contests/user_history/"
    headers = {
        "Authorization": f"Bearer {get_bearer_token}",
        "Accept": "application/json"
    }

    response = requests.post(url, headers=headers)
    assert response.status_code == 405, "Статус ответа не соответствует при использовании POST вместо GET"

def test_expired_token():
    """
    Тест: Проверка истечения срока действия токена.
    """
    expired_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOnsidXNlcl9pZCI6IjIwOTg2MTFkLTMyZTItNGQ4Zi1hY2VhLTc2NTcwYWY2NTg0MyIsImRldmljZV9pZCI6ImRldmljZV9pZCAod2lwKSIsInVzZXJfaXAiOiJ1c2VyX2lwICh3aXApIiwicHJvZmlsZV9pZCI6IjIwOTg2MTFkLTMyZTItNGQ4Zi1hY2VhLTc2NTcwYWY2NTg0MyIsImFjY291bnRfaWQiOm51bGx9LCJpYXQiOjE3MzIxNzc4MjMsImV4cCI6MTczMjIyMTAyM30.oRILy1DE..."
    url = f"{BASE_URL}/api/contests/user_history/"
    headers = {
        "Authorization": f"Bearer {expired_token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == 403, "Статус ответа не соответствует при истечении срока действия токена"
    response_json = response.json()
    assert response_json["detail"]["code"] == "TOKEN_INCORRECT", "Код ошибки не соответствует истечению срока действия токена"
    assert response_json["detail"]["message"] == "Некорректный токен", "Сообщение об истечении срока действия токена не соответствует"