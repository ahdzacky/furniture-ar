import uuid
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import xendit
from xendit.invoice import InvoiceApi
from xendit.invoice.model.create_invoice_request import CreateInvoiceRequest

from catalog.models import Furniture, FurnitureVariant
from .models import Cart, CartItem, Order, OrderItem, ShippingAddress, UserProfile
from .forms import RegisterForm, ShippingAddressForm, UserForm, UserProfileForm, PaymentProofForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

# ─────────────────────────── AUTH ────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('collection')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Selamat datang, {user.username}! Akun berhasil dibuat.')
            return redirect('collection')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('collection')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'collection')
            return redirect(next_url)
        else:
            error = 'Username atau password salah.'
    return render(request, 'store/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('collection')


# ─────────────────────────── CART ────────────────────────────

def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('furniture').all()
    return render(request, 'store/cart.html', {
        'cart': cart,
        'items': items,
    })


@login_required
@require_POST
def add_to_cart(request, pk):
    furniture = get_object_or_404(Furniture, pk=pk)
    variant_id = request.POST.get('selected_variant')

    if not variant_id:
        messages.error(request, 'Silakan pilih varian terlebih dahulu.')
        return redirect('furniture_detail', pk=pk)

    variant = get_object_or_404(FurnitureVariant, id=variant_id, furniture=furniture)

    if variant.stock < 1:
        messages.error(request, 'Maaf, varian ini sedang habis stok.')
        return redirect('furniture_detail', pk=pk)

    cart = get_or_create_cart(request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > variant.stock:
        messages.error(request, f'Maaf, stok yang tersedia hanya {variant.stock}.')
        return redirect('furniture_detail', pk=pk)

    # Cari item yang sama (furniture + variant)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        furniture=furniture,
        variant=variant,
        defaults={'quantity': quantity}
    )
    if not created:
        if item.quantity + quantity > variant.stock:
            messages.error(request, f'Total kuantitas melebihi sisa stok varian ({variant.stock}).')
            return redirect('furniture_detail', pk=pk)
        item.quantity += quantity
        item.save()

    messages.success(request, f'"{furniture.name} - {variant.name}" berhasil ditambahkan ke keranjang.')
    
    action = request.POST.get('action')
    if action == 'buy_now':
        from django.urls import reverse
        return redirect(f"{reverse('checkout')}?selected_items={item.id}")
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if not item.variant:
        item.delete()
        return redirect(request.META.get('HTTP_REFERER', 'cart'))

    if quantity > 0:
        if quantity > item.variant.stock:
            messages.error(request, f'Kuantitas melebihi sisa stok varian ({item.variant.stock}).')
            item.quantity = item.variant.stock
        else:
            item.quantity = quantity
        item.save()
    else:
        item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, 'Item dihapus dari keranjang.')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


# ─────────────────────────── CHECKOUT ────────────────────────

@login_required
def checkout_view(request):
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('furniture').all()

    selected_items_ids = request.GET.getlist('selected_items')
    if selected_items_ids:
        request.session['checkout_items'] = selected_items_ids
    else:
        selected_items_ids = request.session.get('checkout_items', [])

    if selected_items_ids:
        items = items.filter(id__in=selected_items_ids)
    else:
        messages.warning(request, 'Pilih setidaknya satu produk untuk di-checkout.')
        return redirect('cart')

    if not items.exists():
        messages.warning(request, 'Item yang Anda pilih tidak valid atau sudah dihapus.')
        return redirect('cart')

    total = sum(item.get_subtotal() for item in items)
    formatted_total = f'Rp {int(total):,}'.replace(',', '.')

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Generate order number
            order_number = 'ORD-' + uuid.uuid4().hex[:8].upper()

            # Buat Order
            order = Order.objects.create(
                user=request.user,
                order_number=order_number,
                status='pending',
                payment_method='xendit',
                total_price=total,
                notes=data.get('notes', ''),
            )

            # Buat ShippingAddress
            ShippingAddress.objects.create(
                order=order,
                full_name=data['full_name'],
                phone=data['phone'],
                address=data['address'],
                city=data['city'],
                district=data.get('district', ''),
                village=data.get('village', ''),
                province=data['province'],
                postal_code=data['postal_code'],
            )

            # Buat OrderItems & kurangi stok
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    furniture=item.furniture,
                    furniture_name=item.furniture.name,
                    price=item.furniture.price,
                    quantity=item.quantity,
                    variant_name=item.variant.name if item.variant else '',
                )
                # Kurangi stok
                if item.variant:
                    item.variant.stock = max(0, item.variant.stock - item.quantity)
                    item.variant.save()

            # Kosongkan cart
            items.delete()

            # Hapus session checkout_items
            if 'checkout_items' in request.session:
                del request.session['checkout_items']

            # Simpan order number di session untuk halaman sukses
            request.session['last_order_id'] = order.id

            # Create Xendit Invoice
            try:
                xendit.set_api_key(settings.XENDIT_SECRET_KEY)
                invoice_client = InvoiceApi()

                success_url = request.build_absolute_uri(reverse('order_success'))
                failure_url = request.build_absolute_uri(reverse('order_detail', args=[order_number]))

                invoice_data = CreateInvoiceRequest(
                    external_id=order_number,
                    amount=float(total),
                    payer_email=request.user.email,
                    description=f"Pesanan {order_number} dari SBN Store",
                    success_redirect_url=success_url,
                    failure_redirect_url=failure_url,
                )

                invoice = invoice_client.create_invoice(create_invoice_request=invoice_data)
                order.xendit_invoice_id = invoice.id
                order.xendit_invoice_url = invoice.invoice_url
                order.save()

                return redirect(invoice.invoice_url)
            except Exception as e:
                import traceback
                traceback.print_exc()
                messages.error(request, f'Gagal membuat invoice Xendit: {str(e)}')
                return redirect('order_detail', order_number=order.order_number)
    else:
        # Pre-fill dari UserProfile bila ada
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
        }
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            initial_data.update({
                'phone': profile.phone,
                'address': profile.address,
                'city': profile.city,
                'district': profile.district,
                'village': profile.village,
                'province': profile.province,
                'postal_code': profile.postal_code,
            })
        form = ShippingAddressForm(initial=initial_data)

    return render(request, 'store/checkout.html', {
        'form': form,
        'cart': cart,
        'items': items,
        'formatted_total': formatted_total,
    })


@login_required
def order_success(request):
    order_id = request.session.pop('last_order_id', None)
    if not order_id:
        return redirect('collection')
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {
        'order': order,
    })


# ─────────────────────────── MY ORDERS ────────────────────────

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items', 'shipping_address')
    return render(request, 'store/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_detail.html', {
        'order': order, 
    })

@login_required
@require_POST
def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        # Kembalikan stok
        for item in order.items.all():
            if item.furniture and item.variant_name:
                variant = FurnitureVariant.objects.filter(furniture=item.furniture, name=item.variant_name).first()
                if variant:
                    variant.stock += item.quantity
                    variant.save()
        messages.success(request, 'Pesanan berhasil dibatalkan dan stok dikembalikan.')
    else:
        messages.error(request, 'Pesanan tidak bisa dibatalkan pada tahap ini.')
    return redirect('order_detail', order_number=order.order_number)

@csrf_exempt
@require_POST
def xendit_webhook(request):
    webhook_token = request.headers.get('x-callback-token')
    if webhook_token != settings.XENDIT_WEBHOOK_TOKEN:
        return HttpResponse(status=403)

    try:
        data = json.loads(request.body)
        external_id = data.get('external_id')
        status = data.get('status')
        
        if external_id:
            try:
                order = Order.objects.get(order_number=external_id)
                if status == 'PAID' or status == 'SETTLED':
                    order.status = 'paid'
                    order.save()
                elif status == 'EXPIRED':
                    if order.status == 'pending':
                        order.status = 'expired'
                        order.save()
                        # Restore stock
                        for item in order.items.all():
                            if item.furniture and item.variant_name:
                                variant = FurnitureVariant.objects.filter(furniture=item.furniture, name=item.variant_name).first()
                                if variant:
                                    variant.stock += item.quantity
                                    variant.save()
            except Order.DoesNotExist:
                pass
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return HttpResponse(status=400)


# ─────────────────────────── USER PROFILE ────────────────────────

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Data profil Anda berhasil diperbarui.')
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
        
    return render(request, 'store/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Pastikan sesi tidak ter-logout
            messages.success(request, 'Password berhasil diperbarui.')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
        
    # Inject styling kelas Tailwind ke field
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent text-slate-800'})
            
    return render(request, 'store/password_change.html', {'form': form})
