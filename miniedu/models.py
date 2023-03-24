from django.conf import settings
from django.db import models


class EduProfile(models.Model):
    PROFILE_TYPES = (
        ("P", "Parent"),
        ("S", "Student"),
        ("T", "Teacher"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to="profile-images/", blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    profile_type = models.CharField(max_length=1, choices=PROFILE_TYPES, default="S")

    def __str__(self):
        return self.user.username


class Course(models.Model):
    """Course model for the miniedu app"""

    COURSE_TYPES = (
        ("O", "Online - Recorded"),  # Self-Paced
        ("L", "Online - Live"),  # Live
        ("D", "On-Demand"),  # As Needed by a Student
    )

    COURSE_AGES = (
        ("A", "All"),
        ("5", "5 - 7"),
        ("8", "8 - 9"),
        ("10", "10 - 11"),
        ("12", "12 - 15"),
        ("16", "16 - 18"),
    )

    name = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=500)
    video_preview = models.FileField(upload_to="courses/previews/")
    studies_plan = models.FileField(upload_to="courses/studies_plans/")
    image = models.ImageField(upload_to="images/")

    course_type = models.CharField(max_length=1, choices=COURSE_TYPES)
    course_age = models.CharField(max_length=2, choices=COURSE_AGES)

    price = models.IntegerField()

    def __str__(self):
        return self.course_name


class CourseInstance(models.Model):
    """
    CourseInstance represents a specific instance of a course.
    Will be used to track enrollment, start and end dates!

    For example, a course may be offered in the morning and afternoon or in the Spring and Fall semesters
    By one teacher by the morning and another teacher in the afternoon.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(EduProfile, on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.IntegerField(default=0)  # 0 = unlimited
    is_active = models.BooleanField(
        default=True
    )  # Is the course currently being offered?


class CourseSchedule(models.Model):
    """CourseSchedule represents the schedule of a course instance."""

    DAYS_OF_WEEK = (
        ("1", "Monday"),
        ("2", "Tuesday"),
        ("3", "Wednesday"),
        ("4", "Thursday"),
        ("5", "Friday"),
        ("6", "Saturday"),
        ("7", "Sunday"),
    )
    course = models.ForeignKey(CourseInstance, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=1, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.course.course.name + " " + self.day_of_week


class Enrollment(models.Model):
    """Represents a student's enrollment in a course instance."""

    student = models.ForeignKey(EduProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseInstance, on_delete=models.CASCADE)
    date_enrolled = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.student.user.username + " " + self.course.course.name


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    deliverable = models.FileField(upload_to="deliverables/")
    due_date = models.DateField()

    def __str__(self):
        return self.course.name + " " + self.name
