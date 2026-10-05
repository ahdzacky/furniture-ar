from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(_('Nama Kategori'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True)

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategori'

    def __str__(self):
        return self.name

class Furniture(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='furnitures', verbose_name=_('Kategori'))
    name = models.CharField(_('Nama Produk'), max_length=200)
    description = models.TextField(_('Deskripsi'), blank=True)
    price = models.DecimalField(_('Harga'), max_digits=12, decimal_places=0, default=0, help_text='Harga dalam Rupiah (IDR)')
    # Dimensi
    width = models.DecimalField(_('Lebar'), max_digits=8, decimal_places=1, null=True, blank=True, help_text='Lebar dalam cm')
    height = models.DecimalField(_('Tinggi'), max_digits=8, decimal_places=1, null=True, blank=True, help_text='Tinggi dalam cm')
    depth = models.DecimalField(_('Kedalaman/Panjang'), max_digits=8, decimal_places=1, null=True, blank=True, help_text='Kedalaman/Panjang dalam cm')
    
    
    # Galeri Media
    thumbnail = models.ImageField(_('Foto Utama'), upload_to='thumbnails/')
    image_2 = models.ImageField(_('Foto Tambahan 2'), upload_to='gallery/', blank=True, null=True)
    image_3 = models.ImageField(_('Foto Tambahan 3'), upload_to='gallery/', blank=True, null=True)
    image_4 = models.ImageField(_('Foto Tambahan 4'), upload_to='gallery/', blank=True, null=True)
    image_5 = models.ImageField(_('Foto Tambahan 5'), upload_to='gallery/', blank=True, null=True)
    video = models.FileField(_('Video Produk'), upload_to='videos/', blank=True, null=True, help_text='Unggah video peragaan/produk (opsional)')

    model_glb = models.FileField(_('Model 3D (.glb)'), upload_to='models/glb/', help_text='3D model for Android/WebXR (.glb)')
    model_usdz = models.FileField(_('Model 3D (.usdz)'), upload_to='models/usdz/', help_text='3D model for iOS AR (.usdz)', blank=True, null=True)
    created_at = models.DateTimeField(_('Dibuat pada'), auto_now_add=True)

    class Meta:
        verbose_name = 'Produk Furnitur'
        verbose_name_plural = 'Produk Furnitur'

    @property
    def total_stock(self):
        """Menghitung akumulasi seluruh stok dari semua varian."""
        return sum(v.stock for v in self.variants.all())

    def formatted_price(self):
        """Return price formatted as IDR."""
        return f'Rp {int(self.price):,}'.replace(',', '.')

    def __str__(self):
        return self.name

class FurnitureVariant(models.Model):
    furniture = models.ForeignKey(Furniture, on_delete=models.CASCADE, related_name='variants', verbose_name=_('Produk'))
    name = models.CharField(_('Nama Varian'), max_length=150, help_text='Contoh: Warna Merah, Ukuran L, Set Besi')
    stock = models.PositiveIntegerField(_('Stok'), default=0)

    class Meta:
        verbose_name = 'Varian'
        verbose_name_plural = 'Varian'

    def __str__(self):
        return f"{self.furniture.name} - {self.name}"
