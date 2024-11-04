from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import GetArchiveSerializer, ErrorResponseSerializer, ContestDetailsResponseSerializer
from .services import get_token, get_archive_contests, get_contest


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
        contest_data = get_contest(access_token, contest_id)
        return Response(contest_data[0], status=contest_data[1])

