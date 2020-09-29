from django.db import models

# Create your models here.
from django.db.models import fields


class People(models.Model):
    GENDER_MALE = "Male"
    GENDER_FEMALE = "Female"
    GENDER_UNDISCLOSED = "Undisclosed"

    GENDER_CHOICES = (
        (GENDER_MALE, GENDER_MALE),
        (GENDER_FEMALE, GENDER_FEMALE),
        (GENDER_UNDISCLOSED, GENDER_UNDISCLOSED),
    )

    birth_year = fields.CharField(max_length=10)
    eye_color = fields.CharField(max_length=10)
    gender = fields.CharField(
        choices=GENDER_CHOICES, default=GENDER_UNDISCLOSED, max_length=15
    )
    height = fields.IntegerField()
    mass = fields.CharField(max_length=5)
    name = fields.CharField(max_length=20, db_index=True)
    created = fields.DateTimeField(auto_created=True)
    edited = fields.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "People"


class Species(models.Model):
    average_height = models.FloatField()
    average_lifespan = models.PositiveIntegerField()
    classification = models.CharField(max_length=15)
    designation = models.CharField(max_length=20)
    eye_colors = models.CharField(max_length=100)
    hair_colors = models.CharField(max_length=100)
    skin_colors = models.CharField(max_length=100)
    language = models.CharField(max_length=15)
    name = models.CharField(max_length=20, db_index=True)
    url = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "Species"
