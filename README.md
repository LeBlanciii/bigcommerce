# BigCommerce API Python Client

[![PyPI version](https://badge.fury.io/py/bigcommerce.svg)](https://badge.fury.io/py/bigcommerce)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python client for the BigCommerce API, providing easy-to-use functions for managing products, orders, custom fields, and images.

## Features

- **Product Management**: Create, retrieve, and manage products with full support for variants
- **Order Processing**: Access order data and shipping information
- **Custom Fields**: Add and manage custom product fields
- **Image Management**: Upload, update, and delete product images
- **Type Safety**: Full type hints and dataclass support for better development experience
- **Error Handling**: Comprehensive error handling with meaningful messages

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Installation

### From PyPI (Recommended)

```bash
pip install bigcommerce
```

### Development Installation

#### From GitHub Repository

```bash
git clone https://github.com/LeBlanciii/bigcommerce.git
cd bigcommerce
pip install -e .
```

#### Direct from GitHub in requirements.txt

Add to your `requirements.txt`:

```txt
git+https://github.com/LeBlanciii/bigcommerce.git
```

Then install:

```bash
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- requests

## Configuration

### Environment Variables

You must set the following environment variables:

```bash
export BC_V2_TOKEN="your_v2_api_token"
export BC_V3_TOKEN="your_v3_api_token"
export BC_STORE_HASH="your_store_hash"
```

### Obtaining API Tokens

1. **V2 Token**: Go to your BigCommerce store admin → Settings → API Accounts → Create API Account
2. **V3 Token**: Use the same API account but ensure it has V3 API access
3. **Store Hash**: Found in your store URL: `https://store-{STORE_HASH}.mybigcommerce.com`

### Example .env File

Create a `.env` file in your project root:

```env
BC_V2_TOKEN=your_v2_token_here
BC_V3_TOKEN=your_v3_token_here
BC_STORE_HASH=your_store_hash_here
```

## Quick Start

```python
from bigcommerce.api import get_products, create_product, ProductData

# Get all products
products = get_products()

# Create a new product
product_data = ProductData(
    name="My New Product",
    type="physical",
    price=29.99,
    categories=[1, 2],  # Category IDs
    availability="available",
    weight=1.0
)

new_product = create_product(product_data)
print(f"Created product with ID: {new_product['data']['id']}")
```

## Usage Examples

### Product Management

#### Creating Products with Custom Fields and Images

```python
from bigcommerce.api import (
    create_product, ProductData, CustomField, ProductImage
)

# Create product data
product_data = ProductData(
    name="Premium Widget",
    type="physical",
    price=99.99,
    categories=[1],
    availability="available",
    weight=2.5,
    description="A high-quality widget for all your needs",
    inventory_level=100
)

# Add custom fields
custom_fields = [
    CustomField(name="Material", value="Stainless Steel"),
    CustomField(name="Warranty", value="2 Years")
]

# Add product images
images = [
    ProductImage(
        image_url="https://example.com/image1.jpg",
        is_thumbnail=True,
        sort_order=1
    ),
    ProductImage(
        image_url="https://example.com/image2.jpg",
        is_thumbnail=False,
        sort_order=2
    )
]

# Create the product
result = create_product(product_data, custom_fields, images)
print(f"Product created: {result['data']['id']}")
```

#### Retrieving Products

```python
from bigcommerce.api import get_products, get_product_variants

# Get all visible products
products = get_products(include_meta=True, is_visible=True, limit=50)

# Get product variants
variants = get_product_variants(product_id=123)

# Check if product is available
from bigcommerce.api import is_available
for product in products:
    if is_available(product):
        print(f"Product {product['name']} is available")
```

### Order Management

```python
from bigcommerce.api import get_orders, get_order_products
from datetime import datetime

# Get orders from the last 30 days
from datetime import datetime, timedelta
thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
today = datetime.now().strftime('%Y-%m-%d')

orders = get_orders(
    min_date_created=thirty_days_ago,
    max_date_created=today,
    limit=100
)

# Get products for a specific order
order_products = get_order_products(order_id=12345)
```

### Custom Fields Management

```python
from bigcommerce.api import (
    get_custom_fields, add_custom_fields_to_product, CustomField
)

# Get custom fields for a product
custom_fields = get_custom_fields(product_id=123)

# Add custom fields to an existing product
new_fields = [
    CustomField(name="Color", value="Blue"),
    CustomField(name="Size", value="Large")
]

result = add_custom_fields_to_product(product_id=123, custom_fields=new_fields)
```

### Image Management

```python
from bigcommerce.api import (
    create_product_image, get_product_images, update_product_image,
    delete_product_image, ProductImage
)

# Create a product image
image_data = ProductImage(
    image_url="https://example.com/new-image.jpg",
    is_thumbnail=False,
    sort_order=3,
    description="Product detail view"
)

new_image = create_product_image(product_id=123, image_data=image_data)

# Get all images for a product
images = get_product_images(product_id=123)

# Update an image
updated_image = update_product_image(
    product_id=123,
    image_id=456,
    image_data={"description": "Updated description"}
)

# Delete an image
delete_product_image(product_id=123, image_id=456)
```

### Shipping Management

```python
from bigcommerce.api import get_current_shipping, update_shipping

# Get current shipping address for an order
shipping = get_current_shipping(order_id=12345)

# Update shipping address
address_mapping = {
    "first_name": "John",
    "last_name": "Doe",
    "address_1": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip": "12345",
    "country": "United States"
}

result = update_shipping(
    order_id=12345,
    address_id=1,
    address_mapping=address_mapping
)
```

## API Reference

### Dataclasses

#### ProductData
Main product data structure with required and optional fields.

**Required Fields:**
- `name` (str): Product name
- `type` (str): "physical" or "digital"
- `price` (Union[str, float]): Product price
- `categories` (List[int]): List of category IDs
- `availability` (str): "available", "disabled", or "preorder"
- `weight` (Union[str, float]): Product weight

**Optional Fields:**
- `description` (str): Product description
- `is_visible` (bool): Whether product is visible
- `inventory_level` (int): Stock level
- `inventory_warning_level` (int): Low stock warning level
- `fixed_cost_shipping_price` (Union[str, float]): Fixed shipping cost
- `is_free_shipping` (bool): Free shipping flag
- `inventory_tracking` (str): "none", "product", or "variant"
- `custom_url` (str): Custom product URL
- `meta_keywords` (List[str]): SEO keywords
- `meta_description` (str): SEO description
- And many more...

#### CustomField
Custom field structure for products.

- `name` (str): Field name
- `value` (str): Field value

#### ProductImage
Product image structure.

- `image_url` (str): Image URL
- `is_thumbnail` (bool): Whether this is the thumbnail image
- `sort_order` (int): Display order
- `description` (Optional[str]): Image description
- `image_file` (Optional[str]): For file uploads

### Functions

#### Product Functions

- `get_products(include_meta=True, is_visible=True, limit=100)`: Get products
- `create_product(product_data, custom_fields=None, images=None)`: Create product
- `get_product_variants(product_id)`: Get product variants
- `is_available(product)`: Check if product is available

#### Order Functions

- `get_orders(min_date_created, max_date_created, limit=250, page=1)`: Get orders
- `get_order_products(order_id)`: Get products for an order

#### Shipping Functions

- `get_current_shipping(order_id)`: Get shipping address
- `update_shipping(order_id, address_id, address_mapping)`: Update shipping

#### Custom Field Functions

- `get_custom_fields(product_id)`: Get custom fields
- `add_custom_fields_to_product(product_id, custom_fields)`: Add custom fields

#### Image Functions

- `create_product_image(product_id, image_data)`: Create product image
- `get_product_images(product_id)`: Get all product images
- `get_product_image(product_id, image_id)`: Get specific image
- `update_product_image(product_id, image_id, image_data)`: Update image
- `delete_product_image(product_id, image_id)`: Delete image

#### Brand Functions

- `get_brand(brand_id)`: Get brand information

## Error Handling

The client includes comprehensive error handling:

```python
try:
    product = create_product(product_data)
except Exception as e:
    print(f"Failed to create product: {e}")
```

## Rate Limiting

BigCommerce has API rate limits. The client uses a session for connection pooling, but you should implement appropriate delays for bulk operations.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [BigCommerce API Documentation](https://developer.bigcommerce.com/api-reference)
- [BigCommerce Developer Portal](https://developer.bigcommerce.com/)
- [Package on PyPI](https://pypi.org/project/bigcommerce/)
