from fastapi import FastAPI

app = FastAPI()

# ── Product Data
products = [
    {"id": 1, "name": "Wireless Mouse",       "price": 799,  "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook",             "price": 149,  "category": "Stationery",  "in_stock": True},
    {"id": 3, "name": "USB Hub",              "price": 999,  "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set",              "price": 49,   "category": "Stationery",  "in_stock": True},
    # Q1 — 3 new products
    {"id": 5, "name": "Laptop Stand",         "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard",  "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam",               "price": 1899, "category": "Electronics", "in_stock": False},
]


# ── Q1 — All Products─────────────────
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


# ── Q2 — Filter by Category ───────────────────────────────────
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    result = [p for p in products if p["category"] == category_name]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result, "total": len(result)}


# ── Q3 — In-Stock Products Only ───────────────────────────────
@app.get("/products/instock")
def get_instock():
    available = [p for p in products if p["in_stock"] == True]
    return {"in_stock_products": available, "count": len(available)}


# ── Q5 — Search by Keyword 
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]
    if not results:
        return {"message": "No products matched your search"}
    return {"keyword": keyword, "results": results, "total_matches": len(results)}


# ── Bonus — Cheapest & Most Expensive ────────────────────────
@app.get("/products/deals")
def get_deals():
    cheapest  = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])
    return {
        "best_deal":    cheapest,
        "premium_pick": expensive,
    }


# ── Q4 — Store Summary ────────────────────────────────────────
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
