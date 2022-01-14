from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Lecture, SubjectProfessor
from university.models import University
from article.serializers import *
from common.custom_exception import CustomException



class SubjectProfessorSerializer(serializers.ModelSerializer):

    subject_name = serializers.CharField()
    professor = serializers.CharField(allow_null=True)

    class Meta:
        model = SubjectProfessor
        fields = ('subject_name', 'professor')


    def validate(self, data):
        if SubjectProfessor.objects.filter(subject_name=data['subject_name'], professor=data['professor']):
            raise CustomException("이미 존재하는 Subject-Professor 입니다.", status.HTTP_409_CONFLICT)
        # create 시의 logic
        return data



class LectureSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField()
    professor = serializers.CharField(allow_null=True)
    subject_code = serializers.CharField()
    ####
    year = serializers.IntegerField()
    season = serializers.IntegerField()
    ####
    college = serializers.CharField(allow_null=True)
    department = serializers.CharField(allow_null=True)
    grade = serializers.IntegerField()
    level = serializers.IntegerField()
    credit = serializers.IntegerField()
    category = serializers.IntegerField()
    number = serializers.IntegerField()
    detail = serializers.CharField(allow_null=True)
    language = serializers.CharField()
    ####
    time = serializers.CharField(allow_null=True)
    location = serializers.CharField(allow_null=True)

    class Meta:
        model = Lecture
        fields = ('subject_name', 'subject_code', 'professor',
                  'year', 'season', 'college', 'department', 'grade', 'level', 'credit',
                  'category', 'number', 'detail', 'language',
                  'time', 'location')

    def create(self, validated_data):
        subject_professor = SubjectProfessor.objects.get_or_none\
            (subject_name=validated_data['subject_name'], professor=validated_data['professor'])

        if not subject_professor:
            serializer = SubjectProfessorSerializer(
                data={"subject_name": validated_data['subject_name'],
                      "professor": validated_data['professor']})
            serializer.is_valid(raise_exception=True)
            subject_professor = serializer.save()

        validated_data['subject_professor'] = subject_professor
        validated_data.pop('subject_name')
        validated_data.pop('professor')

        lecture = Lecture.objects.create(**validated_data)
        return lecture

    def update(self, instance, validated_data):
        validated_data.pop('subject_name')
        validated_data.pop('professor')
        super().update(instance, validated_data)


class LectureViewSerializer(LectureSerializer):
    subject_name = serializers.SerializerMethodField()
    professor = serializers.SerializerMethodField()
    ####
    season = serializers.SerializerMethodField()
    ####
    level = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    ####

    def get_subject_name(self, obj):
        return obj.subject_professor.subject_name

    def get_professor(self, obj):
        return obj.subject_professor.professor

    def get_season(self, obj):
        return Lecture.SeasonCode[obj.season]

    def get_level(self, obj):
        return Lecture.LevelCode[obj.level]

    def get_category(self, obj):
        return Lecture.CategoryCode[obj.category]




