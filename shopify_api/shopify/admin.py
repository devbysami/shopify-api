from django.contrib import admin
from shopify.models import *
from shopify.forms import BulkUpdatePriceForm, ApplyDiscountForm
from django.shortcuts import render
from django.urls import path
from django.http import HttpResponseRedirect
from django.urls import reverse

def update_price(modeladmin, request, queryset):
    
    if 'apply' in request.POST:
        
        form = BulkUpdatePriceForm(request.POST)
        
        if form.is_valid():
                        
            price = form.cleaned_data['price']
                        
            updated_count = queryset.update(price=price)            
            modeladmin.message_user(request, f"{updated_count} products' prices updated to {price}.")
                        
            return HttpResponseRedirect(reverse('admin:shopify_product_changelist'))
    else:
        
        form = BulkUpdatePriceForm()

    context = modeladmin.admin_site.each_context(request)

    context.update({
        'form': form,
        'queryset': queryset,
        'title': "Bulk Update Product Price",
        'app_label': 'shopify'
    })

    return render(request, 'admin/bulk_update_price.html', context)

update_price.short_description = "Bulk Update price"

def apply_discount_to_selected(modeladmin, request, queryset):
    
    if 'apply_discount' in request.POST:
        
        form = ApplyDiscountForm(request.POST)
        
        if form.is_valid():
            
            discount = form.cleaned_data['discount']
            
            for product in queryset:
                
                if discount.type == Discount.FIXED:
                    discounted_price = product.price - discount.value
                    
                elif discount.type == Discount.PERCENTAGE:
                    discounted_price = product.price * (1 - discount.value / 100)
                    
                product.discounted_price = discounted_price
                product.save()

            modeladmin.message_user(request, "Discount applied successfully!")
            return HttpResponseRedirect(reverse('admin:shopify_product_changelist'))

    else:
        
        form = ApplyDiscountForm()

    context = {
        'form': form,
        'queryset': queryset,
        'title': "Apply Discount to Selected Products",
    }

    return render(request, 'admin/apply_discount.html', context)

apply_discount_to_selected.short_description = "Apply Discount to selected products"

class ProductAdmin(admin.ModelAdmin):
    
    model = Product
    list_display = ('name', 'sku', 'price', 'quantity', "discounted_price", 'last_update_at')
    search_fields = ('sku', 'name')
    list_filter = ["quantity"]
    date_hierarchy = 'updated_at'
    list_select_related = True
    actions = [update_price, apply_discount_to_selected]

    def get_urls(self):
        
        urls = super().get_urls()
        custom_urls = [
            path('bulk_update_price/', self.admin_site.admin_view(self.bulk_update_view), name='bulk_update_price'),
            path('apply_discount/', self.admin_site.admin_view(self.apply_discount_view), name='apply_discount'),
        ]
        return custom_urls + urls
    
    def bulk_update_view(self, request):
        
        selected = request.POST.getlist('_selected_action')
        queryset = Product.objects.filter(id__in=selected)

        return update_price(self, request, queryset)
    
    def apply_discount_view(self, request):
        
        selected = request.POST.getlist('_selected_action')
        queryset = Product.objects.filter(id__in=selected)

        return apply_discount_to_selected(self, request, queryset)


class DiscountAdmin(admin.ModelAdmin):
    
    list_display = ['name', 'type', 'value', 'created_at']
    search_fields = ['name']
    list_filter = ['type']


admin.site.register(Product, ProductAdmin)
admin.site.register(Discount, DiscountAdmin)