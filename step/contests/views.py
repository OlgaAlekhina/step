from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.conf import settings

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions

from .serializers import (GetArchiveSerializer, ErrorResponseSerializer, ContestDetailsResponseSerializer,
                          QuitContestSerializer, CreateTaskSerializer, TaskResponseSerializer)

from .services import (get_token, get_contest, get_contests, get_application_status, get_tasks, patch_task,
                       get_history, contest_exists, create_task)

# ID Конкурсов
process_contests_id = settings.PROCESS_CONTESTS_ID
process_participation_contest_id = settings.PROCESS_PARTICIPATION_CONTEST_ID

# ID Статусов конкурса
status_id_new = settings.STATUS_ID_NEW
status_id_rejection = settings.STATUS_ID_REJECTION
status_id_sum_results = settings.STATUS_ID_SUM_RESULTS
status_id_voting = settings.STATUS_ID_VOTING
status_id_acceptance_works = settings.STATUS_ID_ACCEPTANCE_WORKS
status_id_done = settings.STATUS_ID_DONE
status_id_acceptance_works_done = settings.STATUS_ID_ACCEPTANCE_WORKS_DONE
status_id_no_winner = settings.STATUS_ID_NO_WINNER

user_id_test = 'seghstr3345ega'


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
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Получение списка архивных конкурсов",
        description="Получение списка всех конкурсов со статусом Завершен и Победитель не выбран. Архив конкурсов.",
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
        result_data = get_contests(
            token=access_token,
            process_id=process_contests_id,
            status_ids=(status_id_done, status_id_no_winner),
            # status_ids=('Завершен', 'Победитель не выбран'),  # Если передавать name а не id
            # projects_ids=None,
            # projects_ids='step',
            projects_ids=('step', 'start'),
            message="Получение списка всех конкурсов со статусом Завершен и Победитель не выбран. Архив конкурсов."
        )
        return Response(result_data[0], status=result_data[1])


class ActiveContestsView(BaseContestView):
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Получение списка активных конкурсов",
        description="Получение списка всех конкурсов со статусом Прием работ. Активные конкурсы.",
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
        result_data = get_contests(
            token=access_token,
            process_id=process_contests_id,
            status_ids=status_id_acceptance_works,
            # status_ids='Прием работ',  # Если передавать name а не id
            # projects_ids=None,
            # projects_ids='step',
            projects_ids=('step', 'start'),
            message="Получение списка всех конкурсов со статусом Прием работ. Активные конкурсы."
        )
        return Response(result_data[0], status=result_data[1])


class ContestDetailsView(BaseContestView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Получение конкретного конкурса",
        description="Получение данных одного конкурса по его id",
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
        access_token = get_token()
        user_data = {'user_task_id': None, 'user_task_status': {'code': 'NOT_DEFINED', 'message': 'Не определен'}}
        # если запрос успешно прошел аутентификацию, получаем id пользователя
        if request.auth:
            user_id = request.auth.get('user_id')
            # проверяем, отправил пользователь решение или нет
            result = get_application_status(access_token, contest_id, user_id)
            user_data = {'user_task_id': result.get('user_task'), 'user_task_status': result.get('task_status')}
        contest_data = get_contest(access_token, contest_id)
        if not contest_data:
            return Response({'detail': dict(code='NOT_FOUND', message='Конкурс не найден.')},
                            status=status.HTTP_404_NOT_FOUND)
        response_data = contest_data[0]
        if contest_data[1] == 200:
            response_data['data'].update(user_data)
        return Response(response_data, status=contest_data[1])


class QuitContestView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Отказ от участия в конкурсе",
        description="Отказ от участия в конкурсе: изменение статуса заявки на 'Отказ'",
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
        access_token = get_token()
        user_id = request.auth.get('user_id')
        response_data = patch_task(access_token, task_id, user_id)
        if not response_data:
            return Response({'detail': dict(code='NOT_FOUND', message='Заявка на участие не найдена.')},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(response_data[0], status=response_data[1])


class UserTaskView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        summary="Создать задачу для участия в конкурсе",
        description="Создание задачи для участия в конкурсе",
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
        user_id = request.auth.get('user_id')
        serializer = CreateTaskSerializer(data=request.data)
        if serializer.is_valid():
            contest_id = serializer.validated_data['contest_id']
            access_token = get_token()
            if contest_exists(access_token, contest_id):
                task = get_application_status(access_token, contest_id, user_id)
                if task and task.get('user_task'):
                    response = {
                        "detail": {
                            "code": "ENTITY_EXISTS",
                            "message": "Задача для участия в конкурсе уже существует."
                        },
                        "info": {
                            "api_version": "0.0.1",
                            # "compression_algorithm": "lossy"
                        }
                    }
                    return Response(response, status=status.HTTP_409_CONFLICT)

                else:
                    new_contest = create_task(access_token, contest_id, user_id)
                    return Response(new_contest, status=status.HTTP_201_CREATED)
            return Response({'detail': dict(code='NOT_FOUND', message='Конкурс не найден.')},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors)


class UserTasksView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Получение списка заданий пользователя",
        description="Получение списка всех заданий пользователя. Мои задания.",
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=GetArchiveSerializer()
            ),
            **BaseContestView.COMMON_RESPONSES
        },
        tags=['Contests']
    )
    def get(self, request):
        access_token = get_token()
        user_id = request.auth.get('user_id')
        result_data = get_tasks(
            token=access_token,
            process_id=process_contests_id,
            # status_ids=None,
            status_ids=(
                status_id_acceptance_works,
                status_id_acceptance_works_done,
                status_id_voting,
                status_id_sum_results,
                status_id_done
            ),
            # status_ids='Прием работ',  # Если передавать name а не id
            projects_ids=None,
            user_id=user_id,
            # projects_ids='step',
            # projects_ids=('step', 'start'),
            message="Получение списка всех конкурсов со статусом Прием работ, Прием работ окончен, Голосование, Подведение итогов, Завершен. Для раздела мои задания."
        )
        return Response(result_data[0], status=result_data[1])


class UserHistoryView(BaseContestView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Получение списка завершенных конкурсов пользователя",
        description="Получение списка всех завершенных конкурсов, где пользователя участвовал. История участия.",
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=GetArchiveSerializer()
            ),
            **BaseContestView.COMMON_RESPONSES
        },
        tags=['Contests']
    )
    def get(self, request):
        access_token = get_token()
        user_id = request.auth.get('user_id')
        result_data = get_history(
            token=access_token,
            process_id=process_contests_id,
            # status_ids=None,
            status_ids=(
                status_id_done
            ),
            # status_ids='Прием работ',  # Если передавать name а не id
            projects_ids=None,
            user_id=user_id,
            # projects_ids='step',
            # projects_ids=('step', 'start'),
            message="Получение списка всех конкурсов со статусом Завершен. Для раздела история участия."
        )
        return Response(result_data[0], status=result_data[1])
