from django.conf import settings
from django.db import models


class EduProfile(models.Model):
    PROFILE_TYPES = (
        ("P", "Parent"),
        ("S", "Student"),
        ("T", "Teacher"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="edu_profile", on_delete=models.CASCADE
    )
    bio = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to="profile-images/", blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    profile_type = models.CharField(max_length=1, choices=PROFILE_TYPES, default="S")

    def __str__(self):
        return "%s - (%s)" % (self.user.username, self.get_profile_type_display())


class CourseManager(models.Manager):
    def get_queryset(self):
        """
        Prefetch related objects to avoid N+1 queries.
        """
        return (
            super()
            .get_queryset()
            .prefetch_related("course_instances")
            .prefetch_related("course_instances__schedules")
        )

    def get_courses_with_enrollments_count(self):
        return self.get_queryset().annotate(
            enrollments_count=models.Count("course__enrollments")
        )

    def get_popular_courses(self):
        return self.get_courses_with_enrollments_count().order_by(
            "-course__enrollments__count"
        )[:5]

    def get_new_courses(self):
        return self.get_queryset().order_by("-course__course_instances__start_date")[:5]

    def get_recommended_courses(self):
        return self.get_queryset().order_by("-course__course_instances__start_date")[:5]


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
    video_preview = models.FileField(upload_to="courses/previews/", blank=True)
    studies_plan = models.FileField(upload_to="courses/studies_plans/", blank=True)
    image = models.ImageField(upload_to="images/", blank=True)

    course_type = models.CharField(max_length=1, choices=COURSE_TYPES)
    course_age = models.CharField(max_length=2, choices=COURSE_AGES)

    price = models.IntegerField(default=0)

    objects = CourseManager()

    def __str__(self):
        return self.name + " - " + self.get_course_type_display()


class CourseInstance(models.Model):
    """
    CourseInstance represents a specific instance of a course.
    Will be used to track enrollment, start and end dates!

    For example, a course may be offered in the morning and afternoon or in the Spring and Fall semesters
    By one teacher by the morning and another teacher in the afternoon.
    """

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_instances"
    )
    teacher = models.ForeignKey(EduProfile, on_delete=models.CASCADE, related_name="courses")

    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.IntegerField(default=0)  # 0 = unlimited
    is_active = models.BooleanField(
        default=True
    )  # Is the course currently being offered?

    def validate_teacher_hours_dont_conflict(self):
        """
        Validate that the hours of the course instance don't conflict with the hours of the teacher's other courses.
        """
        for schedule in self.schedules.all():
            for other_schedule in self.teacher.courses.exclude(
                course_instances=self
            ).schedules.all():
                if (
                    schedule.day_of_week == other_schedule.day_of_week
                    and schedule.start_time < other_schedule.end_time
                    and schedule.end_time > other_schedule.start_time
                ):
                    return False

    @property
    def hours(self):
        """Returns the total hours of the course instance."""
        return sum([s.duration().seconds / 3600 for s in self.schedules.all()])

    def __str__(self):
        return "{0} {1} {2}".format(
            self.course.name,
            self.teacher.user.username,
            self.start_date.strftime("%d/%m/%Y"),
        )


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
    course = models.ForeignKey(
        CourseInstance, on_delete=models.CASCADE, related_name="schedules"
    )
    day_of_week = models.CharField(max_length=1, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def duration(self):
        return self.end_time - self.start_time

    def __str__(self):
        return self.course.course.name + " " + self.day_of_week


class Enrollment(models.Model):
    """Represents a student's enrollment in a course instance."""

    student = models.ForeignKey(
        EduProfile, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        CourseInstance, on_delete=models.CASCADE, related_name="enrollments"
    )
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
