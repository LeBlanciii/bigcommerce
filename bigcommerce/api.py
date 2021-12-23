import http
import json
import os

import requests

BC_API_URL = "http://api.bigcommerce.com/stores"
STORE_V3_API_URL = "{}/{}/v3".format(BC_API_URL, os.environ['BC_STORE_HASH'])
STORE_V2_API_URL = "{}/{}/v2".format(BC_API_URL, os.environ['BC_STORE_HASH'])
session = requests.Session()
V2 = "V2"
V3 = "V3"


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
