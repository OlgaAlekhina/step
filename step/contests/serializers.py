from rest_framework import serializers


# class ContestsResponseSerializer(serializers.Serializer):
#     title = serializers.CharField()
#     id = serializers.CharField()
#     brief = serializers.CharField()
#     category = serializers.CharField()


class FioSerializer(serializers.Serializer):
    name = serializers.CharField()
    surname = serializers.CharField(allow_blank=True)
    middlename = serializers.CharField(allow_blank=True)


class ContactsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.CharField()


class AuthorSerializer(serializers.Serializer):
    id = serializers.CharField()
    user_name = serializers.CharField()
    fio = FioSerializer()
    contacts = ContactsSerializer()
    full_name = serializers.CharField()


class ProcessSerializer(serializers.Serializer):
    id = serializers.CharField()
    key = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    teams = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    progress_id = serializers.CharField()
    node_id = serializers.CharField()


class StatusSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    color = serializers.CharField(allow_null=True)
    description = serializers.CharField()


class CustomFieldsSerializer(serializers.Serializer):
    cf_deadline = serializers.DateTimeField()
    cf_contact = ContactsSerializer()
    cf_konkurs_link = serializers.CharField(allow_blank=True)
    cf_award = serializers.CharField()
    cf_timepickerrange = serializers.CharField(allow_blank=True)
    cf_address = serializers.DictField(
        child=serializers.CharField(),
        allow_empty=True
    )
    cf_brief = serializers.CharField(allow_blank=True)
    cf_konkurs_category = serializers.CharField(allow_blank=True)
    cf_title = serializers.CharField(allow_blank=True)
    cf_oiv_type = serializers.CharField(allow_blank=True)
    cf_konkurs_id = serializers.CharField(allow_blank=True)
    cf_userid = serializers.CharField(allow_blank=True)
    cf_projects = serializers.CharField()
    cf_profession = serializers.CharField(allow_blank=True)


class GetArchiveSerializer(serializers.Serializer):
    id = serializers.CharField()
    key = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    author = AuthorSerializer()
    assignee = serializers.CharField(allow_null=True)
    process = ProcessSerializer()
    status = StatusSerializer()
    custom_fields = CustomFieldsSerializer()
    attachments = serializers.ListField(child=serializers.DictField(), allow_empty=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField(allow_null=True)
