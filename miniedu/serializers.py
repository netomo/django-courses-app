from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Course, CourseInstance, CourseSchedule, Enrollment, EduProfile


class EduProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = EduProfile
        fields = ["bio", "image", "profile_type"]


class UserSerializer(serializers.ModelSerializer):
    profile = EduProfileSerializer()

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password", "profile"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})


class CourseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSchedule
        fields = ("start_time", "end_time", "day_of_week")


class CourseInstanceSerializer(serializers.ModelSerializer):
    schedule = CourseScheduleSerializer(many=True)

    class Meta:
        model = CourseInstance
        fields = (
            "id",
            "course",
            "teacher",
            "start_date",
            "end_date",
            "schedule",
            "capacity",
            "is_active",
        )


class CourseSerializer(serializers.ModelSerializer):
    course_instances = CourseInstanceSerializer(many=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "description",
            "video_preview",
            "studies_plan",
            "image",
            "course_type",
            "course_age",
            "course_instances",
            "price",
        )


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ("student", "course", "date_enrolled", "is_active")
