from flask import Flask, request, jsonify, render_template
import mysql.connector as mysql
from datetime import datetime, date

app = Flask(__name__)

# Helper function to get DB connection
def get_db_connection():
    return mysql.connect(
        host='localhost',
        user='root',
        passwd='2210',
        database='medtech'
    )

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_credentials (
                username VARCHAR(50) PRIMARY KEY,
                password VARCHAR(255) NOT NULL,
                owner_key VARCHAR(255) NOT NULL
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM admin_credentials")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO admin_credentials (username, password, owner_key)
                VALUES ('admin', 'admin123', 'owner123')
            """)
            conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database initialization failed: {e}")
        if conn:
            conn.close()

init_db()

# Serve the frontend home page
@app.route('/')
def index():
    return render_template('index.html')

# API: Dashboard Stats
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total medicines count
        cursor.execute("SELECT COUNT(*) as count FROM med_list")
        med_count = cursor.fetchone()['count']
        
        # Total devices count
        cursor.execute("SELECT COUNT(*) as count FROM pharma_devices")
        dev_count = cursor.fetchone()['count']
        
        # Total customers count
        cursor.execute("SELECT COUNT(*) as count FROM Customer")
        cust_count = cursor.fetchone()['count']
        
        # Total revenue
        cursor.execute("SELECT SUM(total) as revenue FROM Bill")
        revenue_row = cursor.fetchone()
        revenue = revenue_row['revenue'] if revenue_row['revenue'] is not None else 0.0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "medicines": med_count,
            "devices": dev_count,
            "customers": cust_count,
            "revenue": round(revenue, 2)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# API: Medicines CRUD
@app.route('/api/medicines', methods=['GET'])
def get_medicines():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM med_list")
        rows = cursor.fetchall()
        
        # Convert date objects to string for JSON serialization
        for r in rows:
            if isinstance(r['expire_date'], (date, datetime)):
                r['expire_date'] = r['expire_date'].strftime('%Y-%m-%d')
                
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/medicines', methods=['POST'])
def add_medicine():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """INSERT INTO med_list 
                   (med_code, med_name, manufacturer, dosage_form, category, expire_date, price, medstock) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        params = (
            data.get('med_code'),
            data.get('med_name'),
            data.get('manufacturer'),
            data.get('dosage_form'),
            data.get('category'),
            data.get('expire_date'),
            float(data.get('price', 0)),
            int(data.get('medstock', 0))
        )
        
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Medicine added successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/medicines/<code_val>', methods=['PUT'])
def update_medicine(code_val):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic update statement based on fields provided
        fields = []
        params = []
        
        mapping = {
            'med_name': 'med_name = %s',
            'manufacturer': 'manufacturer = %s',
            'dosage_form': 'dosage_form = %s',
            'category': 'category = %s',
            'expire_date': 'expire_date = %s',
            'price': 'price = %s',
            'medstock': 'medstock = %s'
        }
        
        for key, clause in mapping.items():
            if key in data:
                val = data[key]
                if key == 'price':
                    val = float(val)
                elif key == 'medstock':
                    val = int(val)
                fields.append(clause)
                params.append(val)
                
        if not fields:
            return jsonify({"success": False, "error": "No fields to update"}), 400
            
        query = f"UPDATE med_list SET {', '.join(fields)} WHERE med_code = %s"
        params.append(code_val)
        
        cursor.execute(query, tuple(params))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Medicine updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/medicines/<code_val>', methods=['DELETE'])
def delete_medicine(code_val):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM med_list WHERE med_code = %s", (code_val,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Medicine deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# API: Healthcare Devices CRUD
@app.route('/api/devices', methods=['GET'])
def get_devices():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pharma_devices")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": rows})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/devices', methods=['POST'])
def add_device():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """INSERT INTO pharma_devices 
                   (machine_id, name, Warranty, manufacturer, useins, price, stock) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        params = (
            data.get('machine_id'),
            data.get('name'),
            data.get('Warranty'),
            data.get('manufacturer'),
            data.get('useins'),
            float(data.get('price', 0)),
            int(data.get('stock', 0))
        )
        
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Device added successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/devices/<machine_id>', methods=['PUT'])
def update_device(machine_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        fields = []
        params = []
        
        mapping = {
            'name': 'name = %s',
            'Warranty': 'Warranty = %s',
            'manufacturer': 'manufacturer = %s',
            'useins': 'useins = %s',
            'price': 'price = %s',
            'stock': 'stock = %s'
        }
        
        for key, clause in mapping.items():
            if key in data:
                val = data[key]
                if key == 'price':
                    val = float(val)
                elif key == 'stock':
                    val = int(val)
                fields.append(clause)
                params.append(val)
                
        if not fields:
            return jsonify({"success": False, "error": "No fields to update"}), 400
            
        query = f"UPDATE pharma_devices SET {', '.join(fields)} WHERE machine_id = %s"
        params.append(machine_id)
        
        cursor.execute(query, tuple(params))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Device updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/devices/<machine_id>', methods=['DELETE'])
def delete_device(machine_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pharma_devices WHERE machine_id = %s", (machine_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Device deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# API: Customer and Bills
@app.route('/api/bills', methods=['GET'])
def get_bills():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Fetch high-level bill items including contact number
        query = """
            SELECT b.bill_id, c.cust_id, c.cust_name, c.contact, SUM(b.total) as total_amount, b.dt_purchase, b.payment_mode
            FROM Bill b
            JOIN Customer c ON b.cust_id = c.cust_id
            GROUP BY b.bill_id, c.cust_id, c.cust_name, c.contact, b.dt_purchase, b.payment_mode
            ORDER BY b.dt_purchase DESC, b.bill_id DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for r in rows:
            if isinstance(r['dt_purchase'], (date, datetime)):
                r['dt_purchase'] = r['dt_purchase'].strftime('%Y-%m-%d')
            r['contact'] = (r['contact'] or '').strip()

        # Group bills by mobile number (contact)
        # Bills of people having the same mobile number are shown together,
        # with the recent one above and old ones below.
        groups = {}
        for r in rows:
            contact_key = r['contact']
            if not contact_key:
                contact_key = f"__NO_CONTACT_{r['bill_id']}__"
            if contact_key not in groups:
                groups[contact_key] = []
            groups[contact_key].append(r)
            
        # Within each group, sort bills by dt_purchase DESC, bill_id DESC (recent above, old below)
        for key in groups:
            groups[key].sort(key=lambda x: (str(x['dt_purchase']), str(x['bill_id'])), reverse=True)
            
        # Sort groups by the date of their most recent bill (descending)
        sorted_group_keys = sorted(
            groups.keys(),
            key=lambda k: (str(groups[k][0]['dt_purchase']), str(groups[k][0]['bill_id'])),
            reverse=True
        )
        
        ordered_bills = []
        for k in sorted_group_keys:
            ordered_bills.extend(groups[k])
            
        return jsonify({"success": True, "data": ordered_bills})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/bills/<bill_id>', methods=['GET'])
def get_bill_detail(bill_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT c.cust_name, c.address, c.contact, 
                   b.bill_id, b.dt_purchase, b.item_name, b.quantity, b.price, b.total, b.payment_mode
            FROM Bill b
            JOIN Customer c ON b.cust_id = c.cust_id
            WHERE b.bill_id = %s
        """
        cursor.execute(query, (bill_id,))
        rows = cursor.fetchall()
        
        if not rows:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "Bill not found"}), 404
            
        bill_info = {
            "bill_id": rows[0]["bill_id"],
            "cust_name": rows[0]["cust_name"],
            "address": rows[0]["address"],
            "contact": (rows[0]["contact"] or '').strip(),
            "payment_mode": rows[0]["payment_mode"],
            "dt_purchase": rows[0]["dt_purchase"].strftime('%Y-%m-%d') if isinstance(rows[0]["dt_purchase"], (date, datetime)) else rows[0]["dt_purchase"],
            "items": [],
            "returned_items": [],
            "total_amount": 0.0
        }
        
        for r in rows:
            qty = r["quantity"]
            tot = float(r["total"])
            if qty < 0 or tot < 0:
                bill_info["returned_items"].append({
                    "item_name": r["item_name"],
                    "quantity": abs(qty),
                    "price": float(r["price"]),
                    "total": abs(tot)
                })
            else:
                bill_info["items"].append({
                    "item_name": r["item_name"],
                    "quantity": qty,
                    "price": float(r["price"]),
                    "total": tot
                })
            bill_info["total_amount"] += tot
            
        bill_info["total_amount"] = round(bill_info["total_amount"], 2)
        
        # Fetch all related bills for the same contact number (recent above, old below)
        related_bills = []
        if bill_info["contact"]:
            rel_query = """
                SELECT b.bill_id, c.cust_name, SUM(b.total) as total_amount, b.dt_purchase, b.payment_mode
                FROM Bill b
                JOIN Customer c ON b.cust_id = c.cust_id
                WHERE c.contact = %s
                GROUP BY b.bill_id, c.cust_name, b.dt_purchase, b.payment_mode
                ORDER BY b.dt_purchase DESC, b.bill_id DESC
            """
            cursor.execute(rel_query, (bill_info["contact"],))
            rel_rows = cursor.fetchall()
            for r in rel_rows:
                related_bills.append({
                    "bill_id": r["bill_id"],
                    "cust_name": r["cust_name"],
                    "payment_mode": r["payment_mode"],
                    "dt_purchase": r["dt_purchase"].strftime('%Y-%m-%d') if isinstance(r["dt_purchase"], (date, datetime)) else r["dt_purchase"],
                    "total_amount": round(float(r["total_amount"]), 2)
                })
        bill_info["related_bills"] = related_bills

        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": bill_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/bills', methods=['POST'])
def create_bill():
    conn = None
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start transaction
        conn.start_transaction()
        
        # 1. Handle Customer
        cust_id = data.get('cust_id')
        cust_name = data.get('cust_name')
        contact = data.get('contact')
        address = data.get('address')
        
        # Check if customer already exists
        cursor.execute("SELECT cust_id FROM Customer WHERE cust_id = %s", (cust_id,))
        cust_exists = cursor.fetchone()
        
        if not cust_exists:
            cursor.execute(
                "INSERT INTO Customer (cust_id, cust_name, contact, address) VALUES (%s, %s, %s, %s)",
                (cust_id, cust_name, contact, address)
            )
            
        # 2. Insert Bill items (Purchased)
        bill_id = data.get('bill_id')
        dt_purchase = data.get('dt_purchase') or datetime.now().strftime('%Y-%m-%d')
        payment_mode = data.get('payment_mode', 'Cash')
        items = data.get('items', [])
        returned_items = data.get('returned_items', [])
        
        for item in items:
            name = item.get('item_name')
            qty = int(item.get('quantity', 1))
            price = float(item.get('price', 0))
            total = qty * price
            key = item.get('key', '')
            
            # Check and update stock
            if key.startswith('med:'):
                med_code = key.split(':', 1)[1]
                cursor.execute("SELECT medstock, med_name FROM med_list WHERE med_code = %s", (med_code,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Medicine code {med_code} not found in database.")
                current_stock = row[0]
                if current_stock < qty:
                    raise ValueError(f"Insufficient stock for medicine '{row[1]}'. Available: {current_stock}, Requested: {qty}")
                cursor.execute("UPDATE med_list SET medstock = medstock - %s WHERE med_code = %s", (qty, med_code))
                
            elif key.startswith('dev:'):
                machine_id = key.split(':', 1)[1]
                cursor.execute("SELECT stock, name FROM pharma_devices WHERE machine_id = %s", (machine_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Device ID {machine_id} not found in database.")
                current_stock = row[0]
                if current_stock < qty:
                    raise ValueError(f"Insufficient stock for device '{row[1]}'. Available: {current_stock}, Requested: {qty}")
                cursor.execute("UPDATE pharma_devices SET stock = stock - %s WHERE machine_id = %s", (qty, machine_id))
            
            cursor.execute(
                """INSERT INTO Bill 
                   (bill_id, cust_id, item_name, quantity, price, total, dt_purchase, payment_mode) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (bill_id, cust_id, name, qty, price, total, dt_purchase, payment_mode)
            )

        # 3. Insert Returned items (Old medicines returned by customer)
        for ret_item in returned_items:
            name = ret_item.get('item_name', '')
            qty = int(ret_item.get('quantity', 1))
            price = float(ret_item.get('price', 0))
            total = - (qty * price)  # Negative total to subtract from total bill
            key = ret_item.get('key', '')
            
            # Add stock back to inventory
            if key.startswith('med:'):
                med_code = key.split(':', 1)[1]
                cursor.execute("UPDATE med_list SET medstock = medstock + %s WHERE med_code = %s", (qty, med_code))
            elif key.startswith('dev:'):
                machine_id = key.split(':', 1)[1]
                cursor.execute("UPDATE pharma_devices SET stock = stock + %s WHERE machine_id = %s", (qty, machine_id))
            else:
                # Try finding by name in medicines or devices
                cursor.execute("SELECT med_code FROM med_list WHERE med_name = %s", (name,))
                m_row = cursor.fetchone()
                if m_row:
                    cursor.execute("UPDATE med_list SET medstock = medstock + %s WHERE med_code = %s", (qty, m_row[0]))
                else:
                    cursor.execute("SELECT machine_id FROM pharma_devices WHERE name = %s", (name,))
                    d_row = cursor.fetchone()
                    if d_row:
                        cursor.execute("UPDATE pharma_devices SET stock = stock + %s WHERE machine_id = %s", (qty, d_row[0]))
            
            displayName = name if "(Returned)" in name else f"{name} (Returned)"
            cursor.execute(
                """INSERT INTO Bill 
                   (bill_id, cust_id, item_name, quantity, price, total, dt_purchase, payment_mode) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (bill_id, cust_id, displayName, -qty, price, total, dt_purchase, payment_mode)
            )
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Bill recorded successfully!"})
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/bills/<bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start transaction
        conn.start_transaction()
        
        # 1. Fetch all items in this bill to restore stock
        cursor.execute("SELECT item_name, quantity FROM Bill WHERE bill_id = %s", (bill_id,))
        items = cursor.fetchall()
        
        if not items:
            return jsonify({"success": False, "error": f"No bill found with ID {bill_id}."}), 404
            
        for item_name, qty in items:
            # Check if this item is a medicine
            cursor.execute("SELECT med_code FROM med_list WHERE med_name = %s", (item_name,))
            med_row = cursor.fetchone()
            if med_row:
                med_code = med_row[0]
                cursor.execute("UPDATE med_list SET medstock = medstock + %s WHERE med_code = %s", (qty, med_code))
                continue
                
            # Check if this item is a device
            cursor.execute("SELECT machine_id FROM pharma_devices WHERE name = %s", (item_name,))
            dev_row = cursor.fetchone()
            if dev_row:
                machine_id = dev_row[0]
                cursor.execute("UPDATE pharma_devices SET stock = stock + %s WHERE machine_id = %s", (qty, machine_id))
                
        # 2. Delete the bill entries
        cursor.execute("DELETE FROM Bill WHERE bill_id = %s", (bill_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": f"Bill {bill_id} successfully voided, and stock has been restored."})
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password FROM admin_credentials WHERE username = %s", (username,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row and row['password'] == password:
            return jsonify({"success": True, "message": "Login successful!"})
        else:
            return jsonify({"success": False, "error": "Invalid username or password."}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/change-password', methods=['POST'])
def change_password():
    try:
        data = request.json
        owner_key = data.get('owner_key')
        new_password = data.get('new_password')
        
        if not owner_key or not new_password:
            return jsonify({"success": False, "error": "Missing required fields."}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Verify owner key
        cursor.execute("SELECT owner_key FROM admin_credentials WHERE username = 'admin'")
        row = cursor.fetchone()
        
        if not row or row['owner_key'] != owner_key:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "Invalid Owner Secret Key."}), 403
            
        # 2. Update administrator password
        cursor.execute("UPDATE admin_credentials SET password = %s WHERE username = 'admin'", (new_password,))
        conn.commit()
        
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Administrator password updated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/bills/<bill_id>/return', methods=['POST'])
def return_item(bill_id):
    conn = None
    try:
        data = request.json
        item_name = data.get('item_name')
        return_qty = int(data.get('return_qty', 0))
        
        if not item_name or return_qty <= 0:
            return jsonify({"success": False, "error": "Invalid item name or return quantity."}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()
        
        # 1. Fetch current transaction record details
        cursor.execute(
            "SELECT quantity, price, total FROM Bill WHERE bill_id = %s AND item_name = %s",
            (bill_id, item_name)
        )
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": f"Item '{item_name}' not found in bill '{bill_id}'."}), 404
            
        current_qty = int(row['quantity'])
        price = float(row['price'])
        
        if return_qty > current_qty:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": f"Cannot return {return_qty} units. Only {current_qty} units were purchased."}), 400
            
        # 2. Update stock in inventory (Medicine or Device)
        # Search in Medicines first
        cursor.execute("SELECT med_code FROM med_list WHERE med_name = %s", (item_name,))
        med_row = cursor.fetchone()
        if med_row:
            med_code = med_row['med_code']
            cursor.execute("UPDATE med_list SET medstock = medstock + %s WHERE med_code = %s", (return_qty, med_code))
        else:
            # Search in Devices
            cursor.execute("SELECT machine_id FROM pharma_devices WHERE name = %s", (item_name,))
            dev_row = cursor.fetchone()
            if dev_row:
                machine_id = dev_row['machine_id']
                cursor.execute("UPDATE pharma_devices SET stock = stock + %s WHERE machine_id = %s", (return_qty, machine_id))
        
        # 3. Update the Bill details: quantity and total
        new_qty = current_qty - return_qty
        new_total = new_qty * price
        
        cursor.execute(
            "UPDATE Bill SET quantity = %s, total = %s WHERE bill_id = %s AND item_name = %s",
            (new_qty, new_total, bill_id, item_name)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": f"Successfully returned {return_qty} units of '{item_name}'. Grand total has been updated and stock restored."})
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
