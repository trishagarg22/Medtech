# Medtech — Intelligent Pharmacy & Inventory Dashboard

Medtech is a modern, responsive, and visually stunning web application designed to manage pharmacy inventories, healthcare equipment, customer profiles, and transaction billing. 

This project evolved from a command-line interface (CLI) database tool into a premium single-page web dashboard (SPA) served by a Flask backend and backed by a local MySQL database.

---

## 🌟 Key Features

### 1. Unified Analytics Dashboard
- Dynamic statistics cards showcasing **Total Medicines**, **Pharma Devices**, **Registered Customers**, and **Total Billing Revenue**.
- Real-time **Stock Warnings Panel** displaying immediate alerts for out-of-stock or low-stock items.
- Quick navigation shortcuts for administrative workflow.

### 2. Intelligent Medicine Inventory
- Live search filtering by medicine name, code, manufacturer, or category.
- Custom stock status filters (Low Stock, Out of Stock).
- **Expiry Tracker**: Dedicated lookup filter to check and highlight medicines expiring within the next 6 months.
- Complete CRUD interface (Create, Read, Update, Delete) in modal sheets.

### 3. Healthcare Devices Catalog
- Real-time stock counts and warranty duration details.
- Dual-bound price range filtering to track and filter machines.
- Device CRUD management with automated database updates.

### 4. Billing, Invoice & Customer Ledger
- Transaction-safe customer profile registering.
- **Dynamic Invoice Draft Constructor**: Add multiple medicines or devices into a single cart, update quantities with live stock limits validation, and compute totals dynamically.
- **Billing History**: Tabulated list of previous transactions.
- **Invoice Renderer**: Sleek, printable, and professional receipt sheets tailored via CSS printing overrides.

---

## 🛠️ Technology Stack

- **Backend**: Python, Flask (Web micro-framework)
- **Frontend**: Vanilla HTML5, Custom CSS3 Custom Variables (featuring a tailwind-inspired HSL color theme and Glassmorphism design), Vanilla JavaScript (ES6 Fetch APIs for modular SPA API operations)
- **Database**: MySQL (relational backend utilizing transaction commits and rollbacks)

---

## 📂 Project Structure

```
medtech/
│
├── app.py                # Main Flask server script (REST API & routing)
├── Medtech.py            # Initial Database builder & table seeder
├── Medtech main.py       # Legacy CLI version of the application
│
├── templates/
│   └── index.html        # Unified single-page HTML skeleton
│
└── static/
    ├── css/
    │   └── style.css     # Dark-mode glassmorphic theme styling
    └── js/
        └── app.js        # DOM interaction logic & API integration
```

---

## 🚀 Getting Started

### Prerequisites
Make sure you have **Python 3** and **MySQL Server** installed on your machine.

### Installation & Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/trishagarg22/Medtech.git
   cd Medtech
   ```

2. **Install Python dependencies**:
   ```bash
   pip install flask mysql-connector-python tabulate
   ```

3. **Configure the Database**:
   Ensure your MySQL server is running, then open `Medtech.py` and adjust the connection parameters if necessary:
   ```python
   # Medtech.py (lines 3)
   mycon=mysql.connect(host='localhost',user='root',passwd='YOUR_PASSWORD')
   ```
   Run the database setup script to create tables and seed mock data:
   ```bash
   python Medtech.py
   ```

4. **Launch the Application**:
   Open `app.py` and make sure the MySQL connection password matches your local password (default is `'2210'`):
   ```python
   # app.py (lines 12)
   passwd='YOUR_PASSWORD'
   ```
   Run the server:
   ```bash
   python app.py
   ```

5. **Access the Dashboard**:
   Open your browser and navigate to:
   👉 **[http://localhost:5000](http://localhost:5000)**

---

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.
