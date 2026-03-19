# INNOMATICS-INTERNSHIP-FAST-API-FINAL-PROJECT-FOOD-DELIEVRY-APP-
# 🍕 QuickBite — Food Delivery Service

A fully functional Food Delivery Service backend built using **FastAPI** as part of my internship final project at **Innomatics Research Labs**.

This project covers all concepts from Day 1 to Day 6 — GET APIs, POST with Pydantic validation, helper functions, CRUD operations, multi-step workflows, search, sorting, and pagination.

---

## 🚀 How to Run

```bash
# Step 1 — Install dependencies
pip install -r requirements.txt

# Step 2 — Start the server
uvicorn main:app --reload

# Step 3 — Open Swagger UI
http://127.0.0.1:8000/docs
```

---

## 📁 Project Structure

```
fastapi-quickbite-food-delivery/
│
├── main.py              # All API endpoints
├── requirements.txt     # Dependencies
├── README.md            # Project documentation
└── screenshots/         # Swagger screenshots for all 20 questions
```

---

## ✨ Features Implemented

| Day | Concept | What I Built |
|-----|---------|--------------|
| Day 1 | GET APIs | Home route, full menu, item by ID, orders list, menu summary |
| Day 2 | POST + Pydantic | `OrderRequest` with field validation and error handling |
| Day 3 | Helper Functions | `find_menu_item()`, `calculate_bill()`, `filter_menu_logic()` |
| Day 4 | CRUD Operations | Add item, update price/availability, delete item |
| Day 5 | Multi-step Workflow | Cart → Add items → Checkout → Place orders |
| Day 6 | Search, Sort, Pagination | Keyword search, sorting, pagination, combined browse |

---

## 📋 All 20 API Endpoints

### 🟢 Day 1 — GET APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/menu` | List all menu items with total count |
| GET | `/menu/{item_id}` | Get a specific item by ID |
| GET | `/orders` | List all orders |
| GET | `/menu/summary` | Stats — available count, unavailable count, categories |

### 🔵 Day 2 + Day 3 — POST & Helpers

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Create an order with full cost breakdown |

**Pydantic Validation Rules:**
- `customer_name` — min 2 characters
- `item_id` — must be greater than 0
- `quantity` — between 1 and 20
- `delivery_address` — min 10 characters
- `order_type` — `'delivery'` (default) or `'pickup'`

**Cost Calculation Logic:**
- Base cost = `price × quantity`
- `delivery` order → +₹30 delivery charge
- `pickup` order → no extra charge

### 🟡 Day 3 — Filter

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/menu/filter` | Filter by `category`, `max_price`, `is_available` |

### 🟠 Day 4 — CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/menu` | Add new item (rejects duplicate name) |
| PUT | `/menu/{item_id}` | Update price or availability |
| DELETE | `/menu/{item_id}` | Delete a menu item |

### 🩵 Day 5 — Cart Workflow

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/cart/add` | Add item to cart (updates quantity if already present) |
| GET | `/cart` | View all cart items and grand total |
| DELETE | `/cart/{item_id}` | Remove a specific item from cart |
| POST | `/cart/checkout` | Place orders for all cart items, clear cart |

### 🔴 Day 6 — Search, Sort, Pagination

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/menu/search` | Keyword search across name and category |
| GET | `/menu/sort` | Sort by `price`, `name`, or `category` |
| GET | `/menu/page` | Paginate menu with `total_pages` |
| GET | `/orders/search` | Search orders by customer name |
| GET | `/orders/sort` | Sort orders by `total_price` |
| GET | `/menu/browse` | Combined — keyword + sort + paginate |

---

## 🧪 Sample Data

The project comes with 7 pre-loaded menu items:

| Name | Category | Price | Available |
|------|----------|-------|-----------|
| Margherita Pizza | Pizza | ₹299 | ✅ |
| Pepperoni Pizza | Pizza | ₹349 | ✅ |
| Classic Burger | Burger | ₹199 | ✅ |
| Cheese Burger | Burger | ₹229 | ❌ |
| Coke | Drink | ₹59 | ✅ |
| Chocolate Brownie | Dessert | ₹99 | ✅ |
| Mango Shake | Drink | ₹89 | ✅ |

---

## 🧠 Key Concepts Demonstrated

- **Pydantic models** with field-level validation (`Field`, `min_length`, `gt`, `le`)
- **Helper functions** (`find_menu_item`, `calculate_bill`, `filter_menu_logic`) kept separate from route handlers
- **HTTP status codes** — `201 Created`, `400 Bad Request`, `404 Not Found`
- **Route ordering** — fixed routes (`/menu/summary`, `/menu/filter`) placed before variable routes (`/menu/{item_id}`)
- **Cart system** with duplicate detection and quantity merging
- **Checkout workflow** — multi-item order creation from cart in a single request
- **Combined browse endpoint** — filter → sort → paginate in one call

---

##  Acknowledgement

Thanks to **Innomatics Research Labs** for the structured FastAPI internship training. This project helped me understand how to design real-world REST APIs, structure backend systems, and implement complete application workflows.
