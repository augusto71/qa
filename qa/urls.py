"""
URL configuration for qa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from answers import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('ask', views.ask, name='ask'),
    path('question/<int:qid>', views.question, name='question'),
    path('user/<str:username>', views.user_profile, name='user_profile'),
    path('', views.index, name='index'),
    path('edit_user_profile', views.edit_user_profile, name='edit_user_profile'),
    path('delete_question', views.delete_question, name='delete_question'),
    path('delete_answer', views.delete_answer, name='delete_answer'),
    path('recover-password', views.recover_password, name='recover_password'),
    path('change-password', views.change_password, name='change_password'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)