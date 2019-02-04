from django.shortcuts import render, HttpResponse, redirect
from . models import *
from datetime import datetime
from django.contrib import messages
import bcrypt

def index(request):

	return render(request, "timesheets/index.html")

def create(request):
	errors = User.objects.basic_validator(request.POST)
	if len(errors):
		for key, value in errors.items():
			messages.add_message(request, messages.ERROR, value, extra_tags='register')
		return redirect('/')
	else:
		password = request.POST['password']
		password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
		user = User.objects.create(first_name= request.POST['first_name'], last_name = request.POST['last_name'], email= request.POST['email'], password= password)
		if user == User.objects.first():
			print(user)
			user.user_level = 9
			user.save()
			print(user.user_level)

			request.session['email'] = request.POST['email']
			request.session['user_id'] = user.id
			request.session['user_level'] = user.user_level
			return redirect('/adminDash')
		else:
			request.session['email'] = request.POST['email']
			request.session['user_id'] = user.id 
			request.session['user_level'] = user.user_level
			return redirect('/userDash')

def clockin(request):
    print(request.session['user_id'])
    Day.objects.create(user_id = request.session['user_id'])
    if request.session['user_level'] == 1:
        return redirect('/userDash')
    elif request.session['user_level'] == 9:
        return redirect('/adminDash')
    

def clockout(request):
    print(request.session['user_level'])
    errors = Day.objects.basic_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.add_message(request, messages.ERROR, value, extra_tags='clock')
            if request.session['user_level'] == 1:
                return redirect('/userDash')
            elif request.session['user_level'] == 9:
                return redirect('/adminDash')
    else:
        day = Day.objects.filter(user_id=request.session['user_id']).last()
        print('day is', day.__dict__)
        day.clock_out = datetime.strptime(request.POST['date'] + " " + request.POST['time'], "%Y-%m-%d %H:%M")
        print(day.clock_out)
        print("*"*90)
        print(day.clock_out)
        print(day.clock_in)
        day.hours = (day.clock_out - day.clock_in).seconds//3600
        day.save()
        return redirect(''+request.POST['day_id']+'/dailyReports')


def clockoutnow(request):
    day = Day.objects.filter(user_id=request.session['user_id']).last()
    print('day is', day.__dict__)
    day.clock_out = datetime.now()
    day.hours = (day.clock_out - day.clock_in).seconds//3600
    day.save()
    return redirect(''+request.POST['day_id']+'/dailyReports')

def update(request):
	errors = Report.objects.basic_validator(request.POST)
	if len(errors):
		for key, value in errors.items():
			messages.add_message(request, messages.ERROR, value, extra_tags='report')
		return redirect('/dailyReports')
	else:
		report = Report.objects.create(task= request.POST['task'], notes = request.POST['notes'], assist = request.POST['assist'], user_id = request.session['user_id'], day_id = request.POST['day_id'] )
		if request.session['user_level'] == 1:
			return redirect('/userDash')
		elif request.session['user_level'] == 9:
			return redirect('/adminDash')

def login(request):
	errors = User.objects.login_validator(request.POST)
	if len(errors):
		for key, value in errors.items():
			messages.add_message(request, messages.ERROR, value, extra_tags= "login")
			return redirect('/')
	else:
		request.session['email'] = request.POST['logemail']
		request.session['user_id'] = User.objects.get(email= request.POST['logemail']).id
		print('user id is:', request.session['user_id'])
		if User.objects.get(email= request.POST['logemail']).user_level == 9:
			request.session['user_level'] = User.objects.get(email= request.POST['logemail']).user_level
			return redirect('/adminDash')
		else: 
			request.session['user_level'] = User.objects.get(email= request.POST['logemail']).user_level
			return redirect('/userDash')

def adminDash(request):
	if request.session['user_id'] == 0:
		return redirect('/')
	elif request.session['user_level'] == 1:
		return redirect('/userDash')
	print(request.session['user_level'])
	context = {
        "current_user": User.objects.get(id=request.session['user_id']),
        "users": User.objects.all(),
        "days": Day.objects.filter(user_id=request.session['user_id']).all(),
        "clocked" :Day.objects.filter(user_id=request.session['user_id']).last()
        } 
	return render(request,"timesheets/adminDash.html", context)

def userDash(request):
	if request.session['user_id'] == 0:
		return redirect('/')
	print(request.session['user_level'])
	context = {
		"time_spent" : Day.objects.filter,
        "current_user": User.objects.get(id=request.session['user_id']),
        "days": Day.objects.filter(user_id=request.session['user_id']).all(),
        "clocked" :Day.objects.filter(user_id=request.session['user_id']).last()
        } 
	return render(request, "timesheets/userDash.html", context)
def dailyReports(request, day_id):
	if request.session['user_id'] == 0:
		return redirect('/')
	context = {
		"day_id" : day_id
	}
	return render(request, "timesheets/dailyReports.html", context)

def manage(request):
	if request.session['user_id'] == 0:
		return redirect('/')
	elif request.session['user_level'] == 1:
		return redirect('/userDash')
	context = {
        "current_user": User.objects.get(id=request.session['user_id']),
        "users": User.objects.all(),
        "days": Day.objects.all(),
        }
	return render(request, "timesheets/manage.html", context)

def reports(request, user_id):
	if request.session['user_id'] == 0:
		return redirect('/')
	context = {
        "current_user": User.objects.get(id=request.session['user_id']),
        "users": User.objects.all(),
        "days": Day.objects.filter(user_id = user_id).all(),
        "this_user":  User.objects.get(id= user_id)
        } 
	return render(request, "timesheets/reports.html", context)

def settings(request):
	if request.session['user_id'] == 0:
		return redirect('/')
	context = {
        "current_user": User.objects.get(id=request.session['user_id']),
        "users": User.objects.all(),
        "days": Day.objects.all(),
        } 
	return render(request, "timesheets/settings.html", context)

def changeEmail(request):
	errors = User.objects.change_email_validator(request.POST)
	if len(errors):
		for key, value in errors.items():
			messages.add_message(request, messages.ERROR, value, extra_tags='email')
		return redirect('/settings')
	else:
		user = User.objects.get(id = request.session['user_id'])
		user.email = request.POST['email']
		user.save()
		messages.add_message(request, messages.SUCCESS, "You successfully updated your email!", extra_tags='email')
		return redirect('/settings')

def changeName(request):
	errors = User.objects.change_name_validator(request.POST)
	if len(errors):                                      
		for key, value in errors.items():
			messages.add_message(request, messages.ERROR, value, extra_tags='name')
		return redirect('/settings')
	else:
		user = User.objects.get(id = request.session['user_id'])
		user.first_name = request.POST['first_name']
		user.last_name = request.POST['last_name']
		user.save()    
		messages.add_message(request, messages.SUCCESS, "You successfully updated your name!", extra_tags='name')
		return redirect('/settings')

def resetPassword(request):
	errors = User.objects.change_password_validator(request.POST)
	if len(errors):
		for key, value in errors.items():
			messages.add_message(request, messages.ERROR, value, extra_tags='password')
		return redirect('/settings')
	else:
		user = User.objects.get(id = request.session['user_id'])
		newpassword = request.POST['newpassword']
		newpassword = bcrypt.hashpw(newpassword.encode(), bcrypt.gensalt())
		user.password = newpassword
		user.save()
		messages.add_message(request, messages.SUCCESS, "You successfully updated your password!", extra_tags='password')
	return redirect('/settings')

def toDash(request):
	if request.session['user_level'] == 9:
		return redirect('/adminDash')
	elif request.session['user_level'] == 1:
		return redirect('/userDash')

def level(request, id):
	print("employee id is", request.POST['user_id'])
	print(request.POST['role'])
	if request.POST['role'] == 'User':
		user = User.objects.get(id=request.POST['user_id'])
		user.user_level = 1
		user.save()
		return redirect('/manage')
	elif request.POST["role"] == 'Administrator':
		user = User.objects.get(id=id)
		user.user_level = 9
		user.save()
		return redirect('/manage')

def delete(request, id):
	print(request.POST['user_id'])
	User.objects.get(id=request.POST['user_id']).delete()
	return redirect('/manage')

def logout(request):
	request.session.clear()
	return redirect('/')
