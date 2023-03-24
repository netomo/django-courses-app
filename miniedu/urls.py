from django.urls import path, include
from rest_framework import routers
from . import api_views

router = routers.DefaultRouter()
router.register(r"courses", api_views.CourseViewSet, basename="courses")
router.register(r"register", api_views.RegisterViewSet, basename="register")
router.register(r"login", api_views.LoginViewSet, basename="login")


urlpatterns = [
    path("", include(router.urls)),
]
