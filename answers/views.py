from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from .models import Question
from .models import Answer
from .models import UserProfile
from .models import UserProfileForm

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

		return HttpResponse('Conta criada com sucesso.')
	else:
		return render(request, 'signup.html')

def logout(request):
	django_logout(request)
	return redirect('/')

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
		if request.user.is_authenticated:
			return render(request, 'ask.html')
		else:
			return HttpResponse('<a href="/signin">Faça login</a> para fazer uma pergunta.')

def question(request, qid):

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
	user = User.objects.filter(username=username)

	if not user.exists():
		raise Http404('Usuário não encontrado.')
	else:
		user = user.first()

	up = UserProfile.objects.get(user=user)

	return render(request, 'user_profile.html', {'user_profile': up})

def index(request):

	page_number = request.GET.get('page')

	if not page_number:
		page_number = 1

	questions_page = Paginator(Question.objects.all().order_by('-id'), 3)

	page = questions_page.page(page_number)

	return render(request, 'index.html', {'questions': page.object_list, 'page': page})

def edit_user_profile(request):

	if request.method == 'POST':

		user_profile = UserProfile.objects.get(user=request.user)

		form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

		if form.is_valid():
			form.save()

		return redirect('/user/' + request.user.username)

	form = UserProfileForm(instance=request.user)

	return render(request, 'edit_user_profile.html', {'form': form})

def delete_question(request):
	if request.method != 'POST':
		return HttpResponseBadRequest()

	qid = request.POST.get('qid')

	q = Question.objects.get(id=qid)

	if request.user != q.user:
		return HttpResponseForbidden()

	q.delete()

	return redirect('/')

def delete_answer(request):
	if request.method != 'POST':
		return HttpResponseBadRequest()

	answer_id = request.POST.get('answer_id')

	a = Answer.objects.get(id=answer_id)

	if request.user != a.user:
		return HttpResponseForbidden()

	qid = a.question.id
	a.delete()

	return redirect('/question/%d' % (qid))