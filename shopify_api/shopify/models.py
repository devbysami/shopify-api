from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

class Product(models.Model):
    
    name = models.CharField(max_length=256)
    sku = models.CharField(max_length=256, db_index=True)
    price = models.PositiveIntegerField()
    quantity = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def last_update_at(self):
        return int(self.updated_at.timestamp() * 1000) # Timestamp in ms
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        
        if self.pk:
            
            previous_instance = Product.objects.get(pk=self.pk)
            
            if previous_instance.quantity != self.quantity:
                ProductHistory.objects.create(
                    product=self,
                    previous_quantity=previous_instance.quantity,
                    current_quantity=self.quantity,
                    type=ProductHistory.STOCK_CHANGE
                )
            
            elif previous_instance.price != self.price:
                ProductHistory.objects.create(
                    product=self,
                    previous_quantity=previous_instance.quantity,
                    current_quantity=self.quantity,
                    type=ProductHistory.PRICE_CHANGE
                )
        
        from shopify.utils import remove_cache_embeddings
        remove_cache_embeddings()
        
        super(Product, self).save(*args, **kwargs)
        
    class Meta:
        permissions = [
            ("can_view_product", "Can read product"),
            ("can_edit_product", "Can edit product"),
        ]
        
class MockProductData(models.Model):
    
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]
    
    file = models.FileField(upload_to='mock_product_data/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    failure_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    celery_task_id = models.CharField(max_length=256, null=True, blank=True)
    changes_summary = JSONField(default=dict, blank=True)

    def __str__(self):
        return f"MockProductData {self.id} - {self.status}"
    

class ProductHistory(models.Model):
    
    STOCK_CHANGE = "STOCK"
    PRICE_CHANGE = "PRICE"
    
    CHANGE_TYPES = (
        (STOCK_CHANGE, STOCK_CHANGE),
        (PRICE_CHANGE, PRICE_CHANGE)
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=CHANGE_TYPES)
    previous_quantity = models.IntegerField()
    current_quantity = models.IntegerField()
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Product: {self.product.name}"