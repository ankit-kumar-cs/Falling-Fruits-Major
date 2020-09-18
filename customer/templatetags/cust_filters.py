from django import template
register=template.Library()

@register.filter(name='splitcat')
def splitcateogory(category):
	return str(category.split(":")[1])+".jpg"

@register.filter(name='getcategory')
def getcategory(string):
	x=string
	return [str(x.split(':')[0]).capitalize(),str(string.split(':')[1]).capitalize()]

@register.filter(name='get_item_name')
def get_item_name(string):
	return str(string.split(':')[1]).capitalize()

@register.filter(name='delivery_status')
def delivery_status(string):
	if string:
		return "Delivered"
	else:
		return "On the Way"