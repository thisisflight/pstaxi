from allauth.account.views import LoginView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import (PasswordResetView,
                                       PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView)
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from accounts.forms import (CustomUserCreationForm, ProfileUpdateForm, CustomAuthenticationForm,
                            CustomPasswordResetForm, CustomSetPasswordForm)
from accounts.models import Profile


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/registration/signin.html'


class CustomSignUpView(CreateView):
    model = User
    template_name = 'accounts/registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('motorpool:brand_list')

    def form_valid(self, form):
        result = super().form_valid(form)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(self.request, username=username,
                            password=password)
        if user is not None:
            login(self.request, user)
        return result


class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_detail.html'

    def form_valid(self, form):
        messages.success(self.request, f'Данные успешно обновлены')
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/registration/password_reset_form.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'accounts/registration/password_reset_email.txt'
    subject_template_name = 'accounts/registration/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    from_email = settings.EMAIL_HOST_USER
    html_email_template_name = 'accounts/registration/password_reset_email.html'

    def form_valid(self, form):
        self.request.session['reset_email'] = form.cleaned_data['email']
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/registration/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reset_email'] = self.request.session.get('reset_email', '')
        return context


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/registration/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/registration/password_reset_complete.html'
