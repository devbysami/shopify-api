
# Shopify API

**Version 2.3** (updated April 11, 2025)

This repository contains the implementation of a backend system using **Python**, **Django**, and **Django REST Framework** that integrates with **Shopify**. The backend manages basic product data, handles webhook callbacks, performs scheduled nightly tasks, and integrates AI features for product search and insights.

---

## Core Features

### 1. **API Endpoints**

The following CRUD operations are available for managing products:

- **GET /products/**: List all products or filter by price, SKU, name, or quantity.
- **POST /products/**: Create a new product.
- **GET /products/{id}/**: Retrieve a specific product by ID.
- **PUT /products/{id}/**: Update an existing product by ID.
- **DELETE /products/{id}/**: Delete a product by ID.
- **GET /products/search/?q=...**: Search for products using semantic similarity based on the product name using **spaCy** or **Sentence-Transformers**.

### 2. **Webhook Endpoint**
- **POST /webhooks/update-stock/**: Handle inventory updates from Shopify, updating the product quantity based on the payload received from the webhook.

### 3. **Admin Interface Customization**

- **Advanced Filtering**: Products can be filtered in the Django admin by SKU, name, and last updated timestamp.
- **Bulk Update**: Admin allows bulk updates to product prices.

### 4. **Nightly Background Tasks (Celery)**

A simplified Celery task chain runs nightly:
- **Task 1**: Import mock product data from an external CSV file.
- **Task 2**: Validate imported data and update inventory quantities.
- **Task 3**: Generate a report summarizing inventory updates and email the summary.

### 5. **AI Integration Tasks**

- **Smart Product Search**:
    - Implements semantic search using **spaCy/Sentence-Transformers** to rank products by semantic similarity.
    - Cached embeddings are stored for performance optimization.

- **Automated Insights**:
    - Endpoint: **GET /products/insights/**
    - Returns insights such as low-stock percentage and trending products based on recent stock changes.

- **AI Code Review (Leadership)**:
    - **Audit AI-generated code** for security risks (e.g., ensuring no secrets are included in prompts).

---

## Technical Considerations

### 1. **Database and Optimization**

- **Normalized Database Schema**: A normalized database schema is implemented to reduce redundancy and improve query performance.
- **Transactions**: Transactions are used to ensure data integrity, particularly for bulk operations and updates.
- **Optimized Queries**: Queries are optimized for product lookup and updates using Django ORM features like `select_related` and `prefetch_related` to avoid N+1 query problems.

### 2. **Testing**

- **Unit Tests**: Tests are written for API endpoints, Celery tasks, and webhook handling.
- **Celery Task Testing**: Tests for the full task chain from importing mock data to generating the inventory report.

---

## Deployment

### 1. **Docker Setup**

This project is Dockerized to ensure a clean and reproducible environment. To deploy the Django application with Docker, follow the steps below.

#### **Step 1: Clone the Repository**

Clone the repository to your local machine:

```bash
git clone https://github.com/devbysami/shopify-api.git
cd shopify-api
```

#### **Step 2: Build the Docker Containers**

Build the Docker containers using `docker-compose`:

```bash
sudo docker-compose build
```

#### **Step 3: Run the Docker Containers**

Start the containers (Django, PostgreSQL, and Redis):

```bash
sudo docker-compose up
```

This will start:
- The Django application at `http://localhost:2020`.
- The PostgreSQL database container (`shopify-psql`).
- The Redis container (`shopify-redis`) for Celery task queuing.

#### **Step 4: Run Migrations**

Once the containers are up and running, you may need to apply any database migrations:

```bash
sudo docker-compose exec shopify-django python manage.py migrate
```

#### **Step 5: Collect Static Files (Optional)**

If you haven't already collected static files, you can do so with:

```bash
sudo docker-compose exec shopify-django python manage.py collectstatic --noinput
```

#### **Step 6: Access the Application**

After the containers are running, the application will be available at:

```
http://localhost:2020
```

You can interact with the API endpoints using **Postman** or any HTTP client.

---

## Running Tests

To run the unit tests, including tests for the **Celery tasks**, use the following command:

```bash
python manage.py test
```

If you're using **`pytest`** for testing:

```bash
pytest
```

### **Test Case Coverage**:
- **API Endpoints**: All API endpoints are tested for CRUD operations and filtering.
- **Webhook**: Tests are included for the `update-stock` webhook functionality.
- **Celery Tasks**: Tests for the task chain that imports, validates, and updates inventory data.

---

## Leadership and Collaboration

### **Junior Developer Checklist for Code Reviews**

- **API Endpoint Design**:
    - Ensure API endpoints are RESTful and follow best practices.
    - All endpoints should be well-documented with clear error handling and correct HTTP status codes.
    - Ensure security practices are followed, including authentication and permission checks.

- **Database Query Optimization**:
    - Avoid N+1 queries by using `select_related` and `prefetch_related` when necessary.
    - Ensure queries are optimized by adding appropriate indexes.
    - Use bulk operations where applicable (e.g., `bulk_create`, `bulk_update`).

- **Django Best Practices**:
    - Use **Class-Based Views (CBVs)** for views, where appropriate, to keep the code DRY.
    - Ensure models and serializers are designed to be maintainable and reusable.
    - Use **signals** only when necessary and avoid hidden side effects.
    - **Error Handling**: Ensure all exceptions are handled properly with meaningful messages.

### **Onboarding Plan for Junior Developer**

**Week 1: Introduction and Setup**
- **Introduction**: Overview of the project, tech stack, and key features.
- **Setup**: Help the developer set up Docker, Git, and the local environment.

**Week 2: Codebase Familiarization and First Task**
- **Codebase Walkthrough**: Introduction to project structure and core components.
- **First Task**: Assign a small feature (e.g., adding a new field to the product model).
- **Review**: Conduct a code review and provide feedback.

**Week 3: Development and Testing**
- **Feature Development**: Assign a medium-sized task (e.g., creating a new API endpoint).
- **Unit Testing**: Ensure they understand how to write unit tests and run them locally.
- **Code Review**: Regular feedback on code and testing.

**Week 4: Collaboration and Independent Work**
- **Team Collaboration**: Encourage participation in team discussions and planning.
- **Independent Task**: Assign a larger task to develop independently.
- **Final Check-in**: Provide feedback and guidance for continuous improvement.

---

## Conclusion

This project is fully **Dockerized** for easy deployment and setup. You can quickly run the application, perform CRUD operations on products, process mock product data with **Celery**, and even add advanced AI-powered features like **semantic search** and **automated insights**.

Please feel free to explore the codebase, run the tests, and contribute!
