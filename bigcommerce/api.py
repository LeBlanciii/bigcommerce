import http
import json
import os
from dataclasses import dataclass
from typing import List, Optional, Union

import requests

BC_API_URL = "http://api.bigcommerce.com/stores"
STORE_V3_API_URL = "{}/{}/v3".format(BC_API_URL, os.environ['BC_STORE_HASH'])
STORE_V2_API_URL = "{}/{}/v2".format(BC_API_URL, os.environ['BC_STORE_HASH'])
session = requests.Session()
V2 = "V2"
V3 = "V3"


@dataclass
class CustomField:
    """Custom field structure for BigCommerce products."""
    name: str
    value: str


@dataclass
class ProductImage:
    """Product image structure for BigCommerce API."""
    image_url: str
    is_thumbnail: bool = False
    sort_order: int = 0
    description: Optional[str] = None
    image_file: Optional[str] = None  # For file uploads
    
    def to_dict(self) -> dict:
        """Convert the dataclass to a dictionary for API usage."""
        data = {
            "image_url": self.image_url,
            "is_thumbnail": self.is_thumbnail,
            "sort_order": self.sort_order
        }
        
        if self.description is not None:
            data["description"] = self.description
            
        if self.image_file is not None:
            data["image_file"] = self.image_file
            
        return data


@dataclass
class ProductData:
    """Product data structure for BigCommerce API.
    
    Required fields: name, type, price, categories, availability, weight
    """
    # Required fields
    name: str
    type: str  # "physical" or "digital"
    price: Union[str, float]
    categories: List[int]
    availability: str  # "available", "disabled", "preorder"
    weight: Union[str, float]
    
    # Optional fields
    description: Optional[str] = None
    is_visible: bool = True
    inventory_level: Optional[int] = None
    inventory_warning_level: Optional[int] = None
    fixed_cost_shipping_price: Optional[Union[str, float]] = None
    is_free_shipping: bool = False
    inventory_tracking: str = "none"  # "none", "product", "variant"
    custom_url: Optional[str] = None
    meta_keywords: Optional[List[str]] = None
    meta_description: Optional[str] = None
    layout_file: Optional[str] = None
    is_condition_shown: bool = False
    condition: str = "New"
    order_quantity_minimum: Optional[int] = None
    order_quantity_maximum: Optional[int] = None
    page_title: Optional[str] = None
    is_custom_price: bool = False
    price_hidden_label: Optional[str] = None
    open_graph_type: str = "product"
    open_graph_title: Optional[str] = None
    open_graph_description: Optional[str] = None
    open_graph_use_meta_description: bool = True
    open_graph_use_product_name: bool = True
    open_graph_use_image: bool = True
    
    def to_dict(self) -> dict:
        """Convert the dataclass to a dictionary for API usage."""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if field_value is not None:
                data[field_name] = field_value
        return data
    
    def validate_required_fields(self) -> None:
        """Validate that all required fields are present and valid."""
        required_fields = {
            'name': self.name,
            'type': self.type,
            'price': self.price,
            'categories': self.categories,
            'availability': self.availability,
            'weight': self.weight
        }
        
        for field_name, field_value in required_fields.items():
            if field_value is None or (isinstance(field_value, str) and field_value.strip() == ""):
                raise ValueError(f"Required field '{field_name}' cannot be empty")
        
        # Validate type
        if self.type not in ["physical", "digital"]:
            raise ValueError("Type must be 'physical' or 'digital'")
        
        # Validate availability
        if self.availability not in ["available", "disabled", "preorder"]:
            raise ValueError("Availability must be 'available', 'disabled', or 'preorder'")
        
        # Validate categories is a list
        if not isinstance(self.categories, list) or len(self.categories) == 0:
            raise ValueError("Categories must be a non-empty list of category IDs")


def set_headers(api_version):
    if api_version == V2:
        session.headers = {
            'x-auth-token': os.environ['BC_V2_TOKEN'],
            "content-type": "application/json",
            "accept": "application/json"}
    elif api_version == V3:
        session.headers = {
            'x-auth-token': os.environ['BC_V3_TOKEN'],
            "Content-Type": "application/json"}


def get_products(include_meta=True, is_visible=True, limit=100):
    set_headers(V3)
    is_visible = str(is_visible).lower()
    products = session.get(
        "{}/catalog/products?is_visible={}&limit={}".format(
            STORE_V3_API_URL, is_visible, limit)).json().get("data", None)

    if not include_meta:
        return products

    for product in products:
        product.update(get_meta(product))

    return products


def get_product_variants(product_id):
    set_headers(V3)
    variants = session.get(
        "{}/catalog/products/{}/variants".format(STORE_V3_API_URL, product_id)).json().get("data", None)
    return variants


def get_current_shipping(order_id):
    set_headers(V2)
    url = "{}/orders/{order_id}/shipping_addresses".format(STORE_V2_API_URL, order_id=order_id)
    return session.get(url).json()[0]


def update_shipping(order_id, address_id, address_mapping):
    conn = http.client.HTTPSConnection("api.bigcommerce.com")

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'x-auth-token': os.environ['BC_V2_TOKEN']
    }
    url = "{}/orders/{order_id}/shipping_addresses/{address_id}".format(
        STORE_V2_API_URL, order_id=order_id, address_id=address_id)
    conn.request("PUT", url, json.dumps(address_mapping), headers)

    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")


def get_custom_fields(product_id):
    set_headers(V3)
    return session.get("{}/catalog/products/{}/custom-fields".format(STORE_V3_API_URL, product_id)).json()


def get_brand(brand_id):
    set_headers(V3)
    brand = session.get("{}/catalog/brands/{}".format(STORE_V3_API_URL, brand_id)).json()
    return brand.get("data", {}).get("name", "")


def is_available(product):
    if not product.get("is_visible", False):
        return False
    if int(product.get("inventory_level", 0)) <= 0:
        return False
    return True


def get_meta(product):
    meta = {}
    custom_fields = get_custom_fields(product["id"])
    for cf in custom_fields.get("data", []):
        meta[cf["name"]] = cf["value"]
    return meta


def get_orders(min_date_created, max_date_created, limit=250, page=1):
    set_headers(V2)
    url = f"{STORE_V2_API_URL}/orders?min_date_created={min_date_created}&max_date_created={max_date_created}&limit=" \
          f"{limit}&page={page}"
    return session.get(url).json()


def get_order_products(order_id):
    set_headers(V2)
    url = f"{STORE_V2_API_URL}/orders/{order_id}/products"
    return session.get(url).json()


def create_product(product_data: Union[ProductData, dict], custom_fields: Optional[List[CustomField]] = None, images: Optional[List[ProductImage]] = None):
    """
    Create a new product in BigCommerce with optional custom fields and images.
    
    Args:
        product_data: ProductData instance or dictionary following BigCommerce API format
        custom_fields: List of CustomField instances or dictionaries with 'name' and 'value' keys
        images: List of ProductImage instances or dictionaries with image data
    
    Returns:
        dict: Created product data including the product ID
    """
    set_headers(V3)
    
    # Convert ProductData to dict if needed and validate
    if isinstance(product_data, ProductData):
        product_data.validate_required_fields()
        product_dict = product_data.to_dict()
    else:
        # Validate required fields for dict input
        required_fields = ["name", "type", "price", "categories", "availability", "weight"]
        for field in required_fields:
            if field not in product_data or product_data[field] is None:
                raise ValueError(f"Required field '{field}' is missing from product_data")
        product_dict = product_data
    
    # Create the product
    url = f"{STORE_V3_API_URL}/catalog/products"
    response = session.post(url, json=product_dict)
    
    if response.status_code != 201:
        raise Exception(f"Failed to create product: {response.json()}")
    
    product_response = response.json()
    product_id = product_response.get('data', {}).get('id')
    
    if not product_id:
        raise Exception("Product ID not found in response")
    
    # Add custom fields if provided
    if custom_fields:
        for field in custom_fields:
            # Convert CustomField to dict if needed
            if isinstance(field, CustomField):
                field_dict = {"name": field.name, "value": field.value}
            else:
                field_dict = field
                
            custom_field_url = f"{STORE_V3_API_URL}/catalog/products/{product_id}/custom-fields"
            custom_field_response = session.post(custom_field_url, json=field_dict)
            
            if custom_field_response.status_code != 201:
                raise Exception(f"Failed to add custom field '{field_dict.get('name', 'unknown')}': {custom_field_response.json()}")
    
    # Add images if provided
    if images:
        for image in images:
            # Convert ProductImage to dict if needed
            if isinstance(image, ProductImage):
                image_dict = image.to_dict()
            else:
                image_dict = image
                
            image_url = f"{STORE_V3_API_URL}/catalog/products/{product_id}/images"
            image_response = session.post(image_url, json=image_dict)
            
            if image_response.status_code != 201:
                raise Exception(f"Failed to add product image: {image_response.json()}")
    
    return product_response


def add_custom_fields_to_product(product_id: int, custom_fields: List[Union[CustomField, dict]]):
    """
    Add custom fields to an existing product.
    
    Args:
        product_id: The ID of the product
        custom_fields: List of CustomField instances or dictionaries with 'name' and 'value' keys
    
    Returns:
        list: List of created custom field responses
    """
    set_headers(V3)
    created_fields = []
    
    for field in custom_fields:
        # Convert CustomField to dict if needed
        if isinstance(field, CustomField):
            field_dict = {"name": field.name, "value": field.value}
        else:
            field_dict = field
            
        custom_field_url = f"{STORE_V3_API_URL}/catalog/products/{product_id}/custom-fields"
        custom_field_response = session.post(custom_field_url, json=field_dict)
        
        if custom_field_response.status_code != 201:
            raise Exception(f"Failed to add custom field '{field_dict.get('name', 'unknown')}': {custom_field_response.json()}")
        
        created_fields.append(custom_field_response.json())
    
    return created_fields


def create_product_image(product_id: int, image_data: Union[ProductImage, dict]):
    """
    Create a product image in BigCommerce.
    
    Args:
        product_id: The ID of the product
        image_data: ProductImage instance or dictionary with image data
    
    Returns:
        dict: Created image data including the image ID
    """
    set_headers(V3)
    
    # Convert ProductImage to dict if needed
    if isinstance(image_data, ProductImage):
        image_dict = image_data.to_dict()
    else:
        image_dict = image_data
    
    # Validate required fields
    if "image_url" not in image_dict:
        raise ValueError("image_url is required for product images")
    
    url = f"{STORE_V3_API_URL}/catalog/products/{product_id}/images"
    response = session.post(url, json=image_dict)
    
    if response.status_code != 201:
        raise Exception(f"Failed to create product image: {response.json()}")
    
    return response.json()


def get_product_images(product_id: int):
    """
    Get all images for a product.
    
    Args:
        product_id: The ID of the product
    
    Returns:
        list: List of product images
    """
    set_headers(V3)
    url = f"{STORE_V3_API_URL}/catalog/products/{product_id}/images"
    response = session.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get product images: {response.json()}")
    
    return response.json().get("data", [])


def get_product_image(product_id: int, image_id: int):
    """
    Get a specific product image.
    
    Args:
        product_id: The ID of the product
        image_id: The ID of the image
    
    Returns:
        dict: Image data
    """
    set_headers(V3)
    url = f"{STORE_V3_API_URL}/catalog/products/{product_id}/images/{image_id}"
    response = session.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get product image: {response.json()}")
    
    return response.json().get("data", {})


def update_product_image(product_id: int, image_id: int, image_data: Union[ProductImage, dict]):
    """
    Update a product image.
    
    Args:
        product_id: The ID of the product
        image_id: The ID of the image
        image_data: ProductImage instance or dictionary with updated image data
    
    Returns:
        dict: Updated image data
    """
    set_headers(V3)
    
    # Convert ProductImage to dict if needed
    if isinstance(image_data, ProductImage):
        image_dict = image_data.to_dict()
    else:
        image_dict = image_data
    
    url = f"{STORE_V3_API_URL}/catalog/products/{product_id}/images/{image_id}"
    response = session.put(url, json=image_dict)
    
    if response.status_code != 200:
        raise Exception(f"Failed to update product image: {response.json()}")
    
    return response.json()


def delete_product_image(product_id: int, image_id: int):
    """
    Delete a product image.
    
    Args:
        product_id: The ID of the product
        image_id: The ID of the image
    
    Returns:
        bool: True if successful
    """
    set_headers(V3)
    url = f"{STORE_V3_API_URL}/catalog/products/{product_id}/images/{image_id}"
    response = session.delete(url)
    
    if response.status_code != 204:
        raise Exception(f"Failed to delete product image: {response.json()}")
    
    return True
