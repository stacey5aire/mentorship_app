from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    nationality = models.CharField(max_length=50)
    dob = models.DateField(null=True, blank=True)  # Allow null values
    password = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)
    bio = models.CharField(max_length=250, null=True)
    dob = models.DateField()
    address = models.CharField(max_length=255)  # Added max_length
    telephone = models.CharField(max_length=50)
    expertise = models.CharField(max_length=255, null=True, blank=True)
    availability = models.CharField(max_length=15, null=True, blank=True)
    role_choices = [
        ("1", "Admin"),
        ("2", "Mentor"),
        ("3", "Mentee"),
    ]
    role = models.CharField(max_length=1, choices=role_choices)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    id = models.AutoField(primary_key=True)
    last_login = models.DateTimeField(default=timezone.now)  # Added field
    is_active = models.BooleanField(default=True)  # Added field
    is_staff = models.BooleanField(default=False)  # Added field

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Fields required for creating a user


    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.email}, {self.role}"

class MentorshipMatch(models.Model):
    mentor = models.ForeignKey(
        User, related_name="mentor_matches", on_delete=models.CASCADE
    )
    mentee = models.ForeignKey(User, on_delete=models.CASCADE)
    match_date = models.DateTimeField(auto_now_add=True)
    status_choices = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(
        max_length=10, choices=status_choices, default="pending")

    def __str__(self):
        return f"({self.mentor} -> {self.mentee}, {self.status}, ID->{self.mentor})"

class Message(models.Model):
    sender = models.ForeignKey(
        User, related_name="sent_messages", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="received_messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    file = models.FileField(
        upload_to="message_files/", blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.sent_at}"

class Notification(models.Model):
    sent_by = models.ForeignKey(
        User, related_name='notifications_sent', on_delete=models.CASCADE)  # Added related_name
    received_by = models.ForeignKey(
        # Added related_name
        User, related_name='notifications_received', on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.received_by}, read: {self.is_read}, at {self.created_at}"

class Schedule(models.Model):
    mentor = models.ForeignKey(
        User, related_name="mentor_schedules", on_delete=models.CASCADE
    )
    mentee = models.ForeignKey(
        User, related_name="mentee_schedules", on_delete=models.CASCADE
    )
    session_date = models.DateTimeField()
    status_choices = [
        ("scheduled", "Scheduled"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]
    status = models.CharField(
        max_length=10, choices=status_choices, default="scheduled"
    )

    def __str__(self):
        return f"Schedule: {self.mentor} with {self.mentee} on {self.session_date}, status: {self.status}"

class Progress(models.Model):
    session_number = models.AutoField(primary_key=True)
    mentor = models.ForeignKey(
        User, related_name="progress_mentor", on_delete=models.CASCADE
    )
    mentee = models.ForeignKey(
        User, related_name="progress_mentee", on_delete=models.CASCADE, blank=True, null=True
    )
    progress_percentage = models.CharField(
        max_length=255, blank=True, null=True)

    def __str__(self):
        return f"'session_number':{self.session_number}, 'mentee':{self.mentee.id if self.mentee else 'N/A'},'mentor_id:'{self.mentor.id}, progress_percentage:{self.progress_percentage}"

class Goals(models.Model):
    id = models.AutoField(primary_key=True)
    goal_id = models.ForeignKey(
        Progress, related_name="session_goals", on_delete=models.CASCADE, blank=True, null=True)
    goal = models.CharField(max_length=255)
    status = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Goal: {self.goal}, Status: {self.status}, Session Number: {self.goal_id.session_number if self.goal_id else 'N/A'}"

class Evaluation(models.Model):
    mentorship_match = models.ForeignKey(MentorshipMatch, on_delete=models.CASCADE)
    mentor = models.ForeignKey(User, related_name="mentor_evaluations", on_delete=models.CASCADE)
    mentee = models.ForeignKey(User, related_name="mentee_evaluations", on_delete=models.CASCADE)
    evaluation_date = models.DateTimeField(auto_now_add=True)
    support = models.CharField(max_length=20)
    communication = models.CharField(max_length=20)
    confidence = models.CharField(max_length=20)
    career = models.CharField(max_length=20)
    understanding = models.CharField(max_length=20)
    comfort = models.CharField(max_length=3)
    goals = models.CharField(max_length=3)
    recommend = models.CharField(max_length=3)
    resources = models.CharField(max_length=3)
    additional_resources = models.TextField(blank=True, null=True)
    additional_comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Evaluation: {self.mentor} evaluated {self.mentee} on {self.evaluation_date}"# New Model

class MenteeChallenge(models.Model):
    mentee = models.ForeignKey(User,  related_name="mentee", on_delete=models.CASCADE)
    mentor = models.ForeignKey(User, default="14" ,related_name="mentor", on_delete=models.CASCADE)
    challenge = models.CharField(max_length=255)
    session_no = models.CharField(max_length=255)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mentee.username}: {self.challenge}"
