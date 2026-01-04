from allauth.account.forms import SignupForm
from django.core.exceptions import ValidationError
from forums.validators import validate_bits_pilani_email


class RestrictedSignupForm(SignupForm):

    def clean_email(self):
        email = self.cleaned_data.get("email")

        try:
            validate_bits_pilani_email(email)
        except ValidationError as e:
            raise ValidationError(e.messages)

        return email
