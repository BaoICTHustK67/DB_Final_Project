from django.db import models
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        DOCTOR = "DOCTOR", 'Doctor'
        PATIENT = "PATIENT", 'Patient'

    base_role = Role.PATIENT

    role = models.CharField(max_length=50, choices=Role.choices, default=base_role)

    name = models.CharField(max_length=200, null=True, default='Edit your name')
    username = models.CharField(max_length=20, null=True)
    first_name = models.CharField(max_length=20, null=True)
    last_name = models.CharField(max_length=20, null=True)

    email = models.EmailField(unique=True)

    create_time = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Membership(models.Model):
    membership_id = models.CharField(primary_key=True, default="TYPE003")
    discount_percent = models.IntegerField(null=True)
    type = models.CharField(max_length=20, default=3)


class Patient(models.Model):
    patient_id = models.BigAutoField(primary_key=True, db_index=False)
    firstname = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=True)
    gender = models.IntegerField(null=True)
    membership = models.ForeignKey(Membership, null=True, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    dob = models.DateField(default='2004-01-01')
    contact_number = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=50, null=True)
    cccd = models.CharField(max_length=50, null=True)
    bmi = models.FloatField(max_length=20, null=True, blank=True)
    weight = models.FloatField(max_length=20, null=True, blank=True)
    height = models.FloatField(max_length=20, null=True, blank=True)
    blood_pressure = models.FloatField(max_length=20, null=True, blank=True)
    total_order = models.IntegerField(default=0)
    total_payment = models.IntegerField(default=0, null=True)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'
    
class Service(models.Model):
    service_id = models.CharField(max_length=8, primary_key=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    service_name = models.CharField(max_length=50, null=True)
    service_type = models.CharField(max_length=30, null=True)
    status = models.IntegerField(default=2)
    total_order = models.IntegerField(default=0)
    total_payment = models.IntegerField(default=0)
    lastbooking_date = models.DateField(null=True)

    def __str__(self):
        return self.service_id
    
class Doctor(models.Model):
    doctor_id = models.CharField(max_length=8, primary_key=True)
    firstname = models.CharField(max_length=50, null=True)
    lastname = models.CharField(max_length=50, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    address = models.CharField(max_length=50, null=True)
    cccd = models.CharField(max_length=50, null=True)
    contact_number = models.CharField(max_length=20, null=True)
    dob = models.DateField(null=True)
    gender = models.IntegerField(null=True)
    status = models.IntegerField(null=True, default=1)
    service = models.ManyToManyField(Service)   

    def __str__(self):
        return f'{self.firstname} {self.lastname}'
    
    
class Room(models.Model):
    room_id = models.CharField(max_length=8, primary_key=True)
    room_name = models.CharField(max_length=50, null=True)
    room_type = models.CharField(max_length=10, null=True)
    status = models.IntegerField(default=1)
    service = models.ForeignKey(Service, null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.room_name

    
class Appointment(models.Model):
    appointment_id = models.BigAutoField(primary_key=True)
    appointment_date = models.DateField(max_length=20, null=True)
    start_time = models.TimeField(null=True)
    status = models.IntegerField(null=True)
    doctor = models.ForeignKey(Doctor, null=True, on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, null=True, on_delete=models.DO_NOTHING)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    created = models.DateField(auto_now=True, null=True)

    def __int__(self):
        return self.appointment_id
    
class Payment(models.Model):
    appointment_id = models.OneToOneField(Appointment, on_delete=models.CASCADE, primary_key=True)
    payment_time = models.DateTimeField(null=True,auto_now=True)
    status = models.IntegerField(null=True)

    def __str__(self):
        return self.appointment_id


class Prescription(models.Model):
    appointment_id = models.OneToOneField(Appointment, on_delete=models.CASCADE, primary_key=True)
    date_prescribled = models.DateTimeField(null=True)
    dosage = models.CharField(max_length=50, null=True)
    instruction = models.TextField(null=True)

    def __str__(self):
        return self.appointment_id
    


class Category(models.Model):
    name = models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.name

class Post(models.Model):
    post_id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        ordering = ['-updated', '-created']

class Comment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']








    





