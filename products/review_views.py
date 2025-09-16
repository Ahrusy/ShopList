from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count
from .models import Product, Review, Order, OrderItem, Notification
from .forms import ReviewForm
import json

@login_required
def add_review(request, product_id):
    """Добавить отзыв к товару"""
    product = get_object_or_404(Product, id=product_id)
    
    # Проверяем, есть ли уже отзыв от этого пользователя
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    if existing_review:
        messages.warning(request, _("Вы уже оставили отзыв на этот товар."))
        return redirect('product_detail', pk=product_id)
    
    # Проверяем, покупал ли пользователь этот товар
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        order__status__in=['delivered', 'shipped'],
        product=product
    ).exists()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.is_verified_purchase = has_purchased
            review.save()
            
            # Создаем уведомление для продавца
            if product.seller:
                Notification.objects.create(
                    user=product.seller.user,
                    type='review_added',
                    title=_('Новый отзыв на товар'),
                    message=_('Пользователь {} оставил отзыв на товар "{}"').format(
                        request.user.username, product.name
                    )
                )
            
            messages.success(request, _("Отзыв успешно добавлен!"))
            return redirect('product_detail', pk=product_id)
    else:
        form = ReviewForm()
    
    context = {
        'product': product,
        'form': form,
        'has_purchased': has_purchased,
    }
    return render(request, 'reviews/add_review.html', context)

@login_required
def edit_review(request, review_id):
    """Редактировать отзыв"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, _("Отзыв успешно обновлен!"))
            return redirect('product_detail', pk=review.product.id)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'review': review,
        'form': form,
    }
    return render(request, 'reviews/edit_review.html', context)

@login_required
@require_POST
def delete_review(request, review_id):
    """Удалить отзыв"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id
    review.delete()
    messages.success(request, _("Отзыв удален."))
    return redirect('product_detail', pk=product_id)

def product_reviews(request, product_id):
    """Страница всех отзывов товара"""
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product, is_moderated=True).order_by('-created_at')
    
    # Статистика отзывов
    review_stats = reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Распределение по рейтингам
    rating_distribution = {}
    for i in range(1, 6):
        count = reviews.filter(rating=i).count()
        rating_distribution[i] = count
    
    context = {
        'product': product,
        'reviews': reviews,
        'review_stats': review_stats,
        'rating_distribution': rating_distribution,
    }
    return render(request, 'reviews/product_reviews.html', context)

@login_required
def my_reviews(request):
    """Мои отзывы"""
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'reviews': reviews,
    }
    return render(request, 'reviews/my_reviews.html', context)

@login_required
@require_POST
@csrf_exempt
def like_review(request, review_id):
    """Лайкнуть отзыв (AJAX)"""
    try:
        review = get_object_or_404(Review, id=review_id)
        # Здесь можно добавить модель для лайков отзывов
        # Пока просто возвращаем успех
        return JsonResponse({'status': 'success', 'message': _('Отзыв понравился')})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def moderate_reviews(request):
    """Модерация отзывов (для администраторов)"""
    if not request.user.is_staff:
        messages.error(request, _("У вас нет прав для модерации отзывов."))
        return redirect('index')
    
    pending_reviews = Review.objects.filter(is_moderated=False).order_by('-created_at')
    
    context = {
        'pending_reviews': pending_reviews,
    }
    return render(request, 'reviews/moderate_reviews.html', context)

@login_required
@require_POST
def approve_review(request, review_id):
    """Одобрить отзыв"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': _('Нет прав')})
    
    review = get_object_or_404(Review, id=review_id)
    review.is_moderated = True
    review.save()
    
    return JsonResponse({'status': 'success', 'message': _('Отзыв одобрен')})

@login_required
@require_POST
def reject_review(request, review_id):
    """Отклонить отзыв"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': _('Нет прав')})
    
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    
    return JsonResponse({'status': 'success', 'message': _('Отзыв отклонен')})
