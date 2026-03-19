from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
import math

app = FastAPI()

# ══ MODELS ════════════════════════════════════════════════════════

class OrderRequest(BaseModel):
    customer_name:    str  = Field(..., min_length=2)
    item_id:          int  = Field(..., gt=0)
    quantity:         int  = Field(..., gt=0, le=20)
    delivery_address: str  = Field(..., min_length=10)
    order_type:       str  = Field(default='delivery')   # 'delivery' or 'pickup'

class NewMenuItem(BaseModel):
    name:         str  = Field(..., min_length=2, max_length=100)
    price:        int  = Field(..., gt=0)
    category:     str  = Field(..., min_length=2)
    is_available: bool = True

class CheckoutRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)

# ══ DATA ══════════════════════════════════════════════════════════

menu = [
    {'id': 1, 'name': 'Margherita Pizza',  'price': 299, 'category': 'Pizza',   'is_available': True},
    {'id': 2, 'name': 'Pepperoni Pizza',   'price': 349, 'category': 'Pizza',   'is_available': True},
    {'id': 3, 'name': 'Classic Burger',    'price': 199, 'category': 'Burger',  'is_available': True},
    {'id': 4, 'name': 'Cheese Burger',     'price': 229, 'category': 'Burger',  'is_available': False},
    {'id': 5, 'name': 'Coke',              'price':  59, 'category': 'Drink',   'is_available': True},
    {'id': 6, 'name': 'Chocolate Brownie', 'price':  99, 'category': 'Dessert', 'is_available': True},
    {'id': 7, 'name': 'Mango Shake',       'price':  89, 'category': 'Drink',   'is_available': True},
]

orders        = []
order_counter = 1
cart          = []

# ══ HELPERS ═══════════════════════════════════════════════════════

def find_menu_item(item_id: int):
    """Return the menu item dict if found, else None."""
    for item in menu:
        if item['id'] == item_id:
            return item
    return None


def calculate_bill(price: int, quantity: int, order_type: str = 'delivery') -> int:
    """Return total bill. Adds ₹30 delivery charge for 'delivery' orders."""
    total = price * quantity
    if order_type == 'delivery':
        total += 30
    return total


def filter_menu_logic(category=None, max_price=None, is_available=None):
    result = menu
    if category     is not None:
        result = [i for i in result if i['category'].lower() == category.lower()]
    if max_price    is not None:
        result = [i for i in result if i['price'] <= max_price]
    if is_available is not None:
        result = [i for i in result if i['is_available'] == is_available]
    return result

# ══ ENDPOINTS ═════════════════════════════════════════════════════
#
# ROUTE ORDER — fixed routes BEFORE variable /{item_id}
#
# ══════════════════════════════════════════════════════════════════

# ── Day 1 ─────────────────────────────────────────────────────────

@app.get('/')
def home():
    return {'message': 'Welcome to QuickBite Food Delivery'}


@app.get('/menu')
def get_full_menu():
    return {'menu': menu, 'total': len(menu)}


# ── Day 1 — Summary (must be above /menu/{item_id}) ───────────────

@app.get('/menu/summary')
def menu_summary():
    available   = [i for i in menu if i['is_available']]
    unavailable = [i for i in menu if not i['is_available']]
    categories  = list({i['category'] for i in menu})
    return {
        'total_items':       len(menu),
        'available_count':   len(available),
        'unavailable_count': len(unavailable),
        'categories':        categories,
    }


# ── Day 3 — Filter (fixed route, above /{item_id}) ────────────────

@app.get('/menu/filter')
def filter_menu(
    category:     str  = Query(None),
    max_price:    int  = Query(None),
    is_available: bool = Query(None),
):
    result = filter_menu_logic(category, max_price, is_available)
    return {'filtered_items': result, 'count': len(result)}


# ── Day 6 — Search ────────────────────────────────────────────────

@app.get('/menu/search')
def search_menu(
    keyword: str = Query(..., description='Keyword to search in name or category'),
):
    results = [
        i for i in menu
        if keyword.lower() in i['name'].lower()
        or keyword.lower() in i['category'].lower()
    ]
    if not results:
        return {
            'message':     f'No items found for: {keyword}',
            'total_found': 0,
            'results':     [],
        }
    return {
        'keyword':     keyword,
        'total_found': len(results),
        'results':     results,
    }


# ── Day 6 — Sort ──────────────────────────────────────────────────

@app.get('/menu/sort')
def sort_menu(
    sort_by: str = Query('price', description="'price', 'name', or 'category'"),
    order:   str = Query('asc',   description="'asc' or 'desc'"),
):
    if sort_by not in ['price', 'name', 'category']:
        return {'error': "sort_by must be 'price', 'name', or 'category'"}
    if order not in ['asc', 'desc']:
        return {'error': "order must be 'asc' or 'desc'"}

    reverse    = (order == 'desc')
    sorted_menu = sorted(menu, key=lambda i: i[sort_by], reverse=reverse)

    return {
        'sort_by': sort_by,
        'order':   order,
        'menu':    sorted_menu,
    }


# ── Day 6 — Pagination ────────────────────────────────────────────

@app.get('/menu/page')
def get_menu_paged(
    page:  int = Query(1, ge=1,  description='Page number'),
    limit: int = Query(3, ge=1, le=10, description='Items per page'),
):
    start = (page - 1) * limit
    paged = menu[start:start + limit]

    return {
        'page':        page,
        'limit':       limit,
        'total':       len(menu),
        'total_pages': math.ceil(len(menu) / limit),
        'items':       paged,
    }


# ── Day 6 — Browse (search + sort + paginate combined) ────────────

@app.get('/menu/browse')
def browse_menu(
    keyword: str = Query(None),
    sort_by: str = Query('price'),
    order:   str = Query('asc'),
    page:    int = Query(1, ge=1),
    limit:   int = Query(4, ge=1, le=20),
):
    # 1. Filter
    result = menu
    if keyword:
        result = [
            i for i in result
            if keyword.lower() in i['name'].lower()
            or keyword.lower() in i['category'].lower()
        ]

    # 2. Sort (validate first)
    if sort_by not in ['price', 'name', 'category']:
        return {'error': "sort_by must be 'price', 'name', or 'category'"}
    if order not in ['asc', 'desc']:
        return {'error': "order must be 'asc' or 'desc'"}

    result = sorted(result, key=lambda i: i[sort_by], reverse=(order == 'desc'))

    # 3. Paginate
    total       = len(result)
    total_pages = math.ceil(total / limit) if total else 1
    start       = (page - 1) * limit
    paged       = result[start:start + limit]

    return {
        'keyword':     keyword,
        'sort_by':     sort_by,
        'order':       order,
        'page':        page,
        'limit':       limit,
        'total':       total,
        'total_pages': total_pages,
        'items':       paged,
    }


# ── Day 4 — CRUD ──────────────────────────────────────────────────
# Variable route /{item_id} — always AFTER all fixed routes

@app.post('/menu')
def add_menu_item(new_item: NewMenuItem, response: Response):
    existing_names = [i['name'].lower() for i in menu]
    if new_item.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Menu item with this name already exists'}
    next_id = max(i['id'] for i in menu) + 1
    item = {
        'id':           next_id,
        'name':         new_item.name,
        'price':        new_item.price,
        'category':     new_item.category,
        'is_available': new_item.is_available,
    }
    menu.append(item)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Menu item added', 'item': item}


@app.put('/menu/{item_id}')
def update_menu_item(
    item_id:      int,
    response:     Response,
    price:        int  = Query(None),
    is_available: bool = Query(None),
):
    item = find_menu_item(item_id)
    if not item:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Menu item not found'}
    if price        is not None:
        item['price']        = price
    if is_available is not None:
        item['is_available'] = is_available
    return {'message': 'Menu item updated', 'item': item}


@app.delete('/menu/{item_id}')
def delete_menu_item(item_id: int, response: Response):
    item = find_menu_item(item_id)
    if not item:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Menu item not found'}
    menu.remove(item)
    return {'message': f"Menu item '{item['name']}' deleted"}


@app.get('/menu/{item_id}')
def get_menu_item(item_id: int):
    item = find_menu_item(item_id)
    if not item:
        return {'error': 'Item not found'}
    return {'item': item}


# ── Day 2 & 3 — Orders ────────────────────────────────────────────

@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
    item = find_menu_item(order_data.item_id)
    if not item:
        return {'error': 'Item not found'}
    if not item['is_available']:
        return {'error': f"'{item['name']}' is currently unavailable"}
    if order_data.order_type not in ['delivery', 'pickup']:
        return {'error': "order_type must be 'delivery' or 'pickup'"}

    total = calculate_bill(item['price'], order_data.quantity, order_data.order_type)
    order = {
        'order_id':         order_counter,
        'customer_name':    order_data.customer_name,
        'item':             item['name'],
        'quantity':         order_data.quantity,
        'delivery_address': order_data.delivery_address,
        'order_type':       order_data.order_type,
        'total_price':      total,
        'status':           'confirmed',
    }
    orders.append(order)
    order_counter += 1
    return {'message': 'Order placed successfully', 'order': order}


# ── Day 6 — Order Search & Sort (above variable route) ────────────

@app.get('/orders/search')
def search_orders(
    customer_name: str = Query(..., description='Customer name to search'),
):
    results = [
        o for o in orders
        if customer_name.lower() in o['customer_name'].lower()
    ]
    if not results:
        return {'message': f'No orders found for: {customer_name}', 'results': []}
    return {
        'customer_name': customer_name,
        'total_found':   len(results),
        'results':       results,
    }


@app.get('/orders/sort')
def sort_orders(
    order: str = Query('asc', description="'asc' or 'desc'"),
):
    if order not in ['asc', 'desc']:
        return {'error': "order must be 'asc' or 'desc'"}
    sorted_orders = sorted(orders, key=lambda o: o['total_price'], reverse=(order == 'desc'))
    return {
        'sort_by': 'total_price',
        'order':   order,
        'orders':  sorted_orders,
    }


@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}


# ── Day 5 — Cart ──────────────────────────────────────────────────
# Fixed routes /cart/add and /cart/checkout BEFORE variable /cart/{item_id}

@app.post('/cart/add')
def add_to_cart(
    item_id:  int = Query(...),
    quantity: int = Query(1),
):
    item = find_menu_item(item_id)
    if not item:
        return {'error': 'Item not found'}
    if not item['is_available']:
        return {'error': f"'{item['name']}' is currently unavailable"}

    for cart_item in cart:
        if cart_item['item_id'] == item_id:
            cart_item['quantity'] += quantity
            cart_item['subtotal']  = item['price'] * cart_item['quantity']
            return {'message': 'Cart updated', 'cart_item': cart_item}

    cart_item = {
        'item_id':   item_id,
        'item_name': item['name'],
        'quantity':  quantity,
        'unit_price': item['price'],
        'subtotal':  item['price'] * quantity,
    }
    cart.append(cart_item)
    return {'message': 'Added to cart', 'cart_item': cart_item}


@app.get('/cart')
def view_cart():
    if not cart:
        return {'message': 'Cart is empty', 'items': [], 'grand_total': 0}
    return {
        'items':       cart,
        'item_count':  len(cart),
        'grand_total': sum(i['subtotal'] for i in cart),
    }


@app.post('/cart/checkout')
def checkout(checkout_data: CheckoutRequest, response: Response):
    global order_counter
    if not cart:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Cart is empty'}

    placed_orders = []
    grand_total   = 0

    for cart_item in cart:
        order = {
            'order_id':         order_counter,
            'customer_name':    checkout_data.customer_name,
            'item':             cart_item['item_name'],
            'quantity':         cart_item['quantity'],
            'delivery_address': checkout_data.delivery_address,
            'order_type':       'delivery',
            'total_price':      cart_item['subtotal'] + 30,   # delivery charge
            'status':           'confirmed',
        }
        orders.append(order)
        placed_orders.append(order)
        grand_total   += order['total_price']
        order_counter += 1

    cart.clear()
    response.status_code = status.HTTP_201_CREATED
    return {
        'message':       'Checkout successful',
        'orders_placed': placed_orders,
        'grand_total':   grand_total,
    }


@app.delete('/cart/{item_id}')
def remove_from_cart(item_id: int, response: Response):
    for cart_item in cart:
        if cart_item['item_id'] == item_id:
            cart.remove(cart_item)
            return {'message': f"'{cart_item['item_name']}' removed from cart"}
    response.status_code = status.HTTP_404_NOT_FOUND
    return {'error': 'Item not in cart'}
