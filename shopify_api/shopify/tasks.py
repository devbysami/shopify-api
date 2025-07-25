from shopify_api.celery import app
from shopify.models import MockProductData, Product
import os
from django.core.files import File
import pandas as pd
from shopify.serializers import ProductSerializer
from django.utils import timezone
from datetime import timedelta
from core.email_util import send_email
import traceback

@app.task(bind=True)
def async_import_mock_products_file(self, file_path):
    
    mock_product_obj = MockProductData.objects.create(
        status=MockProductData.PENDING,
        celery_task_id=self.request.id
    )
    
    try:
    
        if not os.path.exists(file_path):
            mock_product_obj.status = MockProductData.FAILED
            mock_product_obj.failure_reason = f"Failed to import file. No file on path {file_path}"
            mock_product_obj.save()
            
        with open(file_path, 'rb') as f:
            
            file_name = os.path.basename(file_path)
            file = File(f, name=file_name)
            
            mock_product_obj.file.save(file_name, file)
            mock_product_obj.save()
    
    except Exception as e:
        mock_product_obj.status = MockProductData.FAILED
        mock_product_obj.failure_reason = str(e)
        mock_product_obj.save()


@app.task(bind=True)
def async_validate_and_populate_mock_products(self, mock_data_id):
    
    mock_data = MockProductData.objects.get(id=mock_data_id)
    
    if mock_data.status == MockProductData.FAILED:
        return
    
    mock_data.status = MockProductData.PROCESSING
    mock_data.save()
    
    try:
        
        file_path = mock_data.file.path
        df = pd.read_csv(file_path)
        
        required_columns = ['sku', 'name', 'quantity', 'price']
        df.columns = df.columns.str.lower()
        
        for col in required_columns:
            
            if col not in df.columns:
                
                mock_data.status = MockProductData.FAILED
                mock_data.failure_reason = f"Missing column: {col}"
                mock_data.save()
                return
        
        updated_products = []
        newly_created_products = []
        discarded_products = []
        
        for index, row in df.iterrows():
            
            if row.isnull().all():
                continue
            
            if not row['sku'] or not row['name'] or pd.isnull(row['quantity']) or pd.isnull(row['price']):
                discarded_products.append(row.to_dict())
                continue
            
            product_data = {
                'sku': row['sku'],
                'name': row['name'],
                'quantity': row['quantity'],
                'price': row['price']
            }
            
            existing_product = Product.objects.filter(sku=row['sku'])
            
            if existing_product.exists():
                
                existing_product = existing_product.first()
                
                changes = []
                
                if existing_product.quantity != row['quantity']:
                    changes.append(f"Quantity From: {existing_product.quantity} >>> To: {row['quantity']}")
                    
                if existing_product.price != row['price']:
                    changes.append(f"Price From: {existing_product.price} >>> To: {row['price']}")
                
                if changes:
                    
                    updated_products.append({
                        'sku': existing_product.sku,
                        'name': existing_product.name,
                        'changes': "\n".join(changes),
                    })
                
                    existing_product.quantity = row['quantity']
                    existing_product.price = row['price']
                    existing_product.save()
                                
            else:
                
                serializer = ProductSerializer(data=product_data)
                
                if not serializer.is_valid():
                    discarded_products.append(product_data)
                    continue
                    
                serializer.save()
                
                newly_created_products.append({
                    'sku': serializer.instance.sku,
                    'name': serializer.instance.name,
                    'price': serializer.instance.price,
                    'quantity': serializer.instance.quantity,
                })
                
                                            
        mock_data.status = MockProductData.COMPLETED
        
        print("THESE ARE NEW CREATED")
        print(newly_created_products)
        
        print("These are updated")
        print(updated_products)
        
        mock_data.changes_summary = {
            'created': newly_created_products,
            'updated': updated_products,
            'discarded': discarded_products,
        }
        mock_data.save()
    
    except Exception as e:
        
        print(traceback.format_exc())
        
        mock_data.status = MockProductData.FAILED
        mock_data.failure_reason = str(e)
        mock_data.save()


@app.task(bind=True)
def async_generate_inventory_update_report(self):
    
    seven_days_ago = timezone.now() - timedelta(days=7)
    file_path = "/tmp/inventory_report.xlsx"
    
    completed_mock_data = MockProductData.objects.filter(
        status=MockProductData.COMPLETED,
        created_at__gte=seven_days_ago
    )
    
    if not completed_mock_data.exists():
        return
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        
        created_products = []
        updated_products = []
        
        for mock_data in completed_mock_data:
            
            changes_summary = mock_data.changes_summary
            
            for product in changes_summary.get('created', []):
                
                created_product = {
                    "Name" : product.get("name"),
                    "SKU": product.get("sku"),
                    "Price" : product.get('price', ''),
                    "Quantity" : product.get('quantity', '')
                }

                created_products.append(created_product)
                
            for product in changes_summary.get('updated', []):
                
                updated_product = {
                    "Name" : product.get("name"),
                    "SKU": product.get("sku"),
                    "Changes" : product.get('changes', '')
                }

                updated_products.append(updated_product)
        
        if created_products:
            
            df_created = pd.DataFrame(created_products)
            df_created.to_excel(writer, sheet_name='Created', index=False)
        
        if updated_products:
            df_updated = pd.DataFrame(updated_products)
            df_updated.to_excel(writer, sheet_name='Updated', index=False)
        
    send_email(
        subject="Inventory Update Report Last 7 days",
        body="Here is you shopify store inventory update made in past 7 days.\n Note : THIS IS UPDATE IS BASED ON MOCK PRODUCTS FILE UPLOAD",
        recipients=["samuamir555@gmail.com"],
        file_path=file_path
    )
    
    os.remove(file_path)