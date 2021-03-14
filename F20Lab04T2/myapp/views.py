import secrets
from datetime import datetime

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

# Import necessary classes
from django.http import HttpResponse, HttpResponseRedirect, response
from django.template import RequestContext
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.views import View

from F20Lab04T2 import settings
from .forms import SearchForm, OrderForm, ReviewForm, RegisterForm, UploadImageForm
from .models import Topic, Course, Student, Order, Review

# Create your views here.
"""
def index(request):
    top_list = Topic.objects.all().order_by('id')[:10]
    course_list = Course.objects.all().order_by('-title')[:5]
    response = HttpResponse()
    heading1 = '<p><b><u>' + 'List of topics' + '</u></b>: </p>'
    response.write(heading1)
    for topic in top_list:
        para = '<p>' + str(topic.id) + ': ' + str(topic) + '</p>'
        response.write(para)
    heading2 = '<p><b><u>' + 'List of Courses' + '</u></b>: </p>'
    i = 1
    response.write(heading2)
    for course in course_list:
        para = '<p>' + str(i) + ': ' + str(course) + '&emsp;: &emsp;<i>$' + str(course.price) + '</i></p>'
        response.write(para)
        i = i + 1
    return response
"""

"""
def index(request):
    top_list = Topic.objects.all().order_by('id')[:10]
    return render(request, 'myapp/index1.html',
                  {'top_list': top_list, 'last_login': request.session.get('last_login', False)})
"""


class index(View):
    def get(self, request):
        last_login = 'You are logged out'
        if request.session.get('last_login', False):
            last_login = request.session.get('last_login', False)
        else:  # you are not logged in
            pass
        top_list = Topic.objects.all().order_by('id')[:10]
        return render(request, 'myapp/index1.html', {
            'top_list': top_list,
            'last_login': last_login,
        })


"""
def about(request):
    abt = '<p><center><b>This is an E-learning Website! Search our Topics to find all available ' \
          'Courses.</b></center></p> '
    return HttpResponse(abt)
"""


def about(request):
    visits = request.COOKIES.get('about_visits')
    if visits:
        visits = int(visits) + 1
    else:
        visits = 1
    response = render(request, 'myapp/about1.html', {'visits': visits})
    response.set_cookie('about_visits', visits, expires=300)
    return response


"""
def detail(request, topic_id):
    # topic = Topic.objects.get(id=topic_id)
    topic = get_object_or_404(Topic, id=topic_id)
    head = '<p><b><u>' + 'Topics id</b></u>: ' + str(topic.id) + '</p>'
    t_name = '<p><b><u>Topic Name</u></b>: ' + str(topic.name).upper() + ' &emsp; <b><u>Length</u></b>: ' + str(
        topic.length) + '</p>'
    course_list = Course.objects.filter(topic=topic_id)
    head1 = '<p><b><u>' + 'List of Courses in ' + str(topic.name) + '</u></b>:</p>'
    a = 1
    response = HttpResponse()
    response.write(head)
    response.write(t_name)
    response.write(head1)
    for course in course_list:
        para = '<p>' + str(a) + ': ' + str(course) + '&emsp;: &emsp;<i>$' + str(course.price) + '</i></p>'
        response.write(para)
        a = a + 1
    return response
"""

"""
def detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    course_list = Course.objects.filter(topic=topic_id)
    return render(request, 'myapp/detail1.html', {'topic': topic, 'course_list': course_list})
"""


class detail(View):
    def get(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        course_list = Course.objects.filter(topic=topic_id)
        return render(request, 'myapp/detail1.html', {'topic': topic, 'course_list': course_list})


def findcourses(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            max_price = form.cleaned_data['max_price']
            length = form.cleaned_data['length']
            if form.cleaned_data['length']:
                topics = Topic.objects.filter(length=length)
            else:
                topics = Topic.objects.all()
            courselist = []
            for top in topics:
                courselist = courselist + list(top.courses.filter(price__lte=max_price))
            return render(request, 'myapp/results.html',
                          {'courselist': courselist, 'name': name, 'length': length, 'max_price': max_price})
        else:
            return HttpResponse('Invalid data')
    else:
        form = SearchForm()
        return render(request, 'myapp/findcourses.html', {'form': form})


def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            courses = form.cleaned_data['courses']
            order = form.save()
            student = order.student
            status = order.order_status
            order.save()
            if status == 1:
                for c in order.courses.all():
                    student.registered_courses.add(c)
            return render(request, 'myapp/order_response.html', {'courses': courses, 'order': order})
        else:
            return render(request, 'myapp/place_order.html', {'form': form})

    else:
        form = OrderForm()
        return render(request, 'myapp/place_order.html', {'form': form})


def order_response(request):
    return render(request, 'myapp/order_response.html')


@login_required
def review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if request.user.is_authenticated:
            student = Student.objects.get(id=request.user.id)
            if student.level == 'UG' or student.level == 'PG':
                if form.is_valid():
                    course = form.cleaned_data['course']
                    rating = form.cleaned_data['rating']
                    reviewer = form.cleaned_data['reviewer']
                    comments = form.cleaned_data['comments']
                    review = Review(course=course, reviewer=reviewer, rating=rating, comments=comments)
                    if 1 <= rating <= 5:
                        course.num_reviews = course.num_reviews + 1
                        course.save()
                        review.save()
                        return HttpResponseRedirect('/myapp')
                    else:
                        form.add_error('rating', 'You must enter a rating between 1 and 5')
                        return render(request, 'myapp/review.html', {'form': form})
                else:
                    return render(request, 'myapp/review.html', {'form': form})
            else:
                form.add_error('reviewer',
                               'You must be registered in Undergraduate or Post graduate to submit review')
                return render(request, 'myapp/review.html', {'form': form})
    else:
        form = ReviewForm()
        return render(request, 'myapp/review.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('myapp:user_login')

    form = RegisterForm()
    return render(request, 'myapp/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)

                request.session['last_login'] = str(timezone.now().isoformat('T', 'seconds'))
                request.session.set_expiry(3600)
                if 'next' in request.POST:
                    return redirect('myapp:' + request.POST.get('next'))
                return HttpResponseRedirect(reverse('myapp:myaccount'))

                # return HttpResponseRedirect(reverse('myapp:index'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        return render(request, 'myapp/login.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('myapp:index'))


@login_required(login_url='/myapp/login')
def myaccount(request):
    if 'last_login' in request.session:
        try:
            user = Student.objects.get(id=request.user.id)
        except Student.DoesNotExist:
            user = None

        if user:
            stud_course = user.registered_courses.all()
            interested = user.interested_in.all()

            if request.method == 'POST':
                form = UploadImageForm(request.POST, request.FILES)
                if form.is_valid():
                    user.image = form.cleaned_data.get('image')
                    user.save()
                    return render(request, 'myapp/myaccount.html',
                                  {'user': user, 'interested': interested, 'stud_course': stud_course, 'form': form})
            else:
                form = UploadImageForm()
                return render(request, 'myapp/myaccount.html',
                              {'user': user, 'interested': interested, 'stud_course': stud_course, 'form': form})
        else:
            msg = "You are not a registered student!"
            return render(request, 'myapp/myaccount.html', {'msg': msg})
    else:
        msg = "Please log in!"
        return render(request, 'myapp/myaccount.html', {'msg': msg})


@login_required
def myorders(request):
    if request.user.is_authenticated:
        student = Student.objects.get(id=request.user.id)
        if student:
            user = get_object_or_404(Student, pk=request.user.id)
            order_list = Order.objects.select_related().filter(student_id=user)
            if order_list.exists():
                return render(request, 'myapp/myorders.html', {'user': user, 'order_list': order_list})
            else:
                return HttpResponse("You have not ordered anything yet")
        else:
            return HttpResponse("User not found")
    else:
        return HttpResponse("You are not registered as a student")
