from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()


# ─────────────────────────────────────────────────────────────
#  PRODUCT DATA
# ─────────────────────────────────────────────────────────────
products = [
    {"id": 1, "name": "Wireless Mouse",      "price": 799,  "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook",            "price": 149,  "category": "Stationery",  "in_stock": True},
    {"id": 3, "name": "USB Hub",             "price": 999,  "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set",             "price": 49,   "category": "Stationery",  "in_stock": True},
    {"id": 5, "name": "Laptop Stand",        "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam",              "price": 1899, "category": "Electronics", "in_stock": False},
]

feedback = []
orders   = []
order_id_counter = 1


# ─────────────────────────────────────────────────────────────
#  PYDANTIC MODELS
# ─────────────────────────────────────────────────────────────
class CustomerFeedback(BaseModel):
    customer_name: str           = Field(..., min_length=2, max_length=100)
    product_id:    int           = Field(..., gt=0)
    rating:        int           = Field(..., ge=1, le=5)
    comment:       Optional[str] = Field(None, max_length=300)


class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity:   int = Field(..., gt=0, le=50)


class BulkOrder(BaseModel):
    company_name:  str             = Field(..., min_length=2)
    contact_email: str             = Field(..., min_length=5)
    items:         List[OrderItem] = Field(..., min_length=1)


class SingleOrder(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id:    int = Field(..., gt=0)
    quantity:      int = Field(..., gt=0, le=50)


# ═════════════════════════════════════════════════════════════
#  DAY 1 — Q1   All Products
# ═════════════════════════════════════════════════════════════
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


# ═════════════════════════════════════════════════════════════
#  DAY 1 — Q2   Filter by Category
# ═════════════════════════════════════════════════════════════
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    result = [p for p in products if p["category"] == category_name]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result, "total": len(result)}


# ═════════════════════════════════════════════════════════════
#  DAY 1 — Q3   In-Stock Products Only
# ═════════════════════════════════════════════════════════════
@app.get("/products/instock")
def get_instock():
    available = [p for p in products if p["in_stock"] == True]
    return {"in_stock_products": available, "count": len(available)}


# ═════════════════════════════════════════════════════════════
#  DAY 1 — Q5   Search by Keyword
# ═════════════════════════════════════════════════════════════
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    results = [p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": "No products matched your search"}
    return {"keyword": keyword, "results": results, "total_matches": len(results)}


# ═════════════════════════════════════════════════════════════
#  DAY 1 — BONUS   Cheapest & Most Expensive
# ═════════════════════════════════════════════════════════════
@app.get("/products/deals")
def get_deals():
    cheapest  = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])
    return {
        "best_deal":    cheapest,
        "premium_pick": expensive,
    }


# ═════════════════════════════════════════════════════════════
#  DAY 1 — Q4   Store Summary
# ═════════════════════════════════════════════════════════════
@app.get("/store/summary")
def store_summary():
    in_stock_count  = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count
    categories      = list(set([p["category"] for p in products]))
    return {
        "store_name":     "My E-commerce Store",
        "total_products": len(products),
        "in_stock":       in_stock_count,
        "out_of_stock":   out_stock_count,
        "categories":     categories,
    }


# ═════════════════════════════════════════════════════════════
#  DAY 2 — Q1   Filter Products by Minimum Price
# ═════════════════════════════════════════════════════════════
@app.get("/products/filter")
def filter_products(
    category:  str = Query(None, description="Filter by category"),
    max_price: int = Query(None, description="Maximum price"),
    min_price: int = Query(None, description="Minimum price"),
):
    result = products[:]
    if category:
        result = [p for p in result if p["category"] == category]
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]
    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]
    return {"products": result, "total": len(result)}


# ═════════════════════════════════════════════════════════════
#  DAY 2 — Q4   Product Summary Dashboard
#  NOTE: kept above /{product_id}/price to avoid routing conflict
# ═════════════════════════════════════════════════════════════
@app.get("/products/summary")
def product_summary():
    in_stock   = [p for p in products if p["in_stock"]]
    out_stock  = [p for p in products if not p["in_stock"]]
    expensive  = max(products, key=lambda p: p["price"])
    cheapest   = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))
    return {
        "total_products":     len(products),
        "in_stock_count":     len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive":     {"name": expensive["name"], "price": expensive["price"]},
        "cheapest":           {"name": cheapest["name"],  "price": cheapest["price"]},
        "categories":         categories,
    }


# ═════════════════════════════════════════════════════════════
#  DAY 2 — Q2   Get Only Price of a Product
#  NOTE: dynamic route — must be after all fixed /products/... routes
# ═════════════════════════════════════════════════════════════
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return {"name": p["name"], "price": p["price"]}
    return {"error": "Product not found"}


# ═════════════════════════════════════════════════════════════
#  DAY 2 — Q3   Accept Customer Feedback
# ═════════════════════════════════════════════════════════════
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message":        "Feedback submitted successfully",
        "feedback":       data.dict(),
        "total_feedback": len(feedback),
    }


# ═════════════════════════════════════════════════════════════
#  DAY 2 — Q5   Validate & Place a Bulk Order
# ═════════════════════════════════════════════════════════════
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
    return {
        "company":     order.company_name,
        "confirmed":   confirmed,
        "failed":      failed,
        "grand_total": grand_total,
    }


# ═════════════════════════════════════════════════════════════
#  DAY 2 — BONUS   Order Status Tracker
# ═════════════════════════════════════════════════════════════
@app.post("/orders")
def place_order(order: SingleOrder):
    global order_id_counter
    product = next((p for p in products if p["id"] == order.product_id), None)
    if not product:
        return {"error": "Product not found"}
    if not product["in_stock"]:
        return {"error": f"{product['name']} is out of stock"}
    new_order = {
        "order_id":      order_id_counter,
        "customer_name": order.customer_name,
        "product":       product["name"],
        "quantity":      order.quantity,
        "total":         product["price"] * order.quantity,
        "status":        "pending",
    }
    orders.append(new_order)
    order_id_counter += 1
    return {"message": "Order placed", "order": new_order}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}
    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {"message": "Order confirmed", "order": order}
    return {"error": "Order not found"}
