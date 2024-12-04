import pytest
import requests

BASE_URL = "http://127.0.0.1:8000" #"https://step.skroy.ru"

@pytest.mark.parametrize("method, url, expected_status_code, expected_message", [
    ("GET", f"{BASE_URL}/api/contests/archive/", 200, None),  # Успешное получение списка всех конкурсов
    ("GET", f"{BASE_URL}/api/contests/archive_/", 404, "Page not found"),  # Некорректный URL
    ("POST", f"{BASE_URL}/api/contests/archive/", 405, "Метод \"POST\" не разрешен.")  # Неверный HTTP метод
])
def test_active_contests(method, url, expected_status_code, expected_message):
    """
    Test /api/contests/active/ endpoint with different scenarios.
    """
    if method == "GET":
        response = requests.get(url, headers={"Accept": "application/json"})
    elif method == "POST":
        response = requests.post(url, headers={"Accept": "application/json"})
    else:
        pytest.fail("Unsupported HTTP method")

    assert response.status_code == expected_status_code

    if expected_message:
        # Проверка, является ли контент JSON-ответом
        if "application/json" in response.headers.get("Content-Type", ""):
            response_json = response.json()
            assert expected_message == response_json.get("detail", "")
        else:
            # Если ответ не в формате JSON, проверяем его текст
            assert expected_message in response.text
