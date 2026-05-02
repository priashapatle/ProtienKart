# 🥛 ProteinKart — Premium Supplements Store

> India's trusted online supplement store built with FastAPI backend and a vanilla HTML/CSS/JS frontend. Deployed on Vercel (frontend) and Google Cloud Run (backend).

🔗 **Live Site:** [https://protienkart.vercel.app/](https://protienkart.vercel.app/)

---

## 📸 Project Overview

ProteinKart is a full-stack e-commerce web app for buying protein supplements, peanut butter, mass gainers, BCAA, creatine, and more. It features a product catalog, cart system, order placement, email confirmation, and user authentication — all in one project.

---

## 🗂️ Project Structure

```
share/
├── index.html          # Main storefront (HTML + CSS + JS — single file)
├── login.html          # Login page
├── signup.html         # Signup / Register page
├── profile.html        # User profile page
├── api/
│   └── index.py        # FastAPI backend (all routes)
├── proteins.db         # SQLite database (local dev only)
├── requirements.txt    # Python dependencies
├── Dockerfile          # For Google Cloud Run deployment
├── vercel.json         # Vercel routing config
├── .env                # Environment variables (never commit this!)
└── images/             # Product images (now hosted on Cloudinary)
```

---

## ✨ Features

### 🛍️ Frontend (`index.html`)
- **Hero Slider** — 3 auto-sliding banners with smooth transitions
- **Category Navigation** — Filter by Whey, Isolate, Mass Gainer, BCAA, Creatine, Vegan, etc.
- **Product Grid** — 40+ products with ratings, discounts, weight variants, badges
- **Search** — Real-time search by product name, brand, or flavor
- **Wishlist** — Heart button on each product card
- **Cart Sidebar** — Add/remove items, quantity control, total calculation
- **Checkout Modal** — Name + email form, order summary, places order via API
- **Flash Sale Timer** — Live countdown timer
- **Combo Deals** — Bundle offer cards
- **Meal Plans** — Expert-curated high-protein meal plans
- **Flip Cards** — Expert advice cards with flip animation
- **Customer Reviews** — Testimonials section
- **Newsletter** — Email subscription via EmailJS
- **User Auth** — Register/Login using `localStorage`
- **Toast Notifications** — Smooth slide-up notifications
- **Responsive Design** — Mobile-first, works on all screen sizes

### ⚙️ Backend (`api/index.py`)
- Built with **FastAPI**
- **SQLite** database (local) — stores products and orders
- REST API endpoints:
  - `GET /api/products` — Fetch all products (with filters: type, brand, price, search)
  - `GET /api/products/{id}` — Fetch single product
  - `POST /api/orders` — Place an order
- **Email Confirmation** — Sends beautiful HTML email on order placement via Gmail SMTP
- **CORS** enabled for all origins

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python, FastAPI, Uvicorn |
| Database | SQLite (local), can migrate to PostgreSQL |
| Email | Gmail SMTP via `smtplib` |
| Newsletter | EmailJS |
| Images | Cloudinary CDN |
| Deployment (Frontend) | Vercel |
| Deployment (Backend) | Google Cloud Run |
| Containerization | Docker |

---

## ⚙️ Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/proteinkart.git
cd proteinkart
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the root:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FROM_EMAIL=your-email@gmail.com
DB_PATH=proteins.db
```

> **Note:** Use a Gmail App Password, not your actual Gmail password.  
> Generate one at: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

### 4. Run the backend
```bash
uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be live at: `http://localhost:8000`

### 5. Open the frontend
Just open `index.html` in your browser — no build step needed!

---

## 🌐 Deployment

### Frontend — Vercel
1. Push your code to GitHub
2. Import repo on [vercel.com](https://vercel.com)
3. Vercel auto-detects and deploys `index.html`
4. `vercel.json` handles API routing:
```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index" }
  ]
}
```

### Backend — Google Cloud Run
```bash
# Build Docker image
docker build -t proteinkart-backend .

# Deploy to Cloud Run
gcloud run deploy proteinkart-backend \
  --image proteinkart-backend \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

> ⚠️ **Important:** SQLite doesn't work on Cloud Run (ephemeral filesystem). Migrate to **PostgreSQL** (Neon/Supabase) for production.

---

## 🖼️ Image Hosting

All product and UI images are hosted on **Cloudinary** CDN.

Base URL format:
```
https://res.cloudinary.com/dhiumfzgn/image/upload/<filename>
```

To add new images:
1. Go to [Cloudinary Media Library](https://cloudinary.com)
2. Upload with preset `proteinkart` (Unique suffix: OFF, Use filename as Public ID: ON)
3. Use the URL directly in `index.html`

---

## 📦 API Reference

### Get All Products
```
GET /api/products
```
Query params: `type`, `brand`, `max_price`, `q` (search)

### Get Single Product
```
GET /api/products/{product_id}
```

### Place Order
```
POST /api/orders
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2,
  "customer_name": "Rahul Sharma",
  "customer_email": "rahul@email.com"
}
```

Response:
```json
{
  "order_id": 42,
  "product": "Gold Standard 100% Whey",
  "quantity": 2,
  "total_price": 4998,
  "status": "placed",
  "message": "Order #42 confirmed. Email sent to rahul@email.com"
}
```

---

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `SMTP_HOST` | Gmail SMTP host (`smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port (`465` for SSL) |
| `SMTP_USER` | Gmail address used to send emails |
| `SMTP_PASS` | Gmail App Password |
| `FROM_EMAIL` | Sender email shown to customer |
| `DB_PATH` | Path to SQLite database file |

> **Never commit `.env` to GitHub!** Add it to `.gitignore`

---

## 📋 Pages

| Page | Description |
|------|-------------|
| `index.html` | Main store — products, cart, checkout |
| `login.html` | Login with email & password |
| `signup.html` | New user registration |
| `profile.html` | View logged-in user profile |

---

## 🛣️ Roadmap

- [ ] Migrate SQLite → PostgreSQL (Neon) for production
- [ ] Add payment gateway (Razorpay)
- [ ] Product detail pages
- [ ] Order history page
- [ ] Admin dashboard
- [ ] Coupon/promo code system
- [ ] PWA support (offline mode)

---

## 👩‍💻 Author

**Priasha Patle**  
📧 priashapatle@gmail.com

---

## 📄 License

This project is for educational purposes. All product names and brand logos belong to their respective owners.
