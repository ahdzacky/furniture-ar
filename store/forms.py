from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label=_('Username'),
        max_length=20,
        required=True,
        help_text=_('Maksimal 20 karakter. Hanya huruf kecil (a-z) saja, tanpa spasi atau angka.'),
        validators=[
            RegexValidator(
                regex=r'^[a-z]+$',
                message=_('Username hanya boleh terdiri dari huruf kecil saja.'),
                code='invalid_username'
            )
        ],
        widget=forms.TextInput(attrs={'oninput': "this.value = this.value.replace(/[^a-z]/g, '');"})
    )
    first_name = forms.CharField(
        label=_('Nama Depan'), max_length=100, required=True,
        widget=forms.TextInput(attrs={'oninput': "this.value = this.value.replace(/[^a-zA-Z\\s]/g, '');"})
    )
    last_name = forms.CharField(
        label=_('Nama Belakang'), max_length=100, required=False,
        widget=forms.TextInput(attrs={'oninput': "this.value = this.value.replace(/[^a-zA-Z\\s]/g, '');"})
    )
    email = forms.EmailField(label=_('Email'), required=True)
    phone = forms.CharField(
        label=_('Nomor Telepon'), max_length=20, required=False, initial='+62',
        widget=forms.TextInput(attrs={
            'oninput': "let v=this.value; if(!v.startsWith('+62')) v='+62'+v.replace(/^\\+?6?2?0?/, ''); this.value='+'+v.substring(1).replace(/\\D/g, '');"
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone.strip() == '+62':
            return ''
        if phone.startswith('+620'):
            phone = '+62' + phone[4:]
        elif phone and phone.startswith('0'):
            phone = '+62' + phone[1:]
        elif phone and phone.startswith('62'):
            phone = '+' + phone
        return phone

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent text-slate-800'
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': base_class})
        
        self.fields['password1'].label = _('Kata Sandi')
        self.fields['password2'].label = _('Konfirmasi Kata Sandi')
        self.fields['password2'].help_text = _('Masukkan sandi yang sama persis seperti sebelumnya untuk verifikasi.')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            from .models import UserProfile
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone', ''),
            )
        return user


class ShippingAddressForm(forms.Form):
    full_name = forms.CharField(
        max_length=200, label=_('Nama Lengkap'),
        widget=forms.TextInput(attrs={'placeholder': _('Nama penerima')})
    )
    phone = forms.CharField(
        max_length=20, label=_('Nomor Telepon'),
        initial='+62',
        widget=forms.TextInput(attrs={
            'placeholder': '+628xx-xxxx-xxxx',
            'oninput': "let v=this.value; if(!v.startsWith('+62')) v='+62'+v.replace(/^\\+?6?2?0?/, ''); this.value='+'+v.substring(1).replace(/\\D/g, '');"
        })
    )
    address = forms.CharField(
        label=_('Alamat Lengkap'),
        widget=forms.Textarea(attrs={'placeholder': 'Jl. ..., No. ...', 'rows': 3})
    )
    province = forms.CharField(
        max_length=100, label=_('Provinsi'),
        widget=forms.Select(choices=[('', _('Pilih Provinsi...'))], attrs={'id': 'id_province'})
    )
    city = forms.CharField(
        max_length=100, label=_('Kota/Kabupaten'),
        widget=forms.Select(choices=[('', _('Pilih Kota/Kabupaten...'))], attrs={'id': 'id_city'})
    )
    district = forms.CharField(
        max_length=100, label=_('Kecamatan'), required=False,
        widget=forms.Select(choices=[('', _('Pilih Kecamatan...'))], attrs={'id': 'id_district'})
    )
    village = forms.CharField(
        max_length=100, label=_('Kelurahan/Desa'), required=False,
        widget=forms.Select(choices=[('', _('Pilih Kelurahan/Desa...'))], attrs={'id': 'id_village'})
    )
    postal_code = forms.CharField(
        max_length=10, label=_('Kode Pos'),
        widget=forms.TextInput(attrs={'placeholder': '12345', 'id': 'id_postal_code'})
    )

    notes = forms.CharField(
        label=_('Catatan Pesanan (opsional)'),
        required=False,
        widget=forms.Textarea(attrs={'placeholder': _('Contoh: tolong kirim pagi hari'), 'rows': 2})
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone.strip() == '+62':
            return ''
        if phone.startswith('+620'):
            phone = '+62' + phone[4:]
        elif phone and phone.startswith('0'):
            phone = '+62' + phone[1:]
        elif phone and phone.startswith('62'):
            phone = '+' + phone
        return phone

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['province', 'city', 'district', 'village']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['data-initial'] = self.initial.get(field_name, '')

from .models import UserProfile

class UserForm(forms.ModelForm):
    first_name = forms.CharField(
        label=_('Nama Depan'), max_length=100, required=True,
        widget=forms.TextInput(attrs={'oninput': "this.value = this.value.replace(/[^a-zA-Z\\s]/g, '');"})
    )
    last_name = forms.CharField(
        label=_('Nama Belakang'), max_length=100, required=False,
        widget=forms.TextInput(attrs={'oninput': "this.value = this.value.replace(/[^a-zA-Z\\s]/g, '');"})
    )
    email = forms.EmailField(label=_('Email'), required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent text-slate-800'
        for field in self.fields.values():
            field.widget.attrs.update({'class': base_class})


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone', 'address', 'province', 'city', 'district', 'village', 'postal_code')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'province': forms.Select(choices=[('', _('Pilih Provinsi...'))], attrs={'id': 'id_province'}),
            'city': forms.Select(choices=[('', _('Pilih Kota/Kabupaten...'))], attrs={'id': 'id_city'}),
            'district': forms.Select(choices=[('', _('Pilih Kecamatan...'))], attrs={'id': 'id_district'}),
            'village': forms.Select(choices=[('', _('Pilih Kelurahan/Desa...'))], attrs={'id': 'id_village'}),
            'postal_code': forms.TextInput(attrs={'id': 'id_postal_code'})
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone.strip() == '+62':
            return ''
        if phone and phone.startswith('0'):
            phone = '+62' + phone[1:]
        elif phone and phone.startswith('62'):
            phone = '+' + phone
        return phone

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk or not self.instance.phone:
            self.initial['phone'] = '+62'
            
        base_class = 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent text-slate-800'
        for field_name, field in self.fields.items():
            if field_name == 'address':
                field.widget.attrs.update({'class': base_class + ' resize-none'})
            elif field_name == 'phone':
                field.widget.attrs.update({
                    'class': base_class,
                    'oninput': "let v=this.value; if(!v.startsWith('+62')) v='+62'+v.replace(/^\\+?6?2?0?/, ''); this.value='+'+v.substring(1).replace(/\\D/g, '');"
                })
            elif field_name in ['province', 'city', 'district', 'village']:
                initial_val = getattr(self.instance, field_name, '') or ''
                field.widget.attrs.update({
                    'class': base_class,
                    'data-initial': initial_val
                })
            else:
                field.widget.attrs.update({'class': base_class})

from .models import Order

class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_proof']
        widgets = {
            'payment_proof': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-opacity-90 transition-all cursor-pointer border border-slate-200 rounded-xl bg-slate-50'
            })
        }
