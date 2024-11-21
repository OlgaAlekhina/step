from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.conf import settings

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions

from .serializers import (GetArchiveSerializer, ErrorResponseSerializer, ContestDetailsResponseSerializer, QuitContestSerializer)

from .services import (get_token, get_contest, get_contests, get_application_status, get_tasks, patch_docontest)

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


class ArchiveContestsView(APIView):
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Retrieve a list of contests",
        description="Получение списка всех конкурсов со статусом Завершен и Победитель не выбран. Архив конкурсов.",
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=GetArchiveSerializer()
            ),
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
        },

        tags=['Contests']
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
        # result_data = get_archive_contests(access_token)
        return Response(result_data[0], status=result_data[1])


class ActiveContestsView(APIView):
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Retrieve a list of contests",
        description="Получение списка всех конкурсов со статусом Прием работ. Активные конкурсы.",
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=GetArchiveSerializer()
            ),
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
        },

        tags=['Contests']
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
        # result_data = get_archive_contests(access_token)
        return Response(result_data[0], status=result_data[1])


class ContestDetailsView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    @extend_schema(
        summary="Retrieve a details of contest",
        description="Получение данных одного конкурса по его id",
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=ContestDetailsResponseSerializer()
            ),
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
        },
        tags=['Contests']
    )
    def get(self, request, contest_id):
        access_token = get_token()
        application_status = None
        # если запрос успешно прошел аутентификацию, получаем id пользователя
        if request.auth:
            user_id = request.auth.get('user_id')
            # проверяем, отправил пользователь решение или нет
            application_status = get_application_status(access_token, contest_id, user_id)
        contest_data = get_contest(access_token, contest_id)
        if not contest_data:
            return Response({'detail': dict(code='NOT_FOUND', message='Конкурс не найден.')},
                            status=status.HTTP_404_NOT_FOUND)
        response_data = contest_data[0]
        if contest_data[1] == 200:
            response_data['data'].update({'application_status': application_status})
        return Response(response_data, status=contest_data[1])


class QuitContestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        summary="Update status of contest application",
        description="Отказ от участия в конкурсе: изменение статуса заявки на 'Отказ'",
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=QuitContestSerializer()
            ),
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
        },
        tags=['Contests']
    )
    def patch(self, request, contest_id):
        access_token = get_token()
        user_id = request.auth.get('user_id')
        response_data = patch_docontest(access_token, contest_id, user_id)
        if not response_data:
            return Response({'detail': dict(code='NOT_FOUND', message='Конкурс не найден.')},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(response_data[0], status=response_data[1])


class UserTasksView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Retrieve a list of contests",
        description="Получение списка всех заданий пользователя. Мои задания.",
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=GetArchiveSerializer()
            ),
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
        # result_data = get_archive_contests(access_token)
        return Response(result_data[0], status=result_data[1])
