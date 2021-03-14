from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.

from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone


class Topic(models.Model):
    name = models.CharField(max_length=200)
    length = models.CharField(default=12, blank=False, max_length=10)

    def __str__(self):
        return self.name


def validate_price(value):
    if value < 50 or value > 500:
        raise ValidationError(('%(value)s should be between $50 and $500'), params={'value': value}, )


class Course(models.Model):
    title = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, related_name='courses', on_delete=models.CASCADE)
    price = models.DecimalField(validators=[validate_price], max_digits=10, decimal_places=2)
    for_everyone = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    num_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Student(User):
    LVL_CHOICES = [
        ('HS', 'High School'),
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
        ('ND', 'No Degree'),
    ]

    level = models.CharField(choices=LVL_CHOICES, max_length=2, default='HS')
    address = models.CharField(max_length=200, blank=True)
    province = models.CharField(max_length=2, default='ON')
    registered_courses = models.ManyToManyField(Course, blank=True)
    interested_in = models.ManyToManyField(Topic)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return self.get_full_name()


class Order(models.Model):
    CHOICES = [
        ('0', 'Cancelled'),
        ('1', 'Confirmed'),
        ('2', 'On Hold')
    ]

    courses = models.ManyToManyField(Course)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    order_status = models.CharField(choices=CHOICES, default='1', max_length=2)
    order_date = models.DateField(default=timezone.now(), null=True, blank=True)

    def __str__(self):
        return self.student.get_full_name()

    def total_cost(self):
        return self.courses.aggregate(total=Sum('price'))['total']

    def total_items(self):
        return self.courses.count()


class Review(models.Model):
    reviewer = models.EmailField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comments = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.reviewer
