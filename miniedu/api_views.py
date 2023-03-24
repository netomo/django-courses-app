from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model, authenticate

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Course, CourseInstance, Enrollment
from .serializers import (
    UserSerializer,
    LoginSerializer,
    CourseSerializer,
    EnrollmentSerializer,
)


class RegisterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to register.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["post", "get"]

    def get_queryset(self):
        """Allowing only authenticated users to see their own profile."""
        user = self.request.user
        if user.is_authenticated:
            return user.__class__.objects.filter(id=user.id)
        return get_user_model().objects.none()

    def create(self, request, *args, **kwargs):
        UserModel = get_user_model()
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = UserModel.objects.create_user(
                    username=serializer.validated_data["username"],
                    email=serializer.validated_data["email"],
                    password=serializer.validated_data["password"],
                )
                user.profile = UserModel.objects.create(
                    user=user, **serializer.validated_data["profile"]
                )
                user.save()
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED, headers=headers
                )
        except IntegrityError:
            return Response(
                {"detail": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request, *args, **kwargs):
        """Replacing the default list method with a detail method."""
        user = self.request.user
        if user.is_authenticated:
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        return Response(
            {"detail": "You are not authenticated"}, status=status.HTTP_401_UNAUTHORIZED
        )


class LoginViewSet(viewsets.ViewSet):
    serializer_class = LoginSerializer

    def create(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Missing credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user": UserSerializer(user).data})
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows courses to be viewed or edited.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    @action(
        detail=True,
        methods=["post"],
        url_path="enroll/(?P<instance_id>[0-9]+)",
        permission_classes=[permissions.IsAuthenticated],
    )
    def enroll_student(self, request, pk=None, instance_id=None):
        """
        Enroll the current userin a course.
        Validates that the student is not already enrolled and that the course has capacity.
        """
        course = self.get_object()
        try:
            course_instance = CourseInstance.objects.get(id=instance_id, course=course)
        except CourseInstance.DoesNotExist:
            return Response(
                {"error": "Course instance not found"}, status=status.HTTP_404_NOT_FOUND
            )

        student_profile = request.user.eduprofile

        # Some checks
        if Enrollment.objects.filter(
            student=student_profile, course=course_instance
        ).exists():
            return Response(
                {"error": "Student already enrolled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            course_instance.capacity > 0
            and course_instance.capacity <= course_instance.enrollment_set.count()
        ):
            return Response(
                {"error": "Course capacity reached"}, status=status.HTTP_400_BAD_REQUEST
            )

        enrollment = Enrollment.objects.create(
            student=student_profile, course=course_instance
        )
        # Get the enrollment serializer

        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
