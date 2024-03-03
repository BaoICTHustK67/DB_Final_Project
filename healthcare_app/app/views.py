from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db.models import Q,Count, Sum, F
from django.db import models
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import MyUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import User, Patient, Post, Comment, Category, Doctor, Appointment, Service, Membership, Payment, Room
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta



# Create your views here.
def home(request):
    return render(request, 'app/home.html')

def developing(request):
    return HttpResponse('')

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email or Password does not correct')

    context = {'page':page}
    return render(request, 'app/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def signup(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        email = request.POST.get('email')
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save() 
            login(request, user)
            membership = Membership.objects.filter(membership_id=1)[0]
            new_patient = Patient.objects.create(user=request.user, membership=membership)
            return redirect('home')
        else:
            messages.error(request," An error occured during registration ")
            return render(request,'app/signup.html', {'form':form})

    context = {'form':form}
    return render(request, 'app/signup.html', context)

def bookingPage(request):
    if request.user.is_authenticated:
        service_count = Service.objects.annotate(total=Count('doctor')).values('service_id','service_name', 'total')
        user = User.objects.get(id=request.user.id)
        current_date = datetime.now().strftime('%Y-%m-%d')
        next_year = (timedelta(days=365) + datetime.now()).strftime('%Y-%m-%d')
        if request.method == 'POST':
            date = request.POST.get('date')
            time = request.POST.get('time')
            email = request.POST.get('email')
            service = request.POST.get('service')
            symtomps = request.POST.get('textarea')
            service = Service.objects.all().filter(service_id=service)[0]
            context = {
                "date":date,
                "time":time,
                "email":email,
                "service":service,
                "symtomps":symtomps,
            }

            booking_info = {
                "date":date,
                "time":time,
                "email":email,
                "service_name":service.service_name,
                "service_id":service.service_id,
                "service_price":float(service.price),
                "symtomps":symtomps,
            }
            request.session['booking_info'] = {
                "booking_info":booking_info,
            }
            request.session.save()
            return redirect('bookingCheck')
        else:
            context = {
                "service_count":service_count,
                "user":user,
                "current_date":current_date,
                "next_year":next_year,
            }
        return render(request, 'app/booking_page.html', context)
    else:
        return redirect('login')

def bookingCheck(request):
    if request.user.is_authenticated:
        booking_info = request.session.get('booking_info', None)
        service = Service.objects.filter(service_name=booking_info['booking_info']['service_name'])
        doctor = Doctor.objects.filter(Q(status=1) & Q(service=service[0]))[:1]
        room = Room.objects.filter(status=1)[:1]
        print(room)
        if request.method == 'POST':
            new_appointment = Appointment.objects.create(appointment_date=booking_info['booking_info']['date'],
                                        start_time=booking_info['booking_info']['time'],
                                        status=2,
                                        doctor=doctor[0],
                                        patient=request.user.patient,
                                        service=service[0],
                                        room_id=room[0],
                                        ).appointment_id
            room[0].status = 2
            doctor[0].status = 2
            doctor[0].save()
            room[0].save()
            request.session['appointment_id'] = new_appointment
            request.session.save()
            return redirect('bookingPayment')
        
        return render(request, 'app/booking_check.html',booking_info)
    else:
        return redirect('login')
   

def bookingPayment(request):
    if request.user.is_authenticated:
        booking_info = request.session.get('booking_info', None)
        service_name = booking_info['booking_info']['service_name']
        price = Service.objects.filter(service_id=booking_info['booking_info']['service_id']).values('price')[0]['price']
        membership = Patient.objects.filter(user__email=booking_info['booking_info']['email'])[0].membership
        membership_type = membership.type
        membership_percent = membership.discount_percent
        discount = int(price)*membership_percent/100.0 
        vat = int(price) * 0.05
        bill = int(price) - vat - discount
        print(membership)
        context = {
            'price': price,
            'membership_type': membership_type,
            'discount': discount,
            'vat': vat,
            'bill': bill,
            'service_name': service_name,
        }
        appointment = Appointment.objects.filter(appointment_id=request.session.get('appointment_id'))[0]
        Payment.objects.create(appointment_id=appointment, status=1)
        return render(request, 'app/booking_payment.html', context)
    else:
        return redirect('login')

def bookingSuccess(request):
    if request.user.is_authenticated:
        appointment_id = request.session['appointment_id']
        return render(request, 'app/booking_success.html', {'appointment_id':appointment_id})
    else:
        return redirect('login')

@login_required(login_url='login')    
def patientProfile(request, pk):
    time_now = datetime.now()
    edit = False
    edit_2 = False
    user = User.objects.get(id=pk)
    patient = Patient.objects.get(user_id=request.user.id)
    lastname = patient.lastname or ''
    contact_number = patient.contact_number or ''
    cccd = patient.cccd
    firstname = patient.firstname or ''
    address = patient.address or ''
    dob = patient.dob or ''
    bmi = patient.bmi or ''
    weight = patient.weight or ''
    height = patient.height or ''
    bloodpressure = patient.blood_pressure or ''
    gender = patient.gender or 1
    email = request.user.email 

    print(1)

    if request.user.is_authenticated:
        if request.POST.get('value') == 'edit':
            edit = True
        else:
            edit = False
            if request.POST.get('value') == 'save':
                gender = int(request.POST.get('gender'))
                address = request.POST.get('address') 
                dob = request.POST.get('dob') 
                bmi = request.POST.get('bmi') 
                weight = request.POST.get('weight') 
                height = request.POST.get('height') 
                bloodpressure = request.POST.get('bloodpressure')
                firstname = request.POST.get('firstname')
                lastname = request.POST.get('lastname')
                patient.address = address
            if dob == "" :
                    dob = '2004-01-01'
            patient.dob = dob
            if bmi == "" :
                    bmi = None
            patient.bmi = bmi
            if weight == "" :
                    weight = None
            patient.weight = weight
            if height == "" :
                    height = None
            patient.height = height
            if bloodpressure == "" :
                    bloodpressure = None
            patient.blood_pressure = bloodpressure
            user.first_name = firstname
            user.last_name = lastname
            patient.firstname = firstname
            patient.lastname = lastname
            patient.save()
            user.save()

        if request.POST.get('value') == 'edit_2':
            edit_2 = True
        else:
            edit_2 = False
            if request.POST.get('value') == 'save_2':
                contact_number = request.POST.get('contact_number')
                email = request.POST.get('email')
                cccd = request.POST.get('cccd')
                address = request.POST.get('address')
                patient.contact_number = contact_number
                patient.address = address
                patient.cccd  = cccd 
                patient.save()
        
        appointments = Appointment.objects.filter(patient=patient).order_by('appointment_date').all()[:30] or ''

        context = { 'gender':gender,
                    'user':user,
                    'edit':edit,
                    'edit_2':edit_2,
                    'lastname':lastname,
                    'firstname':firstname,
                    'address':address,
                    'contact_number':contact_number,
                    'cccd': cccd,
                    'dob':dob,
                    'bmi':bmi,
                    'weight':weight,
                    'height':height,
                    'bloodpressure': bloodpressure,
                    'email': request.user.email,
                    'appointments': appointments,
                    'time_now': time_now,
                }
        
        return render(request, 'app/patient_profile.html', context)
    else:
        return redirect('login')
    
@login_required(login_url='login')
def patientHistory(request,pk):
    if request.user.is_authenticated:
        patient = Patient.objects.get(user_id=pk)
        appointments = Appointment.objects.filter(patient=patient).all()[:30] or ''

        if request.method == 'POST':
            date = request.POST.get('date')
            if date != "":
                appointments = Appointment.objects.filter(Q(appointment_date=date) & Q(patient=patient))[:30] or ''

        context = {
            'appointments': appointments
        }
        return render(request, 'app/patient_history.html', context)
    else:
        return redirect('login')
    

@login_required(login_url='login')    
def doctorProfile(request, pk):
    
    edit = False
    edit_2 = False
    user = User.objects.get(id=pk)
    doctor = Doctor.objects.get(user_id=request.user.id)
    dob = doctor.dob or ''
    lastname = doctor.lastname or ''
    contact_number = doctor.contact_number or ''
    cccd = doctor.cccd
    firstname = doctor.firstname or ''
    address = doctor.address or ''
    gender = doctor.gender or 1
    email = request.user.email 



    if request.user.is_authenticated:
        if request.POST.get('value') == 'edit':
            edit = True
        else:
            edit = False
            if request.POST.get('value') == 'save':
                gender = int(request.POST.get('gender'))
                address = request.POST.get('address') 
                dob = request.POST.get('dob') 
                firstname = request.POST.get('firstname')
                lastname = request.POST.get('lastname')
                doctor.address = address
            if dob == "" :
                    dob = '2004-01-01'


            # user.first_name = firstname
            # user.last_name = lastname
            doctor.firstname = firstname
            doctor.lastname = lastname
            doctor.save()
            user.save()

        if request.POST.get('value') == 'edit_2':
            edit_2 = True
        else:
            edit_2 = False
            if request.POST.get('value') == 'save_2':
                contact_number = request.POST.get('contact_number')
                email = request.POST.get('email')
                cccd = request.POST.get('cccd')
                address = request.POST.get('address')
                doctor.contact_number = contact_number
                doctor.address = address
                doctor.cccd  = cccd 
                doctor.save()
        
        appointments = Appointment.objects.filter(doctor=doctor).all()[:30] or ''

        context = { 'gender':gender,
                    'user':user,
                    'edit':edit,
                    'edit_2':edit_2,
                    'lastname':lastname,
                    'firstname':firstname,
                    'address':address,
                    'contact_number':contact_number,
                    'cccd': cccd,
                    'dob':dob,
                    'email': request.user.email,
                    'appointments': appointments,
                    'doctor':doctor
                }
        
        return render(request, 'app/doctor_profile.html', context)
    else:
        return redirect('login')


@login_required(login_url='login')
def doctorWork(request, pk):
    if request.user.is_authenticated:
        doctor = Doctor.objects.get(user_id=pk)
        appointments = Appointment.objects.filter(doctor=doctor).all()[:30] or ''

        if request.method == 'POST':
            date = request.POST.get('date')
            if date != "":
                appointments = Appointment.objects.filter(Q(appointment_date=date) & Q(doctor=doctor))[:30] or ''

        context = {
            'appointments': appointments
        }
        return render(request, 'app/doctor_work.html', context)
    else:
        return redirect('login')

@login_required(login_url='login')   
def paymentHistory(request, pk):
    if request.user.is_authenticated:
        patient = Patient.objects.get(user_id=pk)
        appointments = Appointment.objects.filter(patient=patient).all()[:30] or ''

        if request.method == 'POST':
            payment_id = request.POST.get('id')
            if payment_id != '':
                appointments = Appointment.objects.filter(Q(appointment_id=payment_id) | Q(appointment_id__icontains=payment_id) & Q(patient=patient))[:30]

        context = {
            'appointments': appointments
        }
        return render(request, 'app/payment_history.html', context)
    else:
        return redirect('login')
    
@login_required(login_url='login')    
def appointmentDetail(request,pk):
    if request.method == 'redirect':
        appointment_id = request.session['appointment_id']
    else:
        appointment_id = pk
    appointment = Appointment.objects.filter(appointment_id=appointment_id)[0]
    # service_name = booking_info['booking_info']['service_name']
    price = appointment.service.price
    # membership = Patient.objects.filter(user__email=booking_info['booking_info']['email'])[0].membership
    # membership_type = membership.type
    membership_percent = appointment.patient.membership.discount_percent
    discount = int(price)*membership_percent/100.0 
    vat = int(price) * 0.05
    bill = int(price) - vat - discount

    if request.method == 'POST':
        if request.POST.get('finish') == "finish":
            appointment.status = 1
            appointment.save()
            return redirect('adminAppointment')
        

    context = { 
        'appointment':appointment,
    }
    return render(request, 'app/appointment_detail.html', {'appointment':appointment,
                                                           'discount': discount,
                                                           'vat':vat,
                                                           'bill':bill})

@login_required(login_url='login')    
def blog(request):
    posts = Post.objects.select_related('author')
    user = User.objects.get(id=request.user.id)
    comments = Comment.objects.all()
    if request.POST.get('post') == 'post':
        description = request.POST.get('input')
        Post.objects.create(description=description,
                            author = user)
    if request.POST.get('comment') == 'comment':
        comment = request.POST.get('message')
        post_id = request.POST.get('post_id')
        cur_post = Post.objects.get(post_id=post_id)
        Comment.objects.create(body=comment, post=cur_post, user=request.user)
        
   
        

    context = {'posts':posts, 'comments':comments}

    return render(request, 'app/blog.html', context)

def admin(request):
    doctors_count = Doctor.objects.all().count()
    patients_count = Patient.objects.all().count()
    finished_appointment = Appointment.objects.filter(status=1).count()
    pending_appointment = Appointment.objects.filter(status=2).count()
    appointments = Appointment.objects.all().order_by('-appointment_date')[:30]

    one_month = timezone.now() - timedelta(days=30)
    two_month = timezone.now() - timedelta(days=60)
    three_month = timezone.now() - timedelta(days=90)
    four_month = timezone.now() - timedelta(days=120)
    sale_last_month = Service.objects.filter(appointment__created__gte=one_month).aggregate(total_sales=models.Sum('price'))
    sale_two_month = Service.objects.filter(Q(appointment__created__lt=one_month) & Q(appointment__created__gte=two_month)).aggregate(total_sales=models.Sum('price'))
    sale_three_month = Service.objects.filter(Q(appointment__created__lt=two_month) & Q(appointment__created__gte=three_month)).aggregate(total_sales=models.Sum('price'))
    sale_four_month = Service.objects.filter(Q(appointment__created__lt=three_month) & Q(appointment__created__gte=four_month)).aggregate(total_sales=models.Sum('price'))
    
    percent1 = sale_last_month['total_sales']/sale_four_month['total_sales']*15
    percent2 = sale_two_month['total_sales']/sale_four_month['total_sales']*15
    percent3 = sale_three_month['total_sales']/sale_four_month['total_sales']*15
    percent4 = sale_four_month['total_sales']/sale_four_month['total_sales']*15
    
    if request.method == 'POST':
        value = request.POST.get('filter')
        appointments = Appointment.objects.filter(Q(status__startswith=value) | Q(start_time__icontains=value)
                                                  | Q(status__icontains=value) | Q(start_time__startswith=value)
                                                  | Q(appointment_date__icontains=value) | Q(appointment_date__startswith=value))[:30]


    context =   {
                    "doctors_count": doctors_count,
                    "patients_count": patients_count,
                    "finished_appointment": finished_appointment,
                    "pending_appointment": pending_appointment,
                    "appointments": appointments,
                    "sale_last_month": sale_last_month,
                    "sale_two_month": sale_two_month,
                    "sale_three_month": sale_three_month,
                    "sale_four_month": sale_four_month,
                    "one_month": one_month ,
                    "two_month": two_month ,
                    "three_month": three_month,
                    "four_month":  four_month,
                    "percent1":  percent1,
                    "percent2":  percent2,
                    "percent3":  percent3,
                    "percent4":  percent4,
                }
    return render(request, 'app/admin.html', context)

def adminDoctor(request):
    doctors = Doctor.objects.all()[:30]
    doctors_count = Doctor.objects.all().count()
    doctors_active = Doctor.objects.filter(status=1).count()
    doctors_unactive = doctors_count - doctors_active
    services = Service.objects.all()
    service_count = Service.objects.annotate(total=Count('doctor')).values('service_name', 'total')
    specialize_count = []

    if request.method == 'POST':
        if request.POST.get('all') == 'all':
            doctors = Doctor.objects.all()[:30]
        elif request.POST.get('working') == 'working':
            doctors = Doctor.objects.all().filter(status=1)[:30]
        elif request.POST.get('not') == 'not':
            doctors = Doctor.objects.all().filter(status=2)[:30]
        else:
            value = request.POST.get('filter')
            doctors = Doctor.objects.filter(Q(firstname__startswith=value) | Q(firstname__icontains=value)
                                              |Q(lastname__startswith=value) |Q(lastname__contains=value))

    for doctor in doctors:
        specialize_count.append(Doctor.objects.filter(doctor_id=doctor.doctor_id).annotate(total=Count('service')).values('doctor_id','total')) 
    
    context = {
        "doctors":doctors,
        "doctors_count":doctors_count,
        "doctors_active":doctors_active,
        "doctors_unactive":doctors_unactive,
        "services":services,
        "service_count":service_count,
        "specialize_count":specialize_count,
    }

    return render(request, 'app/admin_doctor.html', context)

def adminPatient(request):
    patients = Patient.objects.all()[:30]
    patient_payment = []
    booking_numbers = []
    total_payment = Appointment.objects.filter(patient__isnull=False).aggregate(Sum('service__price'))['service__price__sum'] or 0

    gold  = Patient.objects.select_related('membership').filter(membership_id='3').count()
    silver  = Patient.objects.select_related('membership').filter(membership_id='2').count()
    bronze  = Patient.objects.select_related('membership').filter(membership_id='1').count()

    
    if request.method == 'POST':
        if request.POST.get('all') == 'all':
            patients = Patient.objects.all().order_by('patient_id')[:30]
        elif request.POST.get('a') == 'a':
            patients = Patient.objects.select_related('membership').filter(membership_id='3')[:30]
        elif request.POST.get('b') == 'b':
            patients = Patient.objects.select_related('membership').filter(membership_id='2')[:30]
        elif request.POST.get('c') == 'c':
            patients = Patient.objects.select_related('membership').filter(membership_id='1')[:30]
        else:
            value = request.POST.get('filter')
            patients = Patient.objects.filter(Q(firstname__startswith=value) | Q(firstname__icontains=value)
                                              |Q(lastname__startswith=value) |Q(lastname__contains=value))[:30]

    for patient in patients:
        patient_payment.append(Appointment.objects.filter(patient_id=patient.patient_id).aggregate(total_payment=models.Sum('service__price'))['total_payment'] or 0)  
        booking_numbers.append(Appointment.objects.filter(patient_id=patient.patient_id).aggregate(total_booking=models.Count('appointment_id'))['total_booking'] or 0)
    
    patients_count = Patient.objects.all().count()
    context = {
        "patients": patients,
        "patients_count": patients_count,
        "patient_payment": patient_payment,
        "booking_numbers": booking_numbers,
        "gold": gold,
        "silver": silver,
        "bronze": bronze,
    }
    return render(request, 'app/admin_patient.html', context)

def adminAppointment(request):
    appointments = Appointment.objects.all()[:30]
    appointment_count = Appointment.objects.all().count()
    appointment_finished = Appointment.objects.filter(status=1).count()
    appointment_processing = Appointment.objects.filter(status=2).count()
    appointment_pending = Appointment.objects.filter(status=3).count()


    one_month = timezone.now() - timedelta(days=30)
    two_month = timezone.now() - timedelta(days=60)
    three_month = timezone.now() - timedelta(days=90)
    four_month = timezone.now() - timedelta(days=120)
    order_last_month = Appointment.objects.filter(created__gte=one_month).aggregate(total_order=models.Count('*'))
    order_two_month = Appointment.objects.filter(Q(created__lt=one_month) & Q(created__gte=two_month)).aggregate(total_order=models.Count('*'))
    order_three_month = Appointment.objects.filter(Q(created__lt=two_month) & Q(created__gte=three_month)).aggregate(total_order=models.Count('*'))
    order_four_month = Appointment.objects.filter(Q(created__lt=three_month) & Q(created__gte=four_month)).aggregate(total_order=models.Count('*'))
    
    percent1 = order_last_month['total_order']/order_four_month['total_order']*15
    percent2 = order_two_month['total_order']/order_four_month['total_order']*15
    percent3 = order_three_month['total_order']/order_four_month['total_order']*15
    percent4 = order_four_month['total_order']/order_four_month['total_order']*15

    if request.method == 'POST':
        if request.method == 'POST':
            if request.POST.get('all') == 'all':
                appointments = Appointment.objects.all()[:30]
            elif request.POST.get('f') == 'f':
                appointments = Appointment.objects.filter(status=1)[:30]
            elif request.POST.get('p') == 'p':
                appointments = Appointment.objects.filter(status=2)[:30]
            elif request.POST.get('pen') == 'pen':
                appointments = Appointment.objects.filter(status=3)[:30]
            else:
                value = request.POST.get('filter')
                appointments = Appointment.objects.select_related('patient').filter(Q(appointment_id=value))[:30]

    context = {
        'appointments':appointments,
        'appointment_finished':appointment_finished,
        'appointment_processing':appointment_processing,
        'appointment_pending':appointment_pending,
        'appointment_count':appointment_count,
        'percent1':percent1,
        'percent2':percent2,
        'percent3':percent3,
        'percent4':percent4,
        "order_last_month": order_last_month,
        "order_two_month": order_two_month,
        "order_three_month": order_three_month,
        "order_four_month": order_four_month,
        "one_month": one_month ,
        "two_month": two_month ,
        "three_month": three_month,
        "four_month":  four_month,
    }
    return render(request, 'app/admin_appoinment.html', context)

def adminRoom(request):
    rooms = Room.objects.all()
    room_count = Room.objects.all().count()
    room_free = Room.objects.filter(status=1).count()
    room_inused = Room.objects.filter(status=2).count()
    room_stopped = Room.objects.filter(status=3).count()

    room_free__deg = (room_free / room_count) *360
    room_inused__deg = room_free__deg + (room_inused / room_count)*360
    room_stopped__deg = room_inused__deg + (room_stopped / room_count)*360

    if request.method == 'POST':
        if request.POST.get('all') == 'all':
            rooms = Room.objects.all()  
        elif request.POST.get('1') == '1':
            rooms = Room.objects.filter(status=1)
        elif request.POST.get('2') == '2':
            rooms = Room.objects.filter(status=2)
        elif request.POST.get('3') == '3':
            rooms = Room.objects.filter(status=3)
        else:
            value = request.POST.get('filter')
            rooms = Room.objects.filter(Q(room_name__contains=value) | Q(room_name__startswith=value)
                                            | Q(room_id__contains=value) | Q(room_id__startswith=value))[:4]

    context = {
        'rooms': rooms,
        'room_count': room_count,
        'room_free': room_free,
        'room_inused': room_inused,
        'room_stopped': room_stopped,
        'room_free__deg': room_free__deg,
        'room_inused__deg': room_inused__deg,
        'room_stopped__deg': room_stopped__deg,
    }
    return render(request, 'app/admin_room.html', context)

def adminService(request):
    services = Service.objects.all()
    total = Service.objects.all().count()
    service_running = Service.objects.filter(status=1).count()
    service_freezed = Service.objects.filter(status=2).count()
    service_pending = Service.objects.filter(status=3).count()


    if request.method == 'POST':
        if request.POST.get('all') == 'all':
            services = Service.objects.all()
        elif request.POST.get('running') == 'running':
            services = Service.objects.filter(status=1)
        elif request.POST.get('freezed') == 'freezed':
            services = Service.objects.filter(status=2)
        elif request.POST.get('pending') == 'pending':
            services = Service.objects.filter(status=3)
        else:
            value = request.POST.get('filter')
            services = Service.objects.filter(Q(service_name__contains=value) | Q(service_name__startswith=value)
                                         | Q(service_id__contains=value) | Q(service_id__startswith=value))[:4]

    context = {
        'total': total,
        'service_running': service_running,
        'service_freezed': service_freezed,
        'service_pending': service_pending,
        'services': services,
    }
    return render(request, 'app/admin_service.html', context)


def adminRoomDetail(request, pk):
    room = Room.objects.get(room_id=pk)

    rooms = Room.objects.all()
    room_count = Room.objects.all().count()
    room_free = Room.objects.filter(status=1).count()
    room_inused = Room.objects.filter(status=2).count()
    room_stopped = Room.objects.filter(status=3).count()

    lastest_appointment = Appointment.objects.filter(room_id=room.room_id).values('start_time', 'appointment_date').order_by('-appointment_date', '-start_time')[0]
    
    context = {
        'room_count': room_count,
        'room_free': room_free,
        'room_inused': room_inused,
        'room_stopped': room_stopped,
        'room':room,
        'lastest_appointment':lastest_appointment,
    }
    return render(request, 'app/admin_roomDetail.html', context)

def supportPage(request):
    time_now = datetime.now()
    return render(request, 'app/support_page.html', {'time_now': time_now,})

def serviceDetail(request, pk):
    service = Service.objects.get(service_id=pk)
    total = Service.objects.all().count()
    service_running = Service.objects.filter(status=1).count()
    service_freezed = Service.objects.filter(status=2).count()
    service_pending = Service.objects.filter(status=3).count()

    one_month = timezone.now() - timedelta(days=30)
    two_month = timezone.now() - timedelta(days=60)
    three_month = timezone.now() - timedelta(days=90)
    four_month = timezone.now() - timedelta(days=120)
    total_order = Appointment.objects.filter(Q(service=service)).aggregate(total_order=models.Count('*'))['total_order']
    order_last_month = Appointment.objects.filter(Q(created__gte=one_month) & Q(service=service)).aggregate(total_order=models.Count('*'))
    order_two_month = Appointment.objects.filter(Q(created__lt=one_month) & Q(created__gte=two_month) & Q(service=service)).aggregate(total_order=models.Count('*'))
    order_three_month = Appointment.objects.filter(Q(created__lt=two_month) & Q(created__gte=three_month) & Q(service=service)).aggregate(total_order=models.Count('*'))
    order_four_month = Appointment.objects.filter(Q(created__lt=three_month) & Q(created__gte=four_month) & Q(service=service)).aggregate(total_order=models.Count('*'))
    
    percent1 = order_last_month['total_order']/order_four_month['total_order']*15
    percent2 = order_two_month['total_order']/order_four_month['total_order']*15
    percent3 = order_three_month['total_order']/order_four_month['total_order']*15
    percent4 = order_four_month['total_order']/order_four_month['total_order']*15

    total_income = Appointment.objects.filter(Q(service=service)).aggregate(total_income=models.Sum('service__price'))['total_income']
    income_last_month = Appointment.objects.filter(Q(created__gte=one_month) & Q(service=service)).aggregate(total_income=models.Sum('service__price'))
    income_two_month = Appointment.objects.filter(Q(created__lt=one_month) & Q(created__gte=two_month) & Q(service=service)).aggregate(total_income=models.Sum('service__price'))
    income_three_month = Appointment.objects.filter(Q(created__lt=two_month) & Q(created__gte=three_month) & Q(service=service)).aggregate(total_income=models.Sum('service__price'))
    income_four_month = Appointment.objects.filter(Q(created__lt=three_month) & Q(created__gte=four_month) & Q(service=service)).aggregate(total_income=models.Sum('service__price'))

    percent_1 = income_last_month['total_income']/income_four_month['total_income']*15
    percent_2 = income_two_month['total_income']/income_four_month['total_income']*15
    percent_3 = income_three_month['total_income']/income_four_month['total_income']*15
    percent_4 = income_four_month['total_income']/income_four_month['total_income']*15

    context = {
        'service':service,
        'total':total,
        'service_running':service_running,
        'service_freezed': service_freezed,
        'service_pending': service_pending,
        'percent1':percent1,
        'percent2':percent2,
        'percent3':percent3,
        'percent4':percent4,
        "order_last_month": order_last_month,
        "order_two_month": order_two_month,
        "order_three_month": order_three_month,
        "order_four_month": order_four_month,
        "one_month": one_month ,
        "two_month": two_month ,
        "three_month": three_month,
        "four_month":  four_month,
        "total_order":  total_order,
        "income_last_month":  income_last_month,
        "income_two_month":  income_two_month,
        "income_three_month":  income_three_month,
        "income_four_month":  income_four_month,
        "percent_1":  percent_1,
        "percent_2":  percent_2,
        "percent_3":  percent_3,
        "percent_4":  percent_4,
        "total_income":  total_income,
    }
    return render(request, 'app/service_detail.html', context)
    

