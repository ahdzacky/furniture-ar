import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Category, Furniture

def home_view(request):
    categories = Category.objects.all()
    latest_furnitures = Furniture.objects.order_by('-created_at')[:6]
    
    # Hero Images Slider
    hero_images = []
    hero_dir = os.path.join(settings.MEDIA_ROOT, 'hero')
    if os.path.exists(hero_dir):
        files = sorted(os.listdir(hero_dir))
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                hero_images.append(os.path.join(settings.MEDIA_URL, 'hero', f))
    
    context = {
        'categories': categories,
        'latest_furnitures': latest_furnitures,
        'hero_images': hero_images,
    }
    return render(request, 'home.html', context)

def collection_view(request):
    categories = Category.objects.all()
    
    # Search and Filtering logic
    q = request.GET.get('q')
    category_slug = request.GET.get('category')
    
    furnitures = Furniture.objects.all()
    
    if q:
        furnitures = furnitures.filter(name__icontains=q)
        
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        furnitures = furnitures.filter(category=selected_category)
    else:
        selected_category = None

    context = {
        'categories': categories,
        'selected_category': selected_category,
        'furnitures': furnitures,
    }
    return render(request, 'collection.html', context)

def furniture_detail(request, pk):
    furniture = get_object_or_404(Furniture, pk=pk)
    return render(request, 'detail.html', {'furniture': furniture})

