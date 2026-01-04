import re
from django.core.exceptions import ValidationError

BITS_EMAIL_REGEX = r"^f\d{8}@pilani\.bits-pilani\.ac\.in$"
def validate_bits_pilani_email(email):
    match = re.match(r"^f(\d{4})(\d{4})@pilani\.bits-pilani\.ac\.in$", email)
    if not match:
        raise ValidationError(
            "Use your BITS Pilani email: fYYYYRRRR@pilani.bits-pilani.ac.in"
        )

    year = int(match.group(1))
    if year < 2015 or year > 2030:
        raise ValidationError("Invalid batch year in email.")
