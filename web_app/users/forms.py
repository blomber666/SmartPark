from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm 
from django.utils.translation import gettext_lazy as _
from users.models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'validate','placeholder': 'Plate'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))

# creating a form
class SignupForm(UserCreationForm):
    #remove help_text
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "autofocus"
            ] = False
            
    username = forms.CharField(
        label=_("Plate"),
        widget=forms.TextInput(attrs={"class":"validate","placeholder": "Plate"})
        )        

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "Password"}),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "Confirm Password"}),
    )

    class Meta:
        model = User
        fields = ("username",)

    # def save(self, commit: bool = True):
    #     user = super(self).save(commit=False)
    #     user.plate = self.cleaned_data["plate"]
    #     if commit:
    #         user.save()
    # #     return user

#a = SignupForm()
#print(a)