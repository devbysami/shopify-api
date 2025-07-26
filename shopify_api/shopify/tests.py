from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from shopify.models import Product, MockProductData
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Permission, Group
import os
import pandas as pd
import tempfile
from shopify.tasks import *

class TestShopify(APITestCase):
    
    def setUp(self):
        
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        
        self.group_edit = Group.objects.create(name="Product Edit")
        self.group_read = Group.objects.create(name="Product Read")
        
        permission_edit = Permission.objects.get(codename="can_edit_product")
        permission_read = Permission.objects.get(codename="can_view_product")
        
        self.group_read.permissions.add(permission_read)
        self.group_edit.permissions.add(permission_edit)
        
        self.user.groups.add(self.group_edit)
        self.user.groups.add(self.group_read)
        
        self.token = Token.objects.create(user=self.user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        cache_path = "/tmp/product_embeddings_cache.pkl"
        if os.path.exists(cache_path):
            os.remove(cache_path)
            
    def test_product_search(self):
        
        product = Product.objects.create(name="Test Product", sku="12345", price=100, quantity=10)

        search_url = reverse('semantic_search')
        response = self.client.get(search_url, {'q': 'Test Product'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("Test Product", response.data["results"][0]["name"])
    

    def test_product_insights(self):
        
        low_stock_product = Product.objects.create(name="Low Stock Product", sku="12346", price=50, quantity=5)
        trending_product = Product.objects.create(name="Trending Product", sku="98765", price=100, quantity=90)
        
        trending_product.quantity = 100
        trending_product.save()
        
        trending_product.quantity = 50
        trending_product.save()
        
        trending_product.quantity = 15
        trending_product.save()

        insights_url = reverse('insights')
        response = self.client.get(insights_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("low_stock_percentage", response.data)
        self.assertIn("trending_products", response.data)
        
        self.assertEqual("Trending Product", response.data["trending_products"][0]["name"])

    def test_webhook_update_stock(self):
        
        product = Product.objects.create(name="Webhook Product", sku="12347", price=100, quantity=10)

        webhook_url = reverse('update-inventory')
        webhook_data = {"sku": "12347", "quantity": 20}
        response = self.client.put(webhook_url, webhook_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product.refresh_from_db()
        self.assertEqual(product.quantity, 20)


    def test_create_product(self):
        
        product_data = {
            "name": "New Product",
            "sku": "12349",
            "price": 150,
            "quantity": 50
        }

        create_url = reverse('product-list')
        response = self.client.post(create_url, product_data, format='json')
        
        self.assertEqual(response.status_code, 200)

        self.assertTrue(Product.objects.filter(sku="12349").exists())
        
    def test_async_import_mock_products_file(self):
        
        product_data = {
            'sku': ['12345', '12346'],
            'name': ['Test Product 1', 'Test Product 2'],
            'quantity': [10, 20],
            'price': [100, 200]
        }
        df = pd.DataFrame(product_data)
        
        with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as tmp_file:
            
            df.to_csv(tmp_file, index=False)
            tmp_file.close()
            
            async_import_mock_products_file(tmp_file.name)
                                    
            mock_products = MockProductData.objects.all().order_by("-id").first()

            self.assertEqual(tmp_file.name.split("/")[-1], mock_products.file.name.split("/")[-1])
            
            async_validate_and_populate_mock_products(mock_products.id)
            
            products_created = Product.objects.filter(sku__in=product_data["sku"])
            
            self.assertEqual(products_created.count(), 2)
            
            async_generate_inventory_update_report()
            
            os.remove(tmp_file.name)