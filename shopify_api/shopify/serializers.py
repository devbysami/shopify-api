from rest_framework import serializers
from shopify.models import Product
from rest_framework.validators import UniqueValidator

class ProductSerializer(serializers.Serializer):
    
    sku = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Product.objects.all())])
    name = serializers.CharField(required=True)
    quantity = serializers.IntegerField(required=True)
    price = serializers.IntegerField(required=True)
    
    class Meta:
        model = Product
        fields = ['sku', 'name', 'quantity', "price"]
        
    def create(self, validated_data):
        return Product.objects.create(**validated_data)