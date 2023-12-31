'''Este módulo contêm as views do aplicativo "answers".'''

import os
import datetime
import string
import random

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings

from .models import Question
from .models import Answer
from .models import Code
from .models import UserProfile
from .models import UserProfileForm


def signin(request):
	'''Página de login do usuário.'''

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return HttpResponse('Login efetuado com sucesso.')
		else:
			return HttpResponse('Dados de login incorretos.')
	else:
		return render(request, 'signin.html')


def signup(request):
	'''Página de registro de conta.'''

	if request.method == 'POST':
		username = request.POST.get('username').strip()
		email = request.POST.get('email')
		password = request.POST.get('password')

		''' verifica se o tamanho do nome de usuário é válido. '''
		max_username_length = User._meta.get_field('username').max_length
		if not username or len(username) > max_username_length:
			return HttpResponse('Nome de usuário vazio ou com mais de %d caracteres.' % (max_username_length))

		''' verifica se o tamanho do email é válido. '''
		max_email_length = User._meta.get_field('email').max_length
		min_email_length = 3

		if len(email) < min_email_length or len(email) > max_email_length:
			return HttpResponse('Email com menos de %d caracteres ou mais de %d caracteres.' % (min_email_length, max_email_length))

		''' verifica se o tamanho da senha é válido. '''
		max_password_length = User._meta.get_field('password').max_length

		if not password or len(password) > max_password_length:
			return HttpResponse('Senha vazia ou com mais de %d caracteres.' % (max_password_length))

		user = User.objects.create_user(username, email, password)

		UserProfile.objects.create(user=user)

		login(request, user)

		messages.success(request, 'Conta criada com sucesso.')
		return redirect('/')
	else:
		return render(request, 'signup.html')


def logout(request):
	'''Desconecta o usuário.'''

	django_logout(request)
	return redirect('/')


def ask(request):
	'''Página de fazer pergunta.'''

	if request.method == 'POST':
		title = request.POST.get('title')
		description = request.POST.get('description')

		''' verifica se o tamanho do título da pergunta é válido. '''
		max_question_size = Question._meta.get_field('title').max_length
		if not title or len(title) > max_question_size:
			return HttpResponse('Título vazio ou grande demais (mais de %d caracteres).' % (max_question_size))

		''' verifica se o tamanho da descrição da pergunta é válido. '''
		max_description_size = Question._meta.get_field('description').max_length
		if len(description) > max_description_size:
			return HttpResponse('Descrição com mais de %d caracteres.' % (max_description_size))

		''' adiciona um ponto de interrogação na pergunta se não houver. '''
		if title.strip()[-1] != '?':
			title += '?'

		q = Question.objects.create(user=request.user, title=title, description=description)

		return redirect('/question/' + str(q.id))
	else:
		if request.user.is_authenticated:
			return render(request, 'ask.html')
		else:
			return HttpResponse('<a href="/signin">Faça login</a> para fazer uma pergunta.')


def question(request, qid):
	'''Página de uma questão.'''

	q = Question.objects.filter(id=qid)

	if not q.exists():
		raise Http404('Questão não encontrada.')
	else:
		q = q.first()

	answers = Answer.objects.filter(question=q)

	if request.method == 'POST':
		text = request.POST.get('text')

		''' verifica se o tamanho da resposta é válido. '''
		max_answer_length = Answer._meta.get_field('text').max_length
		if not text or len(text) > max_answer_length:
			return HttpResponse('Resposta vazia ou com mais de %d caracteres.' % (max_answer_length))

		a = Answer.objects.create(user=request.user, question=q, text=text)
		return render(request, 'includes/answer.html', {'answer': a})
	else:
		if request.user.is_authenticated:
			if Answer.objects.filter(question=q, user=request.user).exists():
				response_form = False
			else:
				response_form = True
		else:
			response_form = False

		return render(request, 'question.html', {'question': q, 'answers': answers, 'response_form': response_form})


def user_profile(request, username):
	'''Página de perfil do usuário.'''

	user = User.objects.filter(username=username)

	if not user.exists():
		raise Http404('Usuário não encontrado.')
	else:
		user = user.first()

	up = UserProfile.objects.get(user=user)

	return render(request, 'user_profile.html', {'user_profile': up})


def index(request):
	'''Página inicial.'''

	page_number = request.GET.get('page')

	if not page_number:
		page_number = 1

	questions_page = Paginator(Question.objects.all().order_by('-id'), 3)

	page = questions_page.page(page_number)

	return render(request, 'index.html', {'questions': page.object_list, 'page': page})


def edit_user_profile(request):
	'''Página para que o usuário possa editar o próprio perfil.'''

	if request.method == 'POST':

		user_profile = UserProfile.objects.get(user=request.user)

		last_profile_photo = os.path.basename(user_profile.image.path)

		form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

		if form.is_valid():
			form.save()
			if len(request.FILES) > 0 and last_profile_photo != 'default.jpg':
				os.remove(last_profile_photo)


		return redirect('/user/' + request.user.username)

	user_profile = UserProfile.objects.get(user=request.user)
	form = UserProfileForm(instance=user_profile)

	return render(request, 'edit_user_profile.html', {'form': form})


def delete_question(request):
	'''Apaga uma questão.'''

	if request.method != 'POST':
		return HttpResponseBadRequest()

	qid = request.POST.get('qid')

	q = Question.objects.get(id=qid)

	if request.user != q.user:
		return HttpResponseForbidden()

	q.delete()

	return redirect('/')


def delete_answer(request):
	'''Apaga uma resposta.'''

	if request.method != 'POST':
		return HttpResponseBadRequest()

	answer_id = request.POST.get('answer_id')

	a = Answer.objects.get(id=answer_id)

	if request.user != a.user:
		return HttpResponseForbidden()

	qid = a.question.id
	a.delete()

	return redirect('/question/%d' % (qid))


def recover_password(request):
	'''view para recuperação de senha.'''

	if request.method == 'POST':

		allowed_hosts = [host.upper() for host in settings.ALLOWED_HOSTS]

		if request.get_host().upper() not in allowed_hosts:
			return HttpResponseForbidden()

		receiver = request.POST.get('email')

		user = User.objects.filter(email=receiver)
		if not user.exists():
			return render(request, 'email-sent-to-change password.html')
		user = user.first()

		new_code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

		code_obj = Code.objects.create(user=user, code=new_code)
		code = code_obj.code

		email_message = 'Use este link para recuperar sua senha: http://%s/change-password?code=%s' % (request.get_host(), code)

		send_mail(subject='Recuperação de senha', message=email_message, from_email=settings.EMAIL_HOST_USER, recipient_list=[receiver])

		return render(request, 'email-sent-to-change password.html')

	return render(request, 'recover-password.html')


def change_password(request):
	'''view para alteração de senha.'''

	code = Code.objects.filter(code=request.GET.get('code'))

	if code.exists():
		code = code.first()
	else:
		return HttpResponse('Código inexistente.')

	max_code_duration = 3600 # segundos

	timediff = datetime.datetime.utcnow() - code.creation_date.replace(tzinfo=None)

	if timediff.seconds > max_code_duration:
		code.delete()
		return HttpResponse('Código expirado.')

	if request.method == 'POST':
		user = code.user
		user.set_password(request.POST.get('password'))
		user.save()

		code.delete()

		messages.success(request, 'Senha alterada com sucesso.')
		return redirect('signin')

	return render(request, 'change-password.html')