# Сервис для личного кабинета "Кловери Шаг" в рамках 9 потока.

<details>
<summary>

## Описание

</summary>

***Кловери.Шаг в будущем – полностью автоматизированная платформа для взаимодействия заказчика и исполнителя
с использованием механик геймификации***

</details>

___

<details>
<summary>

## Технологии

</summary>

### Backend

<img src="https://img.shields.io/badge/-DjangoRestFramework-464646?style=flat-square&logo=djangorestframework" alt="Django Rest Framework">
<img src="https://img.shields.io/badge/-Swagger-464646?style=flat-square&logo=swagger" alt="Swagger">

### Tools

<img src="https://img.shields.io/badge/-PyCharm-464646?style=flat-square&logo=git" alt="PyCharm">
<img src="https://img.shields.io/badge/-Git-464646?style=flat-square&logo=git" alt="Git">
<img src="https://img.shields.io/badge/-GitLab-464646?style=flat-square&logo=github" alt="GitLab">

### Containerization

<img src="https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=git" alt="Docker">
<img src="https://img.shields.io/badge/-DockerCompose-464646?style=flat-square&logo=git" alt="Docker Compose">
<img src="https://img.shields.io/badge/-Nginx-464646?style=flat-square&logo=github" alt="Nginx">

### QA

<img src="https://img.shields.io/badge/-Postman-464646?style=flat-square&logo=postman" alt="Postman">
<img src="https://img.shields.io/badge/-PyTest-464646?style=flat-square&logo=pytest" alt="PyTest">


[//]: # (### Backend)

[//]: # (![Django Rest Framework]&#40;https://img.shields.io/badge/-Django_Rest_Framework-090909?style=for-the-badge&logo=django&logoColor=17952c&#41;)

[//]: # ()

[//]: # (### Tools)

[//]: # (![PyCharm]&#40;https://img.shields.io/badge/-pycharm-090909?style=for-the-badge&logo=pycharm&logoColor=e9fd01&#41;)

[//]: # (![Git]&#40;https://img.shields.io/badge/-GIT-090909?style=for-the-badge&logo=git&logoColor=ff5169&#41;)

[//]: # (![GitLab]&#40;https://img.shields.io/badge/-GITLAB-090909?style=for-the-badge&logo=gitlab&logoColor=FFA500&#41;)

[//]: # ()

[//]: # (### Containerization)

[//]: # (![Docker]&#40;https://img.shields.io/badge/-Docker-090909?style=for-the-badge&logo=docker&logoColor=097CDB&#41;)

[//]: # (![Docker Compose]&#40;https://img.shields.io/badge/-Docker_compose-090909?style=for-the-badge&logo=docker&logoColor=097CDB&#41;)

[//]: # (![Nginx]&#40;https://img.shields.io/badge/-Nginx-090909?style=for-the-badge&logo=Nginx&logoColor=00FF00&#41;)

[//]: # ()

[//]: # (### QA)

[//]: # (![Postman]&#40;https://img.shields.io/badge/-Postman-090909?style=for-the-badge&logo=postman&logoColor=#FF7F00&#41;)

[//]: # (![Pytest]&#40;https://img.shields.io/badge/-Pytest-090909?style=for-the-badge&logo=pytest&logoColor=#FF7F00&#41;)

</details>

___

<details>
<summary>

## Как запустить проект на своем локальном сервере через IDE PyCharm

</summary>

### 1. Клонирование репозитория

```
git clone https://git.infra.cloveri.com/cloveri.start/step/step_latest.git
```

### 2. Создание виртуального окружения

```
python -m venv venv - для Windows
sudo apt-get install -y python3-venv - для Linux
```

### 3. Активирование виртуального окружение

```
venv\scripts\activate  - для Windows
venv/bin/activate - для Linux
```

### 4. Установка переменных окружения

***В корне проекта заполняем файл .env.example и переименовываем его в .env или просто создаём файл .env и
заполняем его.***

```
SECRET_KEY='секретный ключ'
DEBUG=0

DJANGO_ALLOWED_HOSTS=api.step.skroy.ru 127.0.0.1
DJANGO_CORS_ALLOWED_ORIGINS=http://127.0.0.1:3000 https://step.skroy.ru

BASE_URL=https://api.beta.raida-dev.ru
USER_RAIDA=лоин райды
PASSWD_RAIDA=пароль райды
NODE_ID=4fc9986b-d03b-4801-a672-a191c941e17c

# TOKEN
ACCESS_TOKEN_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAwwP2xW8sTF63kyi75Esy\nJd5+ENBZifoOwFz5JTjXRP0yg/feRIR1F3EJ3NMQy7uXXuTCL09wAKBcqxjilXhS\nXLNpBFOZV2ESs3vqAwLL/xN25QWQMUzvCWwVcU3CKrIgDTtcYeyj0xnGjpO9cB8W\nBdtkloxOAXjZaqQ8WLLHtkp2bc34kp4vivFwR8o21v2oeVsINH0eb5Ci8jCDKs6U\nh4Yml6EsRAlKVMJYOsgWm3J9TkbKCvpgl5XcTYCyVdQMRlcmFyF2mG90nyo0tv13\n6oxqGPP7GKozYWIQ1wAprhWPYf13m8/Agvw5bLJknybUO77rVaVM+hq4ASXNMY+j\nyhFfO/OYPZOkfLdmu1UhbIXwy1cHWbk9F6MWPF7fgU/mNVgUlibmUh+zEqdjB/Hx\nCfQPnKFEmmsQhZiLMfcEOY15OTnm9UoM8K0xZQpCM4Hj6v/LVeQnyddeudIgAa0H\nEBH0AqEynXBiJUPDMlp17rJLQsWh03fmTq8W+t41sVk8N1MXJ8dndix7JrRYI9Zx\nMR6aNehyXLCxZfw7Hpr8J5AeMNEBMogkQo83hE0DNURcr/l09pYDu4kxhuzSc1DV\nLKFYpt7G4ZxVDjYY6v8045y5UBdge4KovZjagSmOK/rraWTRyNtPSqqrH0YIlSWi\nCn5sN6gYwyFEYl3uUiTBJScCAwEAAQ==\n-----END PUBLIC KEY-----

JWT_ALGORITHM=RS256


# ID Конкурсов
PROCESS_CONTESTS_ID ='9e57ac56-9ce8-43fe-a725-d6eb6cb3758b'
PROCESS_PARTICIPATION_CONTEST_ID ='eb63f559-62b1-4666-94a4-2ecdc928bdef'
PROCESS_DOCONTESTS_ID=eb63f559-62b1-4666-94a4-2ecdc928bdef

# ID Статусов конкурса
STATUS_ID_NEW='fe5c453a-0249-4b22-980e-c66a76ad78a9'
STATUS_ID_REJECTION='678228a5-cade-451e-bd76-33df0e0875e9'
STATUS_ID_SUM_RESULTS='ab7d8f83-386e-4613-a062-99162356e7ad'
STATUS_ID_VOTING='a1b783c5-2dad-4338-98a8-0a6dfdb74f02'
STATUS_ID_ACCEPTANCE_WORKS='090e4125-f716-4427-a0a2-3e8e4655ae4d'
STATUS_ID_DONE='6c419c06-06fd-43c3-85ee-2f58110db712'
STATUS_ID_ACCEPTANCE_WORKS_DONE='0db1196c-c03f-4d5b-a422-f15a94f7dba4'
STATUS_ID_NO_WINNER='2267301e-6b6b-4f67-9e8d-65d2c6c9c05e'

# ID Статусов участия в конкурсе
STATUS_ID_TASK_COMPLETED='b9d7d6d4-e22e-4aa1-bf2d-35cdfcb94a2d'

STEP_SERVICE_MAIN_PORT=8001
STEP_SERVICE_MAIN_IMAGE=docker.infra.cloveri.com/cloveri.start/step/step/stage:latest

LANGUAGE_CODE=ru
TIME_ZONE=Europe/Moscow

```

### 5. Установка зависимостей

```
pip install -r requirements.txt
```

### 6. Запуск сервиса

```
python manage.py runserver
```

</details>

___

<details>
<summary>

## Команда Кловери Шаг 9 поток

</summary>

| № | ФИО                | Должность           | Никнейм в телеграмме | Ссылка на проекты               |
|---|--------------------|---------------------|----------------------|---------------------------------|
| 1 | Филипенко Виктория | Заказчик, дизайнер  | @up2fika             |                                 |
| 2 | Зайцев Антон       | Backend разработчик | @BlackMarvel         | https://github.com/Hashtagich   |
| 3 | Алехина Ольга      | Backend разработчик | @olik_al             | https://github.com/OlgaAlekhina |
| 4 | Спащенко Регина    | QA                  | @Sp_R_G              | https://github.com/SpaRegina    |

</details>

___

## Urls и API

***Страница с документацией по API***

<code>/docs/</code>

***API для вкладок/разделов личного кабинета Кловери Шаг (Конкурсы)***
<details>
<summary><code>GET/contests/{contest_id}/</code></summary>

*Получение данных конкретного конкурса по его id*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "data": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "string",
    "description": "string",
    "created_at": "2024-12-04",
    "status_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "status_name": "string",
    "deadline": "2024-12-04",
    "award": "string",
    "profession": "string",
    "category": "string",
    "attachments": {
      "id": "string",
      "name": "string"
    }
  },
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>

<details>
<summary><code>GET/contests/active/</code></summary>

*Получение списка всех конкурсов со статусом Прием работ. Вкладка/раздел Активные конкурсы.*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "data": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "description": "string",
      "status": "string",
      "deadline": "2024-12-05",
      "award": "string",
      "brief": "string",
      "title": "string",
      "konkurs_category": "string"
    }
  ],
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>


<details>
<summary><code>GET/contests/archive/</code></summary>

*Получение списка всех конкурсов со статусом Завершен и Победитель не выбран. Вкладка/раздел Архив конкурсов.*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "data": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "description": "string",
      "status": "string",
      "deadline": "2024-12-05",
      "award": "string",
      "brief": "string",
      "title": "string",
      "konkurs_category": "string"
    }
  ],
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>


<details>
<summary><code>GET/contests/user/my/history/</code></summary>

*Получение списка всех завершенных конкурсов, где пользователя участвовал. Вкладка/раздел История участия.*

```
{
  "detail": {
    "code": "OK",
    "message": "Получение списка всех конкурсов со статусом Завершен. Для раздела история участия."
  },
  "data": [
    {
      "id": "e2ccc043-2558-4bd1-872e-4df6cf7b5256",
      "title": "Супер-конкурс",
      "created_at": "06 November 2024",
      "deadline": "28 November 2024",
      "solution_link": "test_link",
      "attachments": {
        "id": "ce063f59-e352-4da9-939f-253644619eb4",
        "name": "f6e3f9a9-79ea-4859-82ea-b1721bff0c70-cat.jpg",
        "url": "media/4fc9986b-d03b-4801-a672-a191c941e17c/f6e3f9a9-79ea-4859-82ea-b1721bff0c70-cat.jpg",
        "content_type": "image/jpeg"
      }
    }
  ],
  "info": {
    "api_version": "0.0.1",
    "count": 1
  }
}
```

</details>

<details>
<summary><code>GET/contests/user/{user_id}/history/</code></summary>

*Получение списка всех завершенных конкурсов конкретного участника, где тот участвовал.*

```
{
  "detail": {
    "code": "OK",
    "message": "Получение списка всех конкурсов со статусом Завершен. Для раздела история участия."
  },
  "data": [
    {
      "id": "e2ccc043-2558-4bd1-872e-4df6cf7b5256",
      "title": "Супер-конкурс",
      "created_at": "06 November 2024",
      "deadline": "28 November 2024",
      "solution_link": "test_link",
      "attachments": {
        "id": "ce063f59-e352-4da9-939f-253644619eb4",
        "name": "f6e3f9a9-79ea-4859-82ea-b1721bff0c70-cat.jpg",
        "url": "media/4fc9986b-d03b-4801-a672-a191c941e17c/f6e3f9a9-79ea-4859-82ea-b1721bff0c70-cat.jpg",
        "content_type": "image/jpeg"
      }
    }
  ],
  "info": {
    "api_version": "0.0.1",
    "count": 1
  }
}
```

</details>


<details>
<summary><code>GET/contests/user/my/tasks/</code></summary>

*Получение списка всех заданий пользователя. Вкладка/раздел Мои задания.*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "data": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "string",
      "description": "string",
      "status_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "status_name": "string",
      "deadline": "2024-12-11",
      "award": "string",
      "brief": "string",
      "profession": "string",
      "projects": "string",
      "konkurs_category": "string",
      "application_status": {
        "application_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "application_status": {
          "code": "string",
          "message": "string"
        },
        "solution_link": "string"
      }
    }
  ],
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>

<details>
<summary><code>POST/contests/user/my/task/</code></summary>

*Создание задачи для участия в конкурсе*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "data": {
    "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "status": "string",
    "contest_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  },
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>

<details>
<summary><code>DELETE/contests/user/my/task/{task_id}/</code></summary>

*Отказ от участия в конкурсе: изменение статуса заявки на 'Отказ'*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>

___

<details>
<summary>

## Дополнительная информация

</summary>

+ ***Дизайн в Figma — https://www.figma.com/design/3r9HwWIEHWElYElRLtc8Gq/ЛК-Кловери.Шаг?node-id=0-1***
+ ***Документация по стажировке 9 потока — https://drive.google.com/drive/folders/1xQej-LEGexAl7P4fzTCJnw2Gl4MeS1T-***

</details>