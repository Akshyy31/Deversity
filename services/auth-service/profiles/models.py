from django.db import models

# Create your models here.

class DeveloperProfile(models.Model):
    user = models.OneToOneField(
        "user_app.User",
        on_delete=models.CASCADE,
        related_name="developer_profile"
    )
    skills = models.JSONField(default=list)


class MentorProfile(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    user = models.OneToOneField(
        "user_app.User",
        on_delete=models.CASCADE,
        related_name="mentor_profile"
    )
    skills = models.JSONField(default=list)
    expertise_in = models.CharField(max_length=100)
    experience_proof = models.FileField(upload_to="mentor_proofs/")   # 
    verification_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
