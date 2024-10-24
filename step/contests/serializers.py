from rest_framework import serializers


class ErrorDetailSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    message = serializers.CharField(required=True)


class ErrorResponseSerializer(serializers.Serializer):
    """Сериализатор для общего ответа об ошибке"""
    detail = ErrorDetailSerializer()


class AddressSerializer(serializers.Serializer):
    city = serializers.CharField()
    postcode = serializers.CharField()
    street = serializers.CharField()
    house = serializers.CharField()
    apartments = serializers.CharField()
    entrance = serializers.CharField()
    floor = serializers.CharField()
    lat = serializers.CharField()
    lon = serializers.CharField()


class ContestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField()
    status = serializers.CharField()
    process = serializers.CharField()
    cf_deadline = serializers.DateField(format="%d.%m.%Y")
    cf_award = serializers.CharField()
    cf_address = AddressSerializer()
    cf_brief = serializers.CharField()
    cf_title = serializers.CharField()
    cf_konkurs_category = serializers.CharField()
    cf_timepickerrange = serializers.CharField()


class DetailSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    message = serializers.CharField(required=True)


class InfoSerializer(serializers.Serializer):
    api_version = serializers.CharField(required=True)
    count = serializers.IntegerField()
    compression_algorithm = serializers.CharField()


class GetArchiveSerializer(serializers.Serializer):
    """Сериализатор для формата ответа API, который возвращает список конкурсов со статусом Завершено """
    detail = DetailSerializer()
    data = ContestSerializer(many=True)
    info = InfoSerializer()
