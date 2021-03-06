from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from customer.forms import RegistrationForm, AccountAuthenticationForm,UserUpdateForm,ProfileUpdateForm,AddressForm
from django.contrib import messages
from .models import Product,OrderItem,Order,Address
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
def home_page(request):
	return render(request,'customer/home.html')

def working(request):
    return render(request,'customer/working-model.html')
def registration_view(request):
	context = {}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email')
			raw_password = form.cleaned_data.get('password1')
			return render(request,'customer/register-success.html')
		else:
			context['registration_form'] = form

	else:
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'customer/register.html', context)


def logout_view(request):
	logout(request)
	return redirect('customer:home')


def login_view(request):

	context = {}

	user = request.user
	if user.is_authenticated:
		return redirect("customer:home")

	if request.POST:
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			email = request.POST['email']
			password = request.POST['password']
			user = authenticate(email=email, password=password)

			if user:
				login(request, user)
				return redirect("customer:home")

	else:
		form = AccountAuthenticationForm()

	context['login_form'] = form

	# print(form)
	return render(request, "customer/login.html", context)




def must_authenticate_view(request):
	return render(request, 'account/must_authenticate.html', {})

@login_required
def profile_view(request):
	context={}
	context['email']=request.user.email
	context['username']= request.user.username
	context['f_name']=request.user.profile.first_name
	context['l_name']=request.user.profile.last_name
	context['contact']=request.user.profile.contact
	context['image']=request.user.profile.image
	return render(request,"customer/profile.html",context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('customer:profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'customer/update-profile.html', context)

@login_required
def CartView(request):
    context={}
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if (order.items.exists()):
            context['orders']=order
            print(order.items)
    print(context)
    return render(request,'customer/cart.html',context)

@login_required
def CheckoutView(request):
    context={}
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        context['orders']=order
        if request.POST:
            form=AddressForm(request.POST)
            if form.is_valid():
                c_name = form.cleaned_data.get('name')
                street_addr=form.cleaned_data.get('street_address')
                village=form.cleaned_data.get('village_name')
                pin_code=form.cleaned_data.get('pincode')
                contact=form.cleaned_data.get('contact_number')
                default_addr=form.cleaned_data.get('default')
                address_obj=Address(
                    user=request.user,
                    name=c_name,
                    street_address=street_addr,
                    village_name=village,
                    contact_number=contact,
                    pincode=pin_code,
                    default=default_addr
                    )
                address_obj.save()
                Order.objects.filter(user=request.user,ordered=False).update(address=address_obj)
                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()
                Order.objects.filter(user=request.user,ordered=False).update(ordered=True)                
                return redirect('customer:order-detail-view',)
        else:
            form=AddressForm()
        context['form']=form
    else:
        context={}
    
    return render(request,'customer/checkout.html',context)

class OrderDetailView(ListView):
    template_name='customer/order-detail.html'
    context_object_name = 'orders'
    model=Order
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user,ordered=True)
    
class ProductView(ListView):
	template_name='customer/product-list.html'
	context_object_name = 'product'
	paginate_by = 12
	model=Product
   

class ProductDetailView(DetailView):
	model = Product
	template_name='customer/product-detail.html'
	context_object_name = 'product'
	def get_object(self, **kwargs):
		return Product.objects.get(slug=self.kwargs['slug'])

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        product=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            #messages.info(request, "This item quantity was updated.")
            return redirect("customer:cart")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("customer:product")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("customer:product")

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                product=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            #messages.info(request, "This item was removed from your cart.")
            return redirect("customer:cart")
        else:
            #messages.info(request, "This item was not in your cart")
            return redirect("customer:cart")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("customer:cart")

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(product__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                product=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("customer:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("customer:cart", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("customer:cart", slug=slug)

