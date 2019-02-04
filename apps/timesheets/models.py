from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.db import models
from datetime import datetime
import bcrypt
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]*$')

class UserManager(models.Manager):
	def basic_validator(self, postData):
		errors = {}
		#first names
		if len(postData['first_name']) < 2:
			errors['first_name'] = "*Name field must be at least 2 characters long"
		elif not NAME_REGEX.match(postData['first_name']):
			errors['first_name'] = "*Name must not contain special characters or numbers"
		#last names
		if len(postData['last_name']) < 2:
			errors['last_name'] = "*Name field must be at least 2 characters long"
		elif not NAME_REGEX.match(postData['last_name']):
			errors['last_name'] = "*Name must not contain special characters or numbers"
		#Email
		if not EMAIL_REGEX.match(postData['email']):
			errors['email'] = "*Email must be in email format"
		elif User.objects.filter(email = postData['email']):
			errors['email'] = "*Email is already in the database"
		#Password
		if len(postData['password']) < 7:
			errors['password'] = "*Password must be atleast 8 character long"
		elif postData['repeat'] != postData['password']:
			errors['password'] = "*Password and Password Confirmation fields do not match"

		return errors

	def login_validator(self, postData):
		errors = {}

		if User.objects.filter(email = postData['logemail']):
			user = User.objects.get(email = postData['logemail'])

		else: 
			errors['logemail'] = "*Email is not in the database"
			return errors

		if not bcrypt.checkpw(postData['logpassword'].encode(), user.password.encode()):
			errors['logpassword'] = "*Email and password do not match"

		return errors

	def change_email_validator(self, postData):
		errors = {}
		if not postData['email']:
			errors['email'] = "*Email Field can't be empty"

		elif not EMAIL_REGEX.match(postData['email']):
			errors['email'] = "*Email must be in email format"

		elif User.objects.filter(email = postData['email']):
			errors['email'] = "*Email is already in the database"

		return errors
	
	def change_name_validator(self, postData):
		errors = {}
		#first names
		if not postData['first_name']:
			errors['first_name'] = "*First name cannot be empty"
		elif len(postData['first_name']) < 2:
			errors['first_name'] = "*Name field must be at least 2 characters long"
		elif not NAME_REGEX.match(postData['first_name']):
			errors['first_name'] = "*First name cannot contain special characters or numbers"
		#last names
		if not postData['last_name']:
			errors['last_name'] = "*Last name cannot be empty"
		elif len(postData['last_name']) < 2:
			errors['last_name'] = "*Name field must be at least 2 characters long"
		elif not NAME_REGEX.match(postData['last_name']):
			errors['last_name'] = "*Last name cannot contain special characters or numbers"
		return errors
	
	def change_password_validator(self, postData):
		errors = {}
		user = User.objects.get(id = postData['user_id'])
		if not postData['password']:
			errors['password'] ="*Current Password field cannot be empty"

		elif not bcrypt.checkpw(postData['password'].encode(), user.password.encode()):
			errors['password'] = "*Incorrect password"

		if not postData['newpassword']:
			errors['newpassword'] ="*New Password field cannot be empty"
		
		elif len(postData['newpassword']) < 7:
			errors['newpassword'] = "*New password must be atleast 8 character long"
		
		elif postData['repeat'] != postData['newpassword']:
			errors['newpassword'] = "*New password and Password Confirmation fields do not match"
		return errors

class ReportManager(models.Manager):
	def basic_validator(self, postData):
		errors = {}
        #tasks
		if len(postData['task']) < 2:
			errors['task'] = "*Name field must be at least 2 characters long"
		elif len(postData['task']) > 85:
			errors['first_name'] = "*Task field must be less than 85 characters long"
        #notes
		if len(postData['notes']) < 2:
			errors['notes'] = "*Notes field must be at least 2 characters long"
        #assistance
		if len(postData['assist']) < 2:
			errors['assist'] = "*Help field must be at least 2 characters long"

		return errors


class DayManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        day = Day.objects.filter(user_id=postData['user_id']).last()
        print(day.__dict__)
        if not postData['date']:
            errors['date'] = "Date field cannot be left blank!"
        elif postData['date'] > str(datetime.now()):
            errors['date'] = "Clock out time cannot be in the future"
        if not postData['time']:
            errors['time'] = 'Time field cannot be left blank'
        elif (postData['date'] + " " + postData['time']) > str(datetime.now()):
        	errors['date'] = "Clock out time cannot be in the future"
        elif (postData['date'] + " " + postData['time']) < str(day.clock_in):
            errors['date'] = "Clock out time cannot be before clock in time"
        
        return errors

class User(models.Model):
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	email= models.CharField(max_length=255)
	password= models.CharField(max_length=255)
	user_level = models.IntegerField(default= 1)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	objects = UserManager()

class Day(models.Model):
    clock_in = models.DateTimeField(auto_now_add=True)
    clock_out = models.DateTimeField(null=True)
    hours = models.IntegerField(null=True)
    date = models.DateField(auto_now_add= True, null=True)
    user = models.ForeignKey(User, related_name="days")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    objects = DayManager()

class Report(models.Model):
    user = models.ForeignKey(User, related_name="reports")
    task = models.CharField(max_length=85)
    notes = models.TextField()
    assist = models.TextField()
    day = models.OneToOneField(Day, related_name='report', null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    objects = ReportManager()
