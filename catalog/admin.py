from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Category, Furniture, FurnitureVariant

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class FurnitureVariantInline(TabularInline):
    model = FurnitureVariant
    extra = 1

@admin.register(Furniture)
class FurnitureAdmin(ModelAdmin):
    list_display = ('name', 'category', 'formatted_price', 'total_stock', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    inlines = [FurnitureVariantInline]
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('category', 'name', 'description')
        }),
        ('Harga', {
            'fields': ('price',),
            'description': 'Stok sekarang ditentukan secara terpisah pada tabel Varian di bagian layar bawah ini.'
        }),
        ('Galeri Media', {
            'fields': ('thumbnail', 'image_2', 'image_3', 'image_4', 'image_5', 'video'),
            'description': 'Unggah foto utama dan hingga 4 foto ekstra, ditambah 1 video opsional.'
        }),
        ('Dimensi (cm)', {
            'fields': ('width', 'height', 'depth'),
            'description': 'Masukkan ukuran dalam satuan sentimeter (cm).'
        }),
        ('File 3D (AR)', {
            'fields': ('model_glb', 'model_usdz'),
        }),
    )
