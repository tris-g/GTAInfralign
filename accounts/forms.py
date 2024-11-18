from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2", "is_staff"]

class AuthenticationForm(AuthenticationForm):

    class Meta:
        model = User
        fields = '__all__'