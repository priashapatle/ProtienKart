"""
ProteinKart Backend — Priasha Patle
REST API with SQLite, email confirmation via priashapatle@gmail.com
Run: uvicorn server:app --host 0.0.0.0 --port 8000
"""

import os
import sqlite3
import smtplib
import ssl
from contextlib import contextmanager
from typing import Optional
from email.message import EmailMessage
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG (Modified) ────────────────────────────────────────
# Default values hata di hain taaki GitHub par secrets leak na hon
DB_PATH = os.getenv("DB_PATH", os.path.join(os.getcwd(), "proteins.db"))
SMTP_HOST  = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT  = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER  = os.getenv("SMTP_USER") 
SMTP_PASS  = os.getenv("SMTP_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL")


# ── DATABASE ─────────────────────────────────────────────────
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Create tables and seed sample data if DB doesn't exist."""
    if os.path.exists(DB_PATH):
        return
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                name             TEXT NOT NULL,
                brand            TEXT NOT NULL,
                type             TEXT NOT NULL,
                flavour          TEXT,
                weight_kg        REAL,
                price            INTEGER NOT NULL,
                protein_per_serving REAL,
                servings         INTEGER,
                rating           REAL DEFAULT 4.0,
                rating_count     INTEGER DEFAULT 0,
                in_stock         INTEGER DEFAULT 1,
                veg              INTEGER DEFAULT 0,
                certified        INTEGER DEFAULT 0,
                image_url        TEXT
            );

            CREATE TABLE IF NOT EXISTS orders (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name  TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                product_id     INTEGER NOT NULL,
                quantity       INTEGER NOT NULL,
                total_price    INTEGER NOT NULL,
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            INSERT INTO products (name, brand, type, flavour, weight_kg, price, protein_per_serving, servings, rating, rating_count, in_stock, veg, certified, image_url) VALUES
            ('Whey Gold Standard', 'Optimum Nutrition', 'whey', 'Chocolate', 2.0, 4999, 24, 74, 4.8, 1200, 1, 0, 1, 'https://m.media-amazon.com/images/I/71IFoFp9jkL._SX679_.jpg'),
            ('Nitro Tech Whey', 'MuscleTech', 'whey', 'Vanilla', 1.8, 3999, 30, 40, 4.6, 890, 1, 0, 1, 'https://m.media-amazon.com/images/I/71k0DRxvRGL._SX679_.jpg'),
            ('Casein Protein', 'MuscleBlaze', 'casein', 'Cookies & Cream', 1.0, 2499, 26, 30, 4.3, 450, 1, 1, 0, 'https://m.media-amazon.com/images/I/61pNsUFHSQL._SX679_.jpg'),
            ('Plant Protein', 'Oziva', 'plant', 'Chocolate', 1.0, 1999, 20, 25, 4.5, 620, 1, 1, 1, 'https://m.media-amazon.com/images/I/71f9OHBVPZL._SX679_.jpg'),
            ('Mass Gainer XXL', 'MuscleBlaze', 'mass', 'Chocolate', 3.0, 2999, 32, 50, 4.2, 340, 1, 1, 0, 'https://m.media-amazon.com/images/I/71RJbvopUFL._SX679_.jpg'),
            ('Biozyme Whey', 'MuscleBlaze', 'whey', 'Cafe Mocha', 1.0, 1799, 25, 25, 4.7, 980, 1, 0, 1, 'https://m.media-amazon.com/images/I/71LRqGxpUQL._SX679_.jpg'),
            ('Serious Mass', 'Optimum Nutrition', 'mass', 'Banana', 2.7, 3499, 50, 16, 4.4, 560, 1, 0, 1, 'https://m.media-amazon.com/images/I/71+JGUqJgbL._SX679_.jpg'),
            ('Nakpro Perform Whey', 'Nakpro', 'whey', 'Mango', 1.0, 1299, 24, 30, 4.1, 210, 1, 1, 0, 'https://m.media-amazon.com/images/I/61j-BMDQHSL._SX679_.jpg');
        """)
    print(f"✅ Database created at {DB_PATH} with sample products.")


# ── EMAIL ────────────────────────────────────────────────────
def send_confirmation_email(order_id, customer_name, customer_email, product, quantity, total_price):
    """Send a beautiful HTML order confirmation email from priashapatle@gmail.com."""
    if not SMTP_USER or not SMTP_PASS:
        print("⚠️ SMTP credentials missing.")
        return False

    now           = datetime.now()
    order_date    = now.strftime("%b %d, %Y")
    arriving_date = (now + timedelta(days=3)).strftime("%A, %B %d")
    first_name    = customer_name.split()[0]

    msg = EmailMessage()
    msg['Subject'] = f"✅ Order Confirmed: #{order_id} | ProteinKart"
    msg['From']    = f"ProteinKart <{FROM_EMAIL}>"
    msg['To']      = customer_email
    msg.set_content(f"Hi {customer_name}, your order #{order_id} for {product['name']} has been confirmed. Total: ₹{total_price:,}")

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{ margin:0; padding:0; background:#F1F5F9; font-family:'Outfit',-apple-system,sans-serif; }}
  </style>
</head>
<body>
<table width="100%" cellspacing="0" cellpadding="0" style="background:#F1F5F9;padding:32px 16px;">
  <tr><td align="center">
    <table width="620" cellspacing="0" cellpadding="0" style="background:#fff;border-radius:20px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.07);border:1px solid #E2E8F0;">

      <!-- HEADER -->
      <tr><td style="background:linear-gradient(135deg,#0d2c24,#1a4d3a);padding:36px 48px;text-align:center;">
        <div style="font-size:10px;color:#d4af37;letter-spacing:6px;text-transform:uppercase;margin-bottom:10px;font-weight:600;">Premium Nutrition</div>
        <div style="font-size:28px;font-weight:800;color:#fff;letter-spacing:5px;text-transform:uppercase;">PROTEINKART</div>
        <div style="height:2px;width:48px;background:#d4af37;margin:14px auto 0;"></div>
      </td></tr>

      <!-- HERO -->
      <tr><td style="padding:40px 48px 0;text-align:center;">
        <div style="font-size:56px;margin-bottom:16px;">📦</div>
        <div style="font-size:13px;color:#4F46E5;font-weight:700;letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">Order Confirmed</div>
        <div style="font-size:30px;font-weight:800;color:#0F172A;margin-bottom:12px;">It's on its way, {first_name}! 💪</div>
        <div style="font-size:15px;color:#64748B;line-height:1.7;max-width:460px;margin:0 auto 32px;">
          Your ProteinKart order has been confirmed and is being packed. Get your shaker ready!
        </div>
      </td></tr>

      <!-- ARRIVAL CARD -->
      <tr><td style="padding:0 48px;">
        <div style="background:linear-gradient(135deg,#EEF2FF,#E0E7FF);border-radius:16px;padding:28px 32px;border:1px solid #C7D2FE;text-align:center;margin-bottom:28px;">
          <div style="font-size:11px;color:#4F46E5;text-transform:uppercase;font-weight:700;letter-spacing:3px;margin-bottom:6px;">Estimated Delivery</div>
          <div style="font-size:26px;font-weight:800;color:#3730A3;margin-bottom:8px;">{arriving_date}</div>
          <div style="font-size:13px;color:#6366F1;">Order ID: <strong>#{order_id}</strong></div>
        </div>
      </td></tr>

      <!-- TRACKING -->
      <tr><td style="padding:0 48px 32px;">
        <table width="100%" cellspacing="0" cellpadding="0"><tr>
          <td align="center" width="22%">
            <div style="width:44px;height:44px;border-radius:12px;background:#4F46E5;line-height:44px;color:#fff;font-size:18px;font-weight:700;text-align:center;">✓</div>
            <div style="font-size:10px;margin-top:7px;color:#1E293B;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Ordered</div>
            <div style="font-size:10px;color:#94A3B8;margin-top:2px;">{order_date}</div>
          </td>
          <td valign="top" style="padding-top:22px;"><div style="height:4px;background:#4F46E5;border-radius:2px;"></div></td>
          <td align="center" width="22%">
            <div style="width:44px;height:44px;border-radius:12px;background:#4F46E5;line-height:44px;color:#fff;font-size:18px;text-align:center;">✓</div>
            <div style="font-size:10px;margin-top:7px;color:#1E293B;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Packed</div>
            <div style="font-size:10px;color:#94A3B8;margin-top:2px;">Today</div>
          </td>
          <td valign="top" style="padding-top:22px;"><div style="height:4px;background:linear-gradient(to right,#4F46E5,#E2E8F0);border-radius:2px;"></div></td>
          <td align="center" width="22%">
            <div style="width:44px;height:44px;border-radius:12px;border:2.5px solid #6366F1;background:#EEF2FF;line-height:40px;color:#6366F1;font-size:20px;text-align:center;box-sizing:border-box;">🚚</div>
            <div style="font-size:10px;margin-top:7px;color:#6366F1;font-weight:700;text-transform:uppercase;letter-spacing:1px;">In Transit</div>
          </td>
          <td valign="top" style="padding-top:22px;"><div style="height:4px;background:#E2E8F0;border-radius:2px;"></div></td>
          <td align="center" width="22%">
            <div style="width:44px;height:44px;border-radius:12px;border:2px solid #E2E8F0;background:#F8FAFC;line-height:40px;color:#CBD5E1;font-size:20px;text-align:center;box-sizing:border-box;">🏠</div>
            <div style="font-size:10px;margin-top:7px;color:#94A3B8;font-weight:500;text-transform:uppercase;letter-spacing:1px;">Delivered</div>
          </td>
        </tr></table>
      </td></tr>

      <!-- ORDER SUMMARY -->
      <tr><td style="padding:0 48px 28px;">
        <div style="font-size:12px;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px;">Order Summary</div>
        <table width="100%" cellspacing="0" cellpadding="0" style="background:#F8FAFC;border-radius:14px;overflow:hidden;border:1px solid #E2E8F0;">
          <tr><td style="padding:20px 24px;border-bottom:1px solid #E2E8F0;">
            <table width="100%" cellspacing="0" cellpadding="0"><tr>
              <td>
                <img src="{product.get('image_url','')}" alt="{product['name']}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;margin-bottom:8px;" /><br>
                <div style="font-size:14px;font-weight:700;color:#0F172A;">{product['name']}</div>
                <div style="font-size:13px;color:#64748B;">Brand: {product['brand']} &nbsp;·&nbsp; Qty: {quantity}</div>
              </td>
              <td align="right"><div style="font-size:16px;font-weight:800;color:#0F172A;">₹{total_price:,}</div></td>
            </tr></table>
          </td></tr>
          <tr><td style="padding:14px 24px;border-bottom:1px solid #E2E8F0;">
            <table width="100%" cellspacing="0" cellpadding="0"><tr>
              <td style="font-size:13px;color:#64748B;">Shipping</td>
              <td align="right" style="font-size:13px;color:#16A34A;font-weight:600;">FREE</td>
            </tr></table>
          </td></tr>
          <tr><td style="padding:14px 24px;">
            <table width="100%" cellspacing="0" cellpadding="0"><tr>
              <td style="font-size:14px;font-weight:700;color:#0F172A;">Total Paid</td>
              <td align="right" style="font-size:18px;font-weight:800;color:#4F46E5;">₹{total_price:,}</td>
            </tr></table>
          </td></tr>
        </table>
      </td></tr>

      <!-- DETAILS GRID -->
      <tr><td style="padding:0 48px 28px;">
        <table width="100%" cellspacing="0" cellpadding="0"><tr>
          <td width="50%" style="padding-right:8px;">
            <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:16px 20px;">
              <div style="font-size:10px;color:#94A3B8;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;">Order ID</div>
              <div style="font-size:14px;font-weight:700;color:#0F172A;">#{order_id}</div>
              <div style="font-size:12px;color:#64748B;margin-top:2px;">{order_date}</div>
            </div>
          </td>
          <td width="50%" style="padding-left:8px;">
            <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:16px 20px;">
              <div style="font-size:10px;color:#94A3B8;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;">Status</div>
              <div style="font-size:13px;font-weight:700;color:#16A34A;">✓ Confirmed</div>
              <div style="font-size:12px;color:#64748B;margin-top:4px;">{customer_email}</div>
            </div>
          </td>
        </tr></table>
      </td></tr>

      <!-- PRO TIP -->
      <tr><td style="padding:0 48px 32px;">
        <div style="background:linear-gradient(135deg,#0d2c24,#1a4d3a);border-radius:16px;padding:24px 28px;">
          <div style="font-size:13px;font-weight:700;color:#d4af37;margin-bottom:10px;letter-spacing:1px;text-transform:uppercase;">💡 Pro Tip While You Wait</div>
          <div style="font-size:14px;color:#CBD5E1;line-height:1.7;">
            Take your whey within <strong style="color:#fff;">30 minutes post-workout</strong> for maximum muscle synthesis. Consistency &gt; Perfection. 🏋️
          </div>
        </div>
      </td></tr>

      <!-- SUPPORT -->
      <tr><td style="padding:0 48px 32px;text-align:center;">
        <div style="font-size:14px;color:#64748B;margin-bottom:12px;">Questions about your order?</div>
        <a href="mailto:priashapatle@gmail.com" style="display:inline-block;background:#0F172A;color:#fff;font-size:13px;font-weight:700;padding:12px 28px;border-radius:10px;text-decoration:none;">Contact Support</a>
      </td></tr>

      <!-- FOOTER -->
      <tr><td style="background:#F8FAFC;border-top:1px solid #E2E8F0;padding:24px 48px;text-align:center;">
        <div style="font-size:18px;margin-bottom:8px;">💪 &nbsp; 🥛 &nbsp; 🏋️</div>
        <div style="font-size:12px;color:#94A3B8;margin-bottom:4px;">© 2026 ProteinKart. All rights reserved.</div>
        <div style="font-size:12px;color:#CBD5E1;">This email was sent to {customer_email}</div>
      </td></tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""

    msg.add_alternative(html, subtype='html')

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"✅ Email sent to {customer_email} from {FROM_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False


# ── MODELS ───────────────────────────────────────────────────
class OrderRequest(BaseModel):
    product_id:     int
    quantity:       int
    customer_name:  str
    customer_email: EmailStr


# ── APP ──────────────────────────────────────────────────────
app = FastAPI(title="ProteinKart API — Priasha Patle", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def health_check():
    return {"status": "ok", "service": "ProteinKart Backend", "owner": "Priasha Patle"}

@app.get("/api/products")
def search_products(
    type:      Optional[str] = Query(None),
    brand:     Optional[str] = Query(None),
    max_price: Optional[int] = Query(None),
    q:         Optional[str] = Query(None),
):
    query  = "SELECT * FROM products WHERE 1=1"
    params = []
    if type:      query += " AND type = ?";              params.append(type)
    if brand:     query += " AND brand = ?";             params.append(brand)
    if max_price: query += " AND price <= ?";            params.append(max_price)
    if q:
        query += " AND (name LIKE ? OR brand LIKE ?)";   params.extend([f"%{q}%", f"%{q}%"])
    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]

@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)

@app.post("/api/orders")
def place_order(order: OrderRequest):
    with get_db() as conn:
        product = conn.execute("SELECT * FROM products WHERE id = ?", (order.product_id,)).fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if not product["in_stock"]:
            raise HTTPException(status_code=400, detail="Product is out of stock")

        total_price = product["price"] * order.quantity
        cursor = conn.execute(
            "INSERT INTO orders (customer_name, customer_email, product_id, quantity, total_price) VALUES (?,?,?,?,?)",
            (order.customer_name, order.customer_email, order.product_id, order.quantity, total_price),
        )
        conn.commit()
        order_id = cursor.lastrowid

    send_confirmation_email(order_id, order.customer_name, order.customer_email, dict(product), order.quantity, total_price)

    return {
        "order_id":       order_id,
        "product":        product["name"],
        "quantity":       order.quantity,
        "total_price":    total_price,
        "status":         "placed",
        "customer_email": order.customer_email,
        "message":        f"Order #{order_id} confirmed. Email sent to {order.customer_email}"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))