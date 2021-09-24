from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm

app_name = 'posts'


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
