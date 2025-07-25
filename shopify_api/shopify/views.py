from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from shopify.models import Product
from shopify.serializers import ProductSerializer
from rest_framework.pagination import PageNumberPagination
from shopify.permissions import CanReadProducts, CanEditProducts

class ProductView(APIView):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, CanReadProducts]

    def get(self, request, *args, **kwargs):
        
        name = request.GET.get("name")
        sku = request.GET.get("sku")
        price = request.GET.get("price")
        quantity = request.GET.get("quantity")
        
        products = Product.objects.all()

        if name:
            products = products.filter(name__icontains=name)
            
        if sku:
            products = products.filter(sku__icontains=sku)
            
        if price:
            products = products.filter(price=price)
            
        if quantity:
            products = products.filter(quantity=quantity)
        
        if not products:
            return Response({
                "success": False,
                "message": "No products found."
            }, status=400)
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(products, request)
        
        serializer = ProductSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        
        serializer = ProductSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        
        return Response({"success" : True, "message" : "Product Created"}, status=200)
    
class UpdateInventory(APIView):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, CanEditProducts]
    
    def put(self, request, *args, **kwargs):
        
        sku = request.data.get('sku', "")
        quantity = request.data.get('quantity')
        
        if quantity is None:
            return Response({"success": False, "message": "Missing Quantity in request."}, status=400)
        
        try:
            product = Product.objects.get(sku=sku)
        except Product.DoesNotExist:
            return Response({"success": False, "message": "Product not found. Invalid SKU"}, status=404)
        
        product.quantity = int(quantity)
        product.save()
        
        return Response({
            "success" : True,
            "message" : f"Product {product.name} updated succesfully"
        }, status=200)