from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ContestsResponseSerializer, GetSolutionsSerializer
from .services import *


class ContestsView(APIView):

    @extend_schema(
        summary="Retrieve a list of contests",
        description="Получение списка всех конкурсов",
        responses={200: ContestsResponseSerializer(many=True)},
        tags=['Contests']
    )
    def get(self, request):
        access_token = get_token()
        contests = get_contests(access_token)

        return Response(contests, status=status.HTTP_200_OK)


class SolutionsView(APIView):
    parser_classes = [JSONParser]

    @extend_schema(
        summary="Retrieve a list of contests",
        description="Получение списка всех конкурсов",
        responses={200: GetSolutionsSerializer(many=True)},
        tags=['solutions']
    )
    def get(self, request):
        access_token = get_token()
        contests = get_solution_contests(access_token)

        return Response(contests, status=status.HTTP_200_OK)
