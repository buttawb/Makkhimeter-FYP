
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        try:
            validate_password(password)
        except ValidationError as e:
            # Customize the error message for password too short
            if 'This password is too short' in e.messages:
                raise ValidationError("Password must be at least 8 characters long.")
            else:
                raise ValidationError(e)

        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_superuser = False  # set is_superuser to False
        if commit:
            user.save()
        return user
