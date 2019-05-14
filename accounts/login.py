from django.contrib.auth.forms import AuthenticationForm
from django.forms import ValidationError
from django import forms
from captcha.fields import CaptchaField

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)

    captcha = CaptchaField()
    
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(CustomLoginForm, self).__init__(*args, **kwargs)

    # def clean(self):
    #     userid = self.cleaned_data.get('username')
    #     password = self.cleaned_data.get('password')
        
    #     if userid and password:
    #         #the backends will be picked from the settings from the variable named AUTHENTICATION_BACKENDS
    #         #and the authentication method of each of one will be called in the same order as the order in the AUTHENTICATION_BACKENDS list
    #         self.user_cache = authenticate(
    #             userid=userid, 
    #             password=password
    #         )

    #         if self.user_cache is None:
    #             raise forms.ValidationError(
    #                 self.error_messages['invalid_login'],
    #                 code='invalid_login',
    #                 params={'username': self.username_field.verbose_name},
    #             )
    #         else:
    #             self.confirm_login_allowed(self.user_cache)
        
    #     return self.cleaned_data