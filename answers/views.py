from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User

from .models import Question
from .models import Answer
from .models import UserProfile

def signin(request):
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
	if request.method == 'POST':
		username = request.POST.get('username')
		email = request.POST.get('email')
		password = request.POST.get('password')

		''' verifica se o tamanho do nome de usuário é válido. '''
		max_username_length = User._meta.get_field('username').max_length
		if not username or len(username) > max_username_length:
			return HttpResponse('Nome de usuário vazio ou com mais de %d caracteres.' % (max_username_length))

		user = User.objects.create_user(username, email, password)

		UserProfile.objects.create(user=user)

		login(request, user)

		return HttpResponse('Conta criada com sucesso.')
	else:
		return render(request, 'signup.html')

def logout(request):
	django_logout(request)
	return HttpResponse('Desconectado com sucesso.')

def ask(request):
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
		return render(request, 'ask.html')

def question(request, qid):

	q = Question.objects.get(id=qid)
	answers = Answer.objects.filter(question=q)

	if request.method == 'POST':
		text = request.POST.get('text')
		a = Answer.objects.create(user=request.user, question=q, text=text)
		return HttpResponse('Pergunta respondida com sucesso.')
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
	user = User.objects.get(username=username)
	up = UserProfile.objects.get(user=user)

	return render(request, 'user_profile.html', {'user_profile': up})

def index(request):

	questions = Question.objects.all().order_by('-id')

	return render(request, 'index.html', {'questions': questions})