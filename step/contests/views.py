from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import (GetArchiveSerializer, ErrorResponseSerializer, ContestDetailsResponseSerializer,
                          GetContestsListSerializer, QueryParamsSerializer)

from .services import get_token, get_archive_contests, get_contest, get_contests, get_user, get_application_status


class ArchiveView(APIView):
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Retrieve a list of contests",
        description="Получение списка всех конкурсов со статусом Завершен",
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

        tags=['Contests']  # Archive на выбор
    )
    def get(self, request):
        access_token = get_token()
        result_data = get_archive_contests(access_token)
        return Response(result_data[0], status=result_data[1])


class ContestDetailsView(APIView):
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
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if auth_header:
            payload = get_user(auth_header)
            if payload[1] == 401:
                return Response(payload[0], status=status.HTTP_401_UNAUTHORIZED)
            user_id = payload[0].get('user_id')
            application_status = get_application_status(access_token, contest_id, user_id)
        contest_data = get_contest(access_token, contest_id)
        if not contest_data:
            return Response({'detail': dict(code='NOT_FOUND', message='Конкурс не найден.')}, status=status.HTTP_404_NOT_FOUND)
        response_data = contest_data[0]
        response_data['data'].update({'application_status': application_status})
        return Response(response_data, status=contest_data[1])


class ContestsView(APIView):
    parser_classes = [JSONParser]

    @extend_schema(
        parameters=[
            QueryParamsSerializer,
        ],
        summary="Retrieve a list of contests",
        description="Получение списка конкурсов по заданному статусу или статусам, проекту или проектам",
        responses={
            200: OpenApiResponse(
                description="Successful Response",
                response=GetContestsListSerializer()
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
    def get(self, request, process_id):
        access_token = get_token()

        status_ids = request.query_params.getlist('status_id')
        projects_ids = request.query_params.getlist('project_id')

        if not process_id:
            return Response({
                "detail": {
                    "code": "BAD_REQUEST",
                    "message": "Необходимо передать параметр 'process_id'."
                }
            }, status=400)

        result_data = get_contests(
            token=access_token,
            process_id=process_id,
            status_ids=status_ids,
            projects_ids=projects_ids
        )

        return Response(result_data[0], status=result_data[1])
