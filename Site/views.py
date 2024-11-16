from django.views import View
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm, CreateApplicationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import DeleteView
from .models import DesignApplication


class LoginUserView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'registration/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль')
        return render(request, 'registration/login.html', {'form': form})

class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Optionally handle any additional logic here before saving
        return super().form_valid(form)

class LogoutUserView(TemplateView):
    template_name = 'registration/logout.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)

class CreateApplicationView(View):
    def get(self, request):
        form = CreateApplicationForm()
        return render(request, 'create_app.html', {'form': form})

    def post(self, request):
        form = CreateApplicationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()  # Saves the instance with correct category
            return redirect('account')
        else:
            print(form.errors)  # Print out the errors for debugging
        return render(request, 'create_app.html', {'form': form})

class AccountListView(LoginRequiredMixin, generic.ListView):
    model = DesignApplication
    template_name = 'account.html'

    def get_queryset(self):
        return DesignApplication.objects.filter(creator=self.request.user).order_by('-time_created')

class HomepageListView(generic.ListView):
    model = DesignApplication
    template_name = 'index.html'

    def get_queryset(self):
        return DesignApplication.objects.all().filter(status='d').order_by('-time_created')[:4]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apps_in_process'] = DesignApplication.objects.filter(status='w').count()
        return context

class AppDelete(DeleteView):
    model = DesignApplication
    success_url = reverse_lazy('account')
    template_name = 'delete_app.html'

    def get_queryset(self):
        return super().get_queryset()