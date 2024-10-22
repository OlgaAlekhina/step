from rest_framework import serializers


class ContestsResponseSerializer(serializers.Serializer):
    title = serializers.CharField()
    id = serializers.CharField()
    brief = serializers.CharField()
    category = serializers.CharField()


class GetSolutionsSerializer(serializers.Serializer):
    contest_title = serializers.CharField()
    contest_id = serializers.CharField()
