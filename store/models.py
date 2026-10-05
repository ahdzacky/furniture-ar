from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from catalog.models import Furniture


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name=_('Pengguna'))
    created_at = models.DateTimeField(_('Dibuat pada'), auto_now_add=True)

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())

    def formatted_total(self):
        return f'Rp {int(self.get_total()):,}'.replace(',', '.')

    def __str__(self):
        return f"Keranjang {self.user.username}"

    class Meta:
        verbose_name = 'Keranjang'
        verbose_name_plural = 'Keranjang'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name=_('Keranjang'))
    furniture = models.ForeignKey(Furniture, on_delete=models.CASCADE, verbose_name=_('Produk Mebel'))
    variant = models.ForeignKey('catalog.FurnitureVariant', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Varian'))
    quantity = models.PositiveIntegerField(_('Kuantitas'), default=1)

    def get_subtotal(self):
        return self.furniture.price * self.quantity

    def formatted_subtotal(self):
        return f'Rp {int(self.get_subtotal()):,}'.replace(',', '.')

    def __str__(self):
        return f"{self.quantity}x {self.furniture.name}"

    class Meta:
        verbose_name = 'Item Keranjang'
        verbose_name_plural = 'Item Keranjang'


ORDER_STATUS_CHOICES = [
    ('pending', _('Menunggu Pembayaran')),
    ('awaiting_confirmation', _('Menunggu Konfirmasi')),
    ('paid', _('Sudah Dibayar')),
    ('processing', _('Sedang Diproses')),
    ('shipped', _('Dikirim')),
    ('delivered', _('Selesai')),
    ('cancelled', _('Dibatalkan')),
    ('expired', _('Kedaluwarsa')),
]

PAYMENT_METHOD_CHOICES = [
    ('xendit', 'Xendit Payment Gateway'),
    ('bca', 'BCA'),
    ('bni', 'BNI'),
    ('bri', 'BRI'),
    ('mandiri', 'Mandiri'),
]


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_('Pengguna'))
    order_number = models.CharField(_('Nomor Pesanan'), max_length=20, unique=True)
    status = models.CharField(_('Status'), max_length=30, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(_('Metode Pembayaran'), max_length=20, choices=PAYMENT_METHOD_CHOICES, default='xendit')
    total_price = models.DecimalField(_('Total Harga'), max_digits=14, decimal_places=0)
    payment_proof = models.ImageField(_('Bukti Pembayaran'), upload_to='payment_proofs/', null=True, blank=True)
    xendit_invoice_id = models.CharField(_('Xendit Invoice ID'), max_length=255, null=True, blank=True)
    xendit_invoice_url = models.URLField(_('Xendit Invoice URL'), null=True, blank=True)
    notes = models.TextField(_('Catatan Tambahan'), blank=True, help_text='Catatan tambahan untuk pesanan')
    created_at = models.DateTimeField(_('Dibuat pada'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Diperbarui pada'), auto_now=True)

    def formatted_total(self):
        return f'Rp {int(self.total_price):,}'.replace(',', '.')

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pesanan'
        verbose_name_plural = 'Pesanan'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_('Pesanan'))
    furniture = models.ForeignKey(Furniture, on_delete=models.SET_NULL, null=True, verbose_name=_('Produk Mebel'))
    furniture_name = models.CharField(_('Nama Produk'), max_length=200)  # snapshot nama produk
    price = models.DecimalField(_('Harga Satuan'), max_digits=12, decimal_places=0)  # snapshot harga saat order
    quantity = models.PositiveIntegerField(_('Kuantitas'))
    variant_name = models.CharField(_('Nama Varian'), max_length=150, blank=True)

    class Meta:
        verbose_name = 'Item Pesanan'
        verbose_name_plural = 'Item Pesanan'

    def get_subtotal(self):
        return self.price * self.quantity

    def formatted_subtotal(self):
        return f'Rp {int(self.get_subtotal()):,}'.replace(',', '.')

    def __str__(self):
        return f"{self.quantity}x {self.furniture_name}"


class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address', verbose_name=_('Pesanan'))
    full_name = models.CharField(_('Nama Lengkap'), max_length=200)
    phone = models.CharField(_('Nomor Telepon'), max_length=20)
    address = models.TextField(_('Alamat Lengkap'))
    city = models.CharField(_('Kota/Kabupaten'), max_length=100)
    district = models.CharField(_('Kecamatan'), max_length=100, blank=True)
    village = models.CharField(_('Kelurahan'), max_length=100, blank=True)
    province = models.CharField(_('Provinsi'), max_length=100)
    postal_code = models.CharField(_('Kode Pos'), max_length=10)

    class Meta:
        verbose_name = 'Alamat Pengiriman'
        verbose_name_plural = 'Alamat Pengiriman'

    def __str__(self):
        return f"Alamat pengiriman untuk Order #{self.order.order_number}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_('Pengguna'))
    phone = models.CharField(_('Nomor Telepon'), max_length=20, blank=True)
    address = models.TextField(_('Alamat Lengkap'), blank=True)
    city = models.CharField(_('Kota/Kabupaten'), max_length=100, blank=True)
    district = models.CharField(_('Kecamatan'), max_length=100, blank=True)
    village = models.CharField(_('Kelurahan'), max_length=100, blank=True)
    province = models.CharField(_('Provinsi'), max_length=100, blank=True)
    postal_code = models.CharField(_('Kode Pos'), max_length=10, blank=True)

    class Meta:
        verbose_name = 'Profil Pengguna'
        verbose_name_plural = 'Profil Pengguna'

    def __str__(self):
        return f"Profile of {self.user.username}"
