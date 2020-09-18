from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from autoslug import AutoSlugField
from random import randint as rd
from django.urls import reverse

import falling_fruits.settings as settings
class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError('Users must have an email address')
		if not username:
			raise ValueError('Users must have a username')

		user = self.model(email=self.normalize_email(email),
			username=username,)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		user = self.create_user(email=self.normalize_email(email),
			password=password,
			username=username,)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user


class Account(AbstractBaseUser):
	email = models.EmailField(verbose_name="email", max_length=60, unique=True)
	username = models.CharField(max_length=30, unique=True)
	date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
	is_admin = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)


	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	objects = MyAccountManager()

	def __str__(self):
		return self.email

	# For checking permissions.  to keep it simple all admin have ALL permissons
	def has_perm(self, perm, obj=None):
		return self.is_admin

	# Does this user have permission to view this app?  (ALWAYS YES FOR
	# SIMPLICITY)
	def has_module_perms(self, app_label):
		return True

class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	contact = models.IntegerField(null=True)
	image = models.ImageField(default='default.jpg', upload_to='profile_pics')
	def __str__(self):
		return f'{self.user.username} Profile'

class Farm(models.Model):
	farm_name = models.CharField(max_length=15,unique=True,null=False)
	pin_code = models.IntegerField()
	address = models.TextField(max_length=50)
	def __str__(self):
		return f'{self.farm_name}'
	
	
CATEGORY_CHOICES = (('Fruit:Apple','Fruit:Apple'),
	('Fruit:Mango','Fruit:Mango'),
	('Fruit:Orange','Fruit:Orange'),
	('Fruit:Cocumber','Fruit:Cocumber'),
	('Vegetable:LadyFinger','Vegetable:LadyFinger'),
	('Vegetable:Tomato','Vegetable:Tomato'),
	('Vegetable:Patato','Vegetable:Patato'),
	('Grain','Grain'),
	('Cotton','Cotton'),
	('Raw Material','Raw Material'),
	('Spices','Spices'),)

class Product(models.Model):
	price = models.FloatField()
	category = models.CharField(max_length=20,choices=CATEGORY_CHOICES)
	farm = models.ForeignKey(Farm,on_delete=models.CASCADE)
	slug = AutoSlugField(populate_from='farm', unique=True)
	#get_absolute_url is used to take us on the product detail page
	def get_absolute_url(self):
		return reverse("customer:product-detail", kwargs={
			'slug': self.slug
		})
	def get_add_to_cart_url(self):
		return reverse("customer:add-to-cart", kwargs={
			'slug': self.slug
		})
	def get_remove_from_cart_url(self):
		return reverse("customer:remove-from-cart", kwargs={
			'slug': self.slug
		})

class OrderItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
							 on_delete=models.CASCADE)
	ordered = models.BooleanField(default=False)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	def __str__(self):
		return f"{self.quantity} of {self.product.category}"
	def get_total_item_price(self):
		return self.quantity * self.product.price

class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
							 on_delete=models.CASCADE)
	ref_code = models.CharField(max_length=20, blank=True, null=True)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	address = models.OneToOneField('Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
	#payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
	being_delivered = models.BooleanField(default=False)
	received = models.BooleanField(default=False)
	coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)

	def __str__(self):
		return self.user.username
	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_total_item_price()
		if self.coupon:
			total -= self.coupon.amount
		return total
	def set_order(self):
		self.ordered=True

DELIVERY_SLOTS=(
	('Morning','Morning(6AM-10AM)'),
	('Evening','Evening(4PM-8PM)')
	)
class Address(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
	name=models.CharField(max_length=100)
	street_address = models.CharField(max_length=100)
	village_name = models.CharField(max_length=100)
	pincode = models.IntegerField()
	default = models.BooleanField(verbose_name="Set as Default Address",default=False)
	contact_number=models.IntegerField()
	delivery_time_slot=models.CharField(max_length=20,choices=DELIVERY_SLOTS)
	slug = AutoSlugField(populate_from='village_name', unique=True)
	def __str__(self):
		return self.slug
	class Meta:
		verbose_name_plural = 'Addresses'

class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code
