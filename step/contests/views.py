from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer, OpenApiParameter
from rest_framework import status, permissions, serializers
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (GetArchiveSerializer, ErrorResponseSerializer, ContestDetailsResponseSerializer,
                          QuitContestSerializer, CreateTaskSerializer, TaskResponseSerializer, QueryParamsSerializer,
                          GetContestTasksListSerializer, GetUserTasksListSerializer, GetUserHistoryListSerializer,
                          HeadersSerializer, SolutionSerializer, DetailSerializer)
from .services import (get_token, get_contest, get_contests, get_user_task, get_tasks, delete_task,
                       get_history, contest_exists, create_task, get_contest_tasks, get_configs, task_solution_status,
                       post_attachments, patch_task)


class BaseContestView(APIView):
    """Родительский класс для исключения дублирования кода в части документация swagger."""

    COMMON_RESPONSES = {
        400: OpenApiResponse(
            description="Ошибка клиента при запросе данных",
            response=ErrorResponseSerializer()
        ),
        401: OpenApiResponse(
            description="Необходима аутентификация",
            response=ErrorResponseSerializer()
        ),
        403: OpenApiResponse(
            description="Доступ запрещён",
            response=ErrorResponseSerializer()
        ),
        404: OpenApiResponse(
            description="Не найдено",
            response=ErrorResponseSerializer()
        ),
        500: OpenApiResponse(
            description="Ошибка сервера при обработке запроса",
            response=ErrorResponseSerializer()
        ),
    }


class ArchiveContestsView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Получение списка архивных конкурсов",
        description="Получение списка всех конкурсов со статусом Завершен и Победитель не выбран. Архив конкурсов.",
        parameters=[
            OpenApiParameter('Project-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER, required=True),
            OpenApiParameter('Account-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER)
        ],
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=GetArchiveSerializer()
            ),
            **BaseContestView.COMMON_RESPONSES
        },
        tags=['Contests'],
    )
    def get(self, request):
        access_token = get_token()
        project_id = request.META.get('HTTP_PROJECT_ID') if request.META.get('HTTP_PROJECT_ID') else None
        account_id = request.META.get('HTTP_ACCOUNT_ID') if request.META.get('HTTP_ACCOUNT_ID') else None
        serializer = HeadersSerializer(data={'project_id': project_id, 'account_id': account_id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        auth_token = request.META.get('HTTP_AUTHORIZATION')
        configs = get_configs(
            project_id=project_id,
            account_id=account_id,
            auth_token=auth_token,
            configs=['node_id', 'contest_process_id', 'contest_status_id']
        )
        if configs[1] == 200:
            configs = configs[0]
            node_id = configs.get('data').get('node_id').get('value')
            contest_process_id = configs.get('data').get('contest_process_id').get('value')
            status_id_done = configs.get('data').get('contest_status_id').get('done')
            status_id_no_winner = configs.get('data').get('contest_status_id').get('no_winner')
        elif configs[1] == 400:
            return Response(
                {'detail': dict(code='INCORRECT_CREDENTIALS', message='Неправильно введены учетные данные.')},
                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(
                {'detail': dict(code='INTERNAL_SERVER_ERROR', message='Внутренняя ошибка в работе сервиса конфигов.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        result_data = get_contests(
            token=access_token,
            node_id=node_id,
            process_id=contest_process_id,
            status_ids=(status_id_done, status_id_no_winner),
            projects_ids=None,
            message="Получение списка всех конкурсов со статусом Завершен и Победитель не выбран. Архив конкурсов."
        )

        return Response(result_data[0], status=result_data[1])


class ActiveContestsView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Получение списка активных конкурсов",
        description="Получение списка всех конкурсов со статусом Прием работ. Активные конкурсы.",
        parameters=[
            OpenApiParameter('Project-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER, required=True),
            OpenApiParameter('Account-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER)
        ],
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=GetArchiveSerializer()
            ),
            **BaseContestView.COMMON_RESPONSES
        },
        tags=['Contests'],
    )
    def get(self, request):
        access_token = get_token()
        project_id = request.META.get('HTTP_PROJECT_ID') if request.META.get('HTTP_PROJECT_ID') else None
        account_id = request.META.get('HTTP_ACCOUNT_ID') if request.META.get('HTTP_ACCOUNT_ID') else None
        serializer = HeadersSerializer(data={'project_id': project_id, 'account_id': account_id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        auth_token = request.META.get('HTTP_AUTHORIZATION')
        configs = get_configs(
            project_id=project_id,
            account_id=account_id,
            auth_token=auth_token,
            configs=['node_id', 'contest_process_id', 'contest_status_id']
        )
        if configs[1] == 200:
            configs = configs[0]
            node_id = configs.get('data').get('node_id').get('value')
            contest_process_id = configs.get('data').get('contest_process_id').get('value')
            status_id_acceptance_works = configs.get('data').get('contest_status_id').get('acceptance_works')
        elif configs[1] == 400:
            return Response(
                {'detail': dict(code='INCORRECT_CREDENTIALS', message='Неправильно введены учетные данные.')},
                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(
                {'detail': dict(code='INTERNAL_SERVER_ERROR', message='Внутренняя ошибка в работе сервиса конфигов.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        result_data = get_contests(
            token=access_token,
            node_id=node_id,
            process_id=contest_process_id,
            status_ids=status_id_acceptance_works,
            projects_ids=None,
            message="Получение списка всех конкурсов со статусом Прием работ. Активные конкурсы."
        )
        return Response(result_data[0], status=result_data[1])


class ContestDetailsView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Получение конкретного конкурса",
        description="Получение данных одного конкурса по его id",
        parameters=[
            OpenApiParameter('Project-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER, required=True),
            OpenApiParameter('Account-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER)
        ],
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=ContestDetailsResponseSerializer()
            ),
            **BaseContestView.COMMON_RESPONSES
        },
        tags=['Contests']
    )
    def get(self, request, contest_id):
        # получаем токен для доступа к Райде
        access_token = get_token()
        project_id = request.META.get('HTTP_PROJECT_ID') if request.META.get('HTTP_PROJECT_ID') else None
        account_id = request.META.get('HTTP_ACCOUNT_ID') if request.META.get('HTTP_ACCOUNT_ID') else None
        # валидируем заголовки
        serializer = HeadersSerializer(data={'project_id': project_id, 'account_id': account_id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        # получаем токен из заголовков для авторизации в сервисе конфигов
        auth_token = request.META.get('HTTP_AUTHORIZATION')
        # получаем конфиги из сервиса конфигов
        configs = get_configs(
            project_id=project_id,
            account_id=account_id,
            auth_token=auth_token,
            configs=['task_process_id', 'node_id', 'task_status_id', 'contest_process_id']
        )
        if configs[1] == 200:
            configs = configs[0]
            task_process_id = configs.get('data').get('task_process_id').get('value')
            contest_process_id = configs.get('data').get('contest_process_id').get('value')
            node_id = configs.get('data').get('node_id').get('value')
            task_status_id = configs.get('data').get('task_status_id')
        elif configs[1] == 400:
            return Response(
                {'detail': dict(code='INCORRECT_CREDENTIALS', message='Неправильно введены учетные данные.')},
                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(
                {'detail': dict(code='INTERNAL_SERVER_ERROR', message='Внутренняя ошибка в работе сервиса конфигов.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # проверяем, существует ли такой конкурс
        if not contest_exists(access_token, contest_id, node_id, contest_process_id):
            return Response({'detail': dict(code='NOT_FOUND', message='Конкурс не найден.')},
                            status=status.HTTP_404_NOT_FOUND)
        # получаем id пользователя из объекта Request
        user_id = request.auth.get('user_id')
        # получаем id заявки пользователя на участие в конкурсе, если она есть, и ее статус (отправлено решение или нет)
        result = get_user_task(access_token, contest_id, user_id, task_process_id, node_id, task_status_id)
        user_data = {'user_task_id': result.get('user_task'), 'user_task_status': result.get('task_status')}
        contest_data = get_contest(access_token, contest_id, node_id)
        response_data = contest_data[0]
        if contest_data[1] == 200:
            response_data['data'].update(user_data)
        return Response(response_data, status=contest_data[1])


class QuitContestView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Отказ от участия в конкурсе",
        description="Отказ от участия в конкурсе: изменение статуса заявки на 'Отказ'",
        parameters=[
            OpenApiParameter('Project-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER, required=True),
            OpenApiParameter('Account-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER)
        ],
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=QuitContestSerializer()
            ),
            **BaseContestView.COMMON_RESPONSES
        },
        tags=['Contests']
    )
    def delete(self, request, task_id):
        project_id = request.META.get('HTTP_PROJECT_ID') if request.META.get('HTTP_PROJECT_ID') else None
        account_id = request.META.get('HTTP_ACCOUNT_ID') if request.META.get('HTTP_ACCOUNT_ID') else None
        # валидируем заголовки
        serializer = HeadersSerializer(data={'project_id': project_id, 'account_id': account_id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        # получаем токен из заголовков для авторизации в сервисе конфигов
        auth_token = request.META.get('HTTP_AUTHORIZATION')
        # получаем конфиги из сервиса конфигов
        configs = get_configs(
            project_id=project_id,
            account_id=account_id,
            auth_token=auth_token,
            configs=['task_process_id', 'contest_process_id', 'node_id', 'task_status_id']
        )
        if configs[1] == 200:
            configs = configs[0]
            task_process_id = configs.get('data').get('task_process_id').get('value')
            node_id = configs.get('data').get('node_id').get('value')
            task_status_id = configs.get('data').get('task_status_id')
            task_status_rejection = configs.get('data').get('task_status_id').get('rejection')
        elif configs[1] == 400:
            return Response(
                {'detail': dict(code='INCORRECT_CREDENTIALS', message='Неправильно введены учетные данные.')},
                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(
                {'detail': dict(code='INTERNAL_SERVER_ERROR', message='Внутренняя ошибка в работе сервиса конфигов.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # получаем токен для запросов в Райду
        access_token = get_token()
        # проверяем, есть ли заявка на конкурс с данным task_id
        task_solution = task_solution_status(access_token, task_id, task_process_id, node_id, task_status_id)
        if task_solution.get('code') not in ('TASK_COMPLETED', 'TASK_UNCOMPLETED'):
            return Response({'detail': dict(code='NOT_FOUND', message='Заявка на участие не найдена.')},
                            status=status.HTTP_404_NOT_FOUND)
        # меняем статус заявки на конкурс на "Отказ"
        response_data = delete_task(access_token, task_id, node_id, task_status_rejection)
        return Response(response_data[0], status=response_data[1])


class UserTaskView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Создание задачи для участия в конкурсе",
        description="Создание задачи для участия в конкурсе",
        parameters=[
            OpenApiParameter('Project-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER, required=True),
            OpenApiParameter('Account-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER)
        ],
        request=CreateTaskSerializer,
        responses={
            201: OpenApiResponse(
                description="Successful Response",
                response=TaskResponseSerializer()
            ),
            409: OpenApiResponse(
                description="Объект уже существует",
                response=ErrorResponseSerializer()
            ),
            **BaseContestView.COMMON_RESPONSES
        },
        tags=['Contests']
    )
    def post(self, request):
        project_id = request.META.get('HTTP_PROJECT_ID') if request.META.get('HTTP_PROJECT_ID') else None
        account_id = request.META.get('HTTP_ACCOUNT_ID') if request.META.get('HTTP_ACCOUNT_ID') else None
        # валидируем заголовкм
        serializer = HeadersSerializer(data={'project_id': project_id, 'account_id': account_id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        # получаем токен из заголовков для авторизации в сервисе конфигов
        auth_token = request.META.get('HTTP_AUTHORIZATION')
        # получаем конфиги из сервиса конфигов
        configs = get_configs(
            project_id=project_id,
            account_id=account_id,
            auth_token=auth_token,
            configs=['task_process_id', 'contest_process_id', 'node_id', 'task_status_id']
        )
        if configs[1] == 200:
            configs = configs[0]
            task_process_id = configs.get('data').get('task_process_id').get('value')
            contest_process_id = configs.get('data').get('contest_process_id').get('value')
            node_id = configs.get('data').get('node_id').get('value')
            task_status_id = configs.get('data').get('task_status_id')
            task_status_new = configs.get('data').get('task_status_id').get('new')
        elif configs[1] == 400:
            return Response(
                {'detail': dict(code='INCORRECT_CREDENTIALS', message='Неправильно введены учетные данные.')},
                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(
                {'detail': dict(code='INTERNAL_SERVER_ERROR', message='Внутренняя ошибка в работе сервиса конфигов.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # получаем id пользователя из объекта Request
        user_id = request.auth.get('user_id')
        # валидируем данные, полученные от пользователя
        serializer = CreateTaskSerializer(data=request.data)
        if serializer.is_valid():
            contest_id = serializer.validated_data['contest_id']
            # получаем токен для запросов в Райду
            access_token = get_token()
            # проверяем, есть ли конкурс с данным contest_id
            if contest_exists(access_token, contest_id, node_id, contest_process_id):
                # проверяем, есть ли заявка на данный конкурс с любым статусом, кроме "Отказ"
                task = get_user_task(access_token, contest_id, user_id, task_process_id, node_id, task_status_id)
                if task and task.get('user_task'):
                    response = {
                        "detail": {
                            "code": "ENTITY_EXISTS",
                            "message": "Задача для участия в конкурсе уже существует."
                        },
                        "info": {
                            "api_version": "0.0.1",
                        }
                    }
                    return Response(response, status=status.HTTP_409_CONFLICT)
                # создаем новую заявку на участие в конкурсе
                new_contest = create_task(access_token, contest_id, user_id, node_id, task_process_id,
                                          task_status_new)
                return Response(new_contest, status=status.HTTP_201_CREATED)
            return Response({'detail': dict(code='NOT_FOUND', message='Конкурс не найден.')},
                            status=status.HTTP_404_NOT_FOUND)
        response = {'detail': {
            "code": "BAD_REQUEST",
            "message": serializer.errors
        }
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class SolutionView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser)

    @extend_schema(
        summary="Отправить решение на конкурс",
        description="Отправить решение на конкурс",
        parameters=[
            OpenApiParameter('Project-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER, required=True),
            OpenApiParameter('Account-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER)
        ],
        request=SolutionSerializer,
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=DetailSerializer()
            ),
            **BaseContestView.COMMON_RESPONSES
        },
        tags=['Contests']
    )
    def post(self, request):
        project_id = request.META.get('HTTP_PROJECT_ID') if request.META.get('HTTP_PROJECT_ID') else None
        account_id = request.META.get('HTTP_ACCOUNT_ID') if request.META.get('HTTP_ACCOUNT_ID') else None
        # валидируем заголовки
        serializer = HeadersSerializer(data={'project_id': project_id, 'account_id': account_id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        # получаем токен из заголовков для авторизации в сервисе конфигов
        auth_token = request.META.get('HTTP_AUTHORIZATION')
        # получаем конфиги из сервиса конфигов
        configs = get_configs(
            project_id=project_id,
            account_id=account_id,
            auth_token=auth_token,
            configs=['task_process_id', 'contest_process_id', 'node_id', 'task_status_id']
        )
        if configs[1] == 200:
            configs = configs[0]
            task_process_id = configs.get('data').get('task_process_id').get('value')
            node_id = configs.get('data').get('node_id').get('value')
            task_status_id = configs.get('data').get('task_status_id')
            task_status_completed = configs.get('data').get('task_status_id').get('completed')
        elif configs[1] == 400:
            return Response(
                {'detail': dict(code='INCORRECT_CREDENTIALS', message='Неправильно введены учетные данные.')},
                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(
                {'detail': dict(code='INTERNAL_SERVER_ERROR', message='Внутренняя ошибка в работе сервиса конфигов.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # получаем id пользователя из объекта Request
        user_id = request.auth.get('user_id')
        # валидируем данные, полученные от пользователя
        serializer = SolutionSerializer(data=request.data)
        if serializer.is_valid():
            task_id = serializer.validated_data['task_id']
            # получаем токен для доступа к Райде
            access_token = get_token()
            # проверяем, существует ли заявка с таким task_id, и было ли к ней прикреплено решение
            task_status = task_solution_status(access_token, task_id, task_process_id, node_id, task_status_id)
            # если решение не было отправлено ранее
            if task_status.get('code') == 'TASK_UNCOMPLETED':
                solution_file = request.FILES.getlist("solution_file")
                # посылаем полученный файл в Райду
                send_solution = post_attachments(access_token, task_id, user_id, node_id, solution_file[0])
                if send_solution[1] == 500:
                    return Response(data={'code': 'INTERNAL_SERVER_ERROR', 'message': f'Произошел сбой при отправке решения: {send_solution[0]}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                solution_link = serializer.validated_data['solution_link'] if 'solution_link' in serializer.validated_data else None
                comments = serializer.validated_data['comments'] if 'comments' in serializer.validated_data else None
                # меняем статус заявки на "решение отправлено" и добавляем к заявке ссылку на решение и комментарии
                change_status = patch_task(access_token, task_id, node_id, solution_link, comments, task_status_completed)
                if change_status[1] == 500:
                    return Response(data={'code': 'INTERNAL_SERVER_ERROR', 'message': f'Произошел сбой при отправке решения: {change_status[0]}'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response(data={'code': 'OK', 'message': 'Решение успешно отправлено'}, status=status.HTTP_200_OK)
            elif task_status.get('code') in ('TASK_COMPLETED', 'TASK_DOES_NOT_EXIST'):
                return Response(data=task_status, status=status.HTTP_400_BAD_REQUEST)
            return Response(data=task_status, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response = {'detail': {
            "code": "BAD_REQUEST",
            "message": serializer.errors
        }
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class UserTasksView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Получение списка заданий пользователя",
        description="Получение списка всех заданий пользователя. Мои задания.",
        parameters=[
            OpenApiParameter('Project-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER, required=True),
            OpenApiParameter('Account-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER)
        ],

        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=GetUserTasksListSerializer()
            ),
            **BaseContestView.COMMON_RESPONSES
        },
        tags=['Contests']
    )
    def get(self, request):
        access_token = get_token()
        project_id = request.META.get('HTTP_PROJECT_ID') if request.META.get('HTTP_PROJECT_ID') else None
        account_id = request.META.get('HTTP_ACCOUNT_ID') if request.META.get('HTTP_ACCOUNT_ID') else None
        serializer = HeadersSerializer(data={'project_id': project_id, 'account_id': account_id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        auth_token = request.META.get('HTTP_AUTHORIZATION')
        configs = get_configs(
            project_id=project_id,
            account_id=account_id,
            auth_token=auth_token,
            configs=['node_id', 'contest_process_id', 'contest_status_id', 'task_status_id', 'task_process_id']
        )

        if configs[1] == 200:
            configs = configs[0]
            node_id = configs.get('data').get('node_id').get('value')
            contest_process_id = configs.get('data').get('contest_process_id').get('value')
            process_task_id = configs.get('data').get('task_process_id').get('value')
            acceptance_works = configs.get('data').get('contest_status_id').get('acceptance_works')
            acceptance_works_done = configs.get('data').get('contest_status_id').get('acceptance_works_done')
            voting = configs.get('data').get('contest_status_id').get('voting')
            sum_results = configs.get('data').get('contest_status_id').get('sum_results')
            done = configs.get('data').get('contest_status_id').get('done')
            task_status_id_rejection = configs.get('data').get('task_status_id').get('rejection')
        elif configs[1] == 400:
            return Response(
                {'detail': dict(code='INCORRECT_CREDENTIALS', message='Неправильно введены учетные данные.')},
                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(
                {'detail': dict(code='INTERNAL_SERVER_ERROR', message='Внутренняя ошибка в работе сервиса конфигов.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if request.auth:
            user_id = request.auth.get('user_id')

        result_data = get_tasks(
            token=access_token,
            node_id=node_id,
            process_id=contest_process_id,
            process_task_id=process_task_id,
            status_ids=(
                acceptance_works,
                acceptance_works_done,
                voting,
                sum_results,
                done
            ),
            task_status_id_rejection=task_status_id_rejection,
            projects_ids=None,
            user_id=user_id,
            message="Получение списка всех конкурсов со статусом Прием работ, Прием работ окончен, Голосование, "
                    "Подведение итогов, Завершен. Для раздела мои задания."
        )

        return Response(result_data[0], status=result_data[1])


class UserHistoryView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Получение списка завершенных конкурсов пользователя",
        description="Получение списка всех завершенных конкурсов, где пользователя участвовал. История участия.",
        parameters=[
            OpenApiParameter('Project-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER, required=True),
            OpenApiParameter('Account-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER)
        ],
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=GetUserHistoryListSerializer()
            ),
            **BaseContestView.COMMON_RESPONSES
        },
        tags=['Contests']
    )
    def get(self, request, user_id=None):
        access_token = get_token()
        project_id = request.META.get('HTTP_PROJECT_ID') if request.META.get('HTTP_PROJECT_ID') else None
        account_id = request.META.get('HTTP_ACCOUNT_ID') if request.META.get('HTTP_ACCOUNT_ID') else None
        serializer = HeadersSerializer(data={'project_id': project_id, 'account_id': account_id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        auth_token = request.META.get('HTTP_AUTHORIZATION')
        configs = get_configs(
            project_id=project_id,
            account_id=account_id,
            auth_token=auth_token,
            configs=['node_id', 'contest_process_id', 'task_process_id', 'contest_status_id']
        )
        if configs[1] == 200:
            configs = configs[0]
            node_id = configs.get('data').get('node_id').get('value')
            contest_process_id = configs.get('data').get('contest_process_id').get('value')
            task_process_id = configs.get('data').get('task_process_id').get('value')
            done = configs.get('data').get('contest_status_id').get('done')
        elif configs[1] == 400:
            return Response(
                {'detail': dict(code='INCORRECT_CREDENTIALS', message='Неправильно введены учетные данные.')},
                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(
                {'detail': dict(code='INTERNAL_SERVER_ERROR', message='Внутренняя ошибка в работе сервиса конфигов.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if user_id is None and request.auth:
            user_id = request.auth.get('user_id')

        result_data = get_history(
            token=access_token,
            node_id=node_id,
            process_id=contest_process_id,
            task_process_id=task_process_id,
            status_ids=(
                done
            ),
            projects_ids=None,
            user_id=user_id,
            message="Получение списка всех конкурсов со статусом Завершен. Для раздела история участия."
        )
        return Response(result_data[0], status=result_data[1])


class ContestTasksView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Получение списка задач конкурса по статусам",
        description="Получение списка задач/участий в конкурсах по переданным статусам/у в рамках конкретного конкурса",
        parameters=[
            QueryParamsSerializer,
            OpenApiParameter('Project-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER, required=True),
            OpenApiParameter('Account-ID', OpenApiTypes.UUID, OpenApiParameter.HEADER)
        ],
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=GetContestTasksListSerializer()
            ),
            **BaseContestView.COMMON_RESPONSES
        },
        tags=['Contests']
    )
    def get(self, request, contest_id):
        access_token = get_token()
        project_id = request.META.get('HTTP_PROJECT_ID') if request.META.get('HTTP_PROJECT_ID') else None
        account_id = request.META.get('HTTP_ACCOUNT_ID') if request.META.get('HTTP_ACCOUNT_ID') else None
        serializer = HeadersSerializer(data={'project_id': project_id, 'account_id': account_id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        auth_token = request.META.get('HTTP_AUTHORIZATION')
        configs = get_configs(
            project_id=project_id,
            account_id=account_id,
            auth_token=auth_token,
            configs=['node_id', 'task_process_id', 'task_status_id']
        )
        if configs[1] == 200:
            configs = configs[0]
            node_id = configs.get('data').get('node_id').get('value')
            task_process_id = configs.get('data').get('task_process_id').get('value')
            status_id_task_approved = configs.get('data').get('task_status_id').get('approved')
            status_id_task_completed = configs.get('data').get('task_status_id').get('completed')
        elif configs[1] == 400:
            return Response(
                {'detail': dict(code='INCORRECT_CREDENTIALS', message='Неправильно введены учетные данные.')},
                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(
                {'detail': dict(code='INTERNAL_SERVER_ERROR', message='Внутренняя ошибка в работе сервиса конфигов.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        status_ids = request.query_params.getlist('status')

        if not status_ids:
            status_ids = (status_id_task_approved, status_id_task_completed)
        else:
            status_ids = tuple(status_ids) if len(status_ids) > 1 else ''.join(status_ids)

        result_data = get_contest_tasks(
            token=access_token,
            node_id=node_id,
            process_id=task_process_id,
            contest_id=contest_id,
            task_status=status_ids,
            message="Получение списка задач конкурса по статусам"
        )
        return Response(result_data[0], status=result_data[1])
