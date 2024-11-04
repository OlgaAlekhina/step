from rest_framework import serializers
from dataclasses import dataclass
from datetime import datetime


def datetime_convert(date, format_date='%d.%m.%Y'):
    """Преобразование даты в заданный формат."""
    if date is not None:
        result = datetime.fromisoformat(date.rstrip("Z") + "+00:00").strftime(format_date)
    else:
        result = date
    return result


class ErrorDetailSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    message = serializers.CharField(required=True)


class ErrorResponseSerializer(serializers.Serializer):
    """Сериализатор для общего ответа об ошибке"""
    detail = ErrorDetailSerializer()


class ContestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField()
    status = serializers.CharField()
    cf_deadline = serializers.DateField(format="%d.%m.%Y")
    cf_award = serializers.CharField()
    cf_brief = serializers.CharField()
    cf_title = serializers.CharField()
    cf_konkurs_category = serializers.CharField()


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


@dataclass
class Contest:
    id: str
    title: str
    description: str
    created_at: str
    status_id: str
    status_name: str
    deadline: str
    award: str
    profession: str
    category: str
    attachments: str


class StatusSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class CustomFieldsSerializer(serializers.Serializer):
    cf_brief = serializers.CharField(allow_blank=True)
    cf_profession = serializers.CharField(allow_blank=True)
    cf_deadline = serializers.CharField()
    cf_award = serializers.CharField(allow_blank=True)
    cf_konkurs_category = serializers.CharField(allow_blank=True)


class AttachmentsSerializer(serializers.Serializer):
    id = serializers.CharField(allow_blank=True)
    name = serializers.CharField(allow_blank=True)


class ContestsSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField()
    created_at = serializers.CharField()
    status = StatusSerializer()
    custom_fields = CustomFieldsSerializer()
    attachments = serializers.ListField(child=AttachmentsSerializer(), allow_null=True)

    def create(self, validated_data):
        status = validated_data.pop('status')
        cf = validated_data.pop('custom_fields')
        created_at = validated_data.pop('created_at')
        validated_data['created_at'] = datetime_convert(created_at)
        validated_data['status_id'] = status['id']
        validated_data['status_name'] = status['name']
        validated_data['deadline'] = datetime_convert(cf['cf_deadline'])
        validated_data['award'] = cf['cf_award']
        validated_data['profession'] = cf['cf_profession']
        validated_data['category'] = cf['cf_konkurs_category']
        return Contest(**validated_data)


class ContestDetailsSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField()
    created_at = serializers.DateField(format="%d.%m.%Y")
    status_id = serializers.UUIDField()
    status_name = serializers.CharField()
    deadline = serializers.DateField(format="%d.%m.%Y")
    award = serializers.CharField()
    profession = serializers.CharField()
    category = serializers.CharField()
    attachments = AttachmentsSerializer()


class ContestDetailsResponseSerializer(serializers.Serializer):
    """Сериализатор для формата ответа API, который возвращает детали конкурса по его id """
    detail = DetailSerializer()
    data = ContestDetailsSerializer()
    info = InfoSerializer()
