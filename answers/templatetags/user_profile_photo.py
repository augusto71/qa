from django import template

from django.contrib.auth.models import User
from ..models import UserProfile

register = template.Library()

@register.simple_tag
def get_user_profile_photo(user_id):
	user = User.objects.get(id=user_id)
	up = UserProfile.objects.get(user=user)
	return up.image.url