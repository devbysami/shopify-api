from shopify.models import Product, ProductHistory
import numpy as np
import joblib
import spacy
from collections import defaultdict
from django.utils import timezone
from datetime import timedelta
import os


nlp = spacy.load("en_core_web_md")

def get_product_embeddings():
    
    products = Product.objects.all()
    product_names = [product.name for product in products]
    
    product_embeddings = [nlp(name).vector for name in product_names]
    
    return product_embeddings, products

def get_cached_product_embeddings():
    
    cache_path = "/tmp/product_embeddings_cache.pkl"
    
    try:
        product_embeddings, products = joblib.load(cache_path)
    except FileNotFoundError:
        
        product_embeddings, products = get_product_embeddings()
        joblib.dump((product_embeddings, products), cache_path)
    
    return product_embeddings, products

def semantic_search(query, top_n=10):
    
    query_embedding = nlp(query).vector
    
    product_embeddings, products = get_cached_product_embeddings()
    
    similarities = []
    
    for product_embedding in product_embeddings:
        similarity = np.dot(query_embedding, product_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(product_embedding))
        similarities.append(similarity)
    
    ranked_products = sorted(zip(products, similarities), key=lambda x: x[1], reverse=True)
    
    return ranked_products[:top_n]

def get_product_insights():
    
    low_stock_threshold = 10
    low_stock_products = Product.objects.filter(quantity__lt=low_stock_threshold)
    low_stock_percentage = (low_stock_products.count() / Product.objects.count()) * 100
    
    trending_products = detect_trending_products(top_n=5)

    return {
        "low_stock_percentage": round(low_stock_percentage , 2),
        "trending_products": [
            {
                "name" : product.name,
                "price" : product.price,
                "sku" : product.sku
            }
            for product in trending_products
        ]
    }
    
def detect_trending_products(top_n=10):
    
    one_week_ago = timezone.now() - timedelta(days=7)
    
    stock_changes = ProductHistory.objects.filter(updated_at__gte=one_week_ago)
    
    product_changes = defaultdict(int)
    
    for change in stock_changes:
        total_change = abs(change.current_quantity - change.previous_quantity)
        product_changes[change.product] += total_change
        
    sorted_products = sorted(product_changes.items(), key=lambda x: x[1], reverse=True)
    
    trending_products = [product for product, _ in sorted_products[:top_n]]
    
    return trending_products

def remove_cache_embeddings():
    
    cache_path = "/tmp/product_embeddings_cache.pkl"
    if os.path.exists(cache_path):
        os.remove(cache_path)