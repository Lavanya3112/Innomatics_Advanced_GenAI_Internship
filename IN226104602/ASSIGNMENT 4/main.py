from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# ──────────────────────────────────────────
# Product catalogue (in-memory)
# ──────────────────────────────────────────
products = [
    {"product_id": 1, "name": "Wireless Mouse",  "price": 499, "in_stock": True},
    {"product_id": 2, "name": "Notebook",         "price":  99, "in_stock": True},
    {"product_id": 3, "name": "USB Hub",           "price": 299, "in_stock": False},
    {"product_id": 4, "name": "Pen Set",           "price":  49, "in_stock": True},
]

# ──────────────────────────────────────────
# In-memory cart and orders
# ──────────────────────────────────────────
cart   = []   # list of cart-item dicts
orders = []   # list of order dicts
order_counter = 0


# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────
def get_product(product_id: int):
    for p in products:
        if p["product_id"] == product_id:
            return p
    return None


def calculate_subtotal(product: dict, quantity: int) -> int:
    return product["price"] * quantity


# ──────────────────────────────────────────
# Schema for checkout
# ──────────────────────────────────────────
class CheckoutRequest(BaseModel):
    customer_name:    str
    delivery_address: str


# ══════════════════════════════════════════
# CART ENDPOINTS
# ══════════════════════════════════════════

# POST /cart/add
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    product = get_product(product_id)

    # 404 — product doesn't exist
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 400 — product exists but is out of stock
    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    # If already in cart → update quantity
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"]  = calculate_subtotal(product, item["quantity"])
            return {"message": "Cart updated", "cart_item": item}

    # New item → append
    cart_item = {
        "product_id":   product["product_id"],
        "product_name": product["name"],
        "quantity":     quantity,
        "unit_price":   product["price"],
        "subtotal":     calculate_subtotal(product, quantity),
    }
    cart.append(cart_item)
    return {"message": "Added to cart", "cart_item": cart_item}


# GET /cart
@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)
    return {
        "items":       cart,
        "item_count":  len(cart),
        "grand_total": grand_total,
    }


# DELETE /cart/{product_id}
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    raise HTTPException(status_code=404, detail="Item not found in cart")


# POST /cart/checkout
@app.post("/cart/checkout")
def checkout(request: CheckoutRequest):
    global order_counter

    # Bonus — reject empty cart
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")

    orders_placed = []

    for item in cart:
        order_counter += 1
        order = {
            "order_id":        order_counter,
            "customer_name":   request.customer_name,
            "delivery_address": request.delivery_address,
            "product":         item["product_name"],
            "quantity":        item["quantity"],
            "total_price":     item["subtotal"],
        }
        orders.append(order)
        orders_placed.append(order)

    grand_total = sum(o["total_price"] for o in orders_placed)

    # Clear cart after checkout
    cart.clear()

    return {
        "message":      "Checkout successful",
        "orders_placed": orders_placed,
        "grand_total":  grand_total,
    }


# ══════════════════════════════════════════
# ORDERS ENDPOINT
# ══════════════════════════════════════════

# GET /orders
@app.get("/orders")
def get_orders():
    if not orders:
        return {"message": "No orders yet"}

    return {
        "orders":       orders,
        "total_orders": len(orders),
    }