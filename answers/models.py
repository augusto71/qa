'''models.py

Este módulo define os modelos do site de perguntas e respostas.

Este módulo contêm os seguintes modelos:
	* UserProfile - extende a classe `django.contrib.auth.models.User`.
'''

from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm

class UserProfile(models.Model):
	'''
	Extende a classe `django.contrib.auth.models.User`.
	'''

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')

class Question(models.Model):
	'''
	Representa uma pergunta.
	'''

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=150)
	description = models.TextField(max_length=4000)
	pub_date = models.DateTimeField(auto_now_add=True, null=True)

class Answer(models.Model):
	'''
	Representa uma resposta.
	'''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	text = models.TextField(max_length=4000)
	pub_date = models.DateTimeField(auto_now_add=True, null=True)

class UserProfileForm(ModelForm):
	'''
	Representa um formulário para criar ou modificar um UserProfile.
	'''
	class Meta:
		model = UserProfile
		fields = ['image']