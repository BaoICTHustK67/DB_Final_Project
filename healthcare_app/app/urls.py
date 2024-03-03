from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('developing/', views.developing, name='developing'),
    path('login/', views.loginPage, name='login'),
    path('signup/', views.signup, name='signup'),
    path('bookingPage/', views.bookingPage, name='bookingPage'),
    path('bookingCheck/', views.bookingCheck, name='bookingCheck'),
    path('bookingPayment/', views.bookingPayment, name='bookingPayment'),
    path('bookingSuccess/', views.bookingSuccess, name='bookingSuccess'),
    path('logout/', views.logoutUser, name='logout'),
    path('profile/<str:pk>', views.patientProfile, name='profile'),
    path('profile-history/<str:pk>', views.patientHistory, name='history'),
    path('profile-payment/<str:pk>', views.paymentHistory, name='payment'),
    path('doctor-profile/<str:pk>', views.doctorProfile, name='doctorProfile'),
    path('doctor-work/<str:pk>', views.doctorWork, name='doctorWork'),
    path('appointment-detail/<str:pk>', views.appointmentDetail, name='appointmentDetail'),
    path('blog/', views.blog, name='blog'),
    path('admin+/', views.admin, name='admin+'),
    path('adminDoctor/', views.adminDoctor, name='adminDoctor'),
    path('adminPatient/', views.adminPatient, name='adminPatient'),
    path('adminRoom/', views.adminRoom, name='adminRoom'),
    path('adminService/', views.adminService, name='adminService'),
    path('adminAppointment/', views.adminAppointment, name='adminAppointment'),
    path('supportPage/', views.supportPage, name='supportPage'),
    path('adminService/serviceDetail/<str:pk>', views.serviceDetail, name='serviceDetail'),
    path('adminRoom/adminRoomDetail/<str:pk>', views.adminRoomDetail, name='adminRoomDetail'),
]