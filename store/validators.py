import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class AlphanumericPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise ValidationError(
                _("Kata Sandi Anda harus mengandung kombinasi huruf dan angka."),
                code='password_no_alphanumeric',
            )

    def get_help_text(self):
        return _("Kata Sandi Anda harus mengandung kombinasi huruf dan angka.")
