from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm, CreateApplicationForm, RedactAppForm, AppFilterForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import DeleteView
from .models import DesignApplication, Category


class HomepageListView(generic.ListView):
    model = DesignApplication
    template_name = 'index.html'

    def get_queryset(self):
        return DesignApplication.objects.all().filter(status='d').order_by('-time_created')[:4]

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
        queryset = super().get_queryset()
        status = self.request.GET.get('status')

        if status:
            queryset = queryset.filter(status=status)

        queryset = queryset.order_by('-time_created')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = AppFilterForm(self.request.GET or None)
        return context

class AppsListView(generic.ListView, PermissionRequiredMixin):
    permission_required = 'Site.can_edit_status'
    model = DesignApplication
    template_name = 'apps_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')

        if status:
            queryset = queryset.filter(status=status)

        queryset = queryset.order_by('-time_created')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = AppFilterForm(self.request.GET or None)
        return context

class RedactApp(UpdateView, PermissionRequiredMixin):
    permission_required = 'Site.can_edit_status'
    model = DesignApplication
    template_name = 'redact_app.html'
    form_class = RedactAppForm
    success_url = reverse_lazy('apps_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # def get_initial(self):
    #     initial = super(RedactApp, self).get_initial()
    #     if self.request.method == 'POST':
    #         initial['status'] = self.request.POST.get('status')
    #     else:
    #         initial['status'] = self.object.status
    #     return initial

class AppDelete(DeleteView, LoginRequiredMixin):
    model = DesignApplication
    success_url = reverse_lazy('account')
    template_name = 'delete_app.html'

    def get_queryset(self):
        return super().get_queryset()

class CreateCategory(CreateView, PermissionRequiredMixin):
    permission_required = 'Site.can_edit_status'
    model = Category
    template_name = 'create_categ.html'
    fields = ['title']

    success_url = reverse_lazy('categ_list')

class CategoriesListView(generic.ListView, PermissionRequiredMixin):
    permission_required = 'Site.can_edit_status'
    model = Category
    template_name = 'categ_list.html'

    def get_queryset(self):
        return Category.objects.all().order_by('id')

class RedactCategory(UpdateView, PermissionRequiredMixin):
    permission_required = 'Site.can_edit_status'
    model = Category
    template_name = 'redact_categ.html'
    fields = ['title']

    success_url = reverse_lazy('categ_list')

class CategoryDelete(DeleteView, PermissionRequiredMixin):
    permission_required = 'Site.can_edit_status'
    model = Category
    success_url = reverse_lazy('categ_list')
    template_name = 'delete_categ.html'

    def get_queryset(self):
        return super().get_queryset()