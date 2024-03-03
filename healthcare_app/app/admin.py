from django.contrib import admin
from .models import User, Appointment, Doctor, Patient, Payment, Prescription, Membership, Room, Service, Post, Comment, Category
# Register your models here.

admin.site.register(User)
admin.site.register(Appointment)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Payment)
admin.site.register(Prescription)
admin.site.register(Membership)
admin.site.register(Room)
admin.site.register(Service)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)
