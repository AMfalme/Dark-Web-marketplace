from django import forms
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password
from .models import VendorTerm

from captcha.fields import CaptchaField

import string
import random

User = get_user_model()


def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class UserPgpChangeForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['pgp_key']


class Changetermsform(forms.ModelForm):

    class Meta:
        model = VendorTerm
        fields = ['description']


class LoginForm(forms.Form):
    """A form to sign-in authenticated users. Includes a simple captcha challenge."""
    username = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)

    captcha = CaptchaField()

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        request = self.request
        cleaned_data = self.cleaned_data
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            raise forms.ValidationError("Invalid username or password")
        if not user.tfalogin:
            login(request, user)
        request.session['username'] = user.username
        request.session['password'] = password
        request.session['org_key'] = random_string()
        return password


class GPGAuthForm(forms.Form):

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(GPGAuthForm, self).__init__(*args, **kwargs)


class SignUpForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
        fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', )

    def clean_password1(self):
        # Validate password using built-in Django validator.
        password1 = self.cleaned_data.get("password1")
        validity_errors = validate_password(password1)  # , user=None, password_validators=None)
        if not validity_errors:
            return password1

    def clean_password2(self):
        # Check that the two password entries match
        print("Cleaning password 2")
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # read file bip39
        list_choice = []
        with open('./data_dump/bip39.txt', 'r+') as f:
            for line in f.readlines():
                print(line)
                list_choice.append(line.strip())

        sampling = self.random_choices(list_choice)
        print('---- >>>>> ', sampling)
        code_bip39 = " ".join(str(x) for x in sampling)

        # Save the User and pas instance to the form
        print("1_")
        user = super(SignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.code_bip39 = code_bip39
        print("2_")
        if commit:
            user.save()
        return user

    def random_choices(self, world_list):
        answer = set()
        sample_size = 8
        answer_size = 0

        while answer_size < sample_size:
            r = random.randint(0, len(world_list))
            if r not in answer:
                answer_size += 1
                answer.add(world_list[r])

        return answer


# Form for updating users in the ADMIN site
class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users on the ADMIN site.
    Includes all the fields on the user, but replaces the
    password field with admin's password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username', )  # 'pgp_key', 'image', 'password', 'admin', 'staff', 'vendor', 'is_active')

    def clean_password(self):
        # Regardless of what input is provided, returns the initial password value.
        # This is done so that only authenticated user can change password.
        # Password Change form is handled using Django's built in form.
        return self.initial["password"]


# Form for creating users in the ADMIN site
class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', )

    def clean_password1(self):
        # Validate password using built-in Django validator.
        password1 = self.cleaned_data.get("password1")
        validity_errors = validate_password(password1)  # , user=None, password_validators=None)
        print(validity_errors)
        if not validity_errors:
            return password1

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
