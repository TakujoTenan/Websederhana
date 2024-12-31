from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Simpan data produk dan transaksi
products = []
transactions = []
logs = []

def add_log(action, product_name, category, details):
    logs.append ({
        "action": action,
        "product_name": product_name,
        "category": category,
        "details": details,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/products', methods=['GET', 'POST'])
def product_list():
    if request.method == 'POST':
        action = request.form.get('action')
        product_id = request.form.get('product_id')
        if action == 'add':
            new_product = {
                'id': len(products) + 1,
                'name': request.form['name'],
                'category': request.form['category'],
                'stock': int(request.form['stock']),
                'price': float(request.form['price']),
            }
            products.append(new_product)
            add_log("Ditambahkan", new_product['name'], new_product['category'], "Menambahkan produk baru.")
            flash('Product added successfully!', 'success')
        elif action == 'delete':
            product = next((p for p in products if p['id'] == int(product_id)), None)
            if product:
                products.remove(product)
                add_log("Dihapus", product["name"], product["category"], "menghapus produk.")
                flash('Product deleted successfully!', 'success')
        elif action == 'update':
            product = next((p for p in products if p['id'] == int(product_id)), None)
            if product:
                product['name'] = request.form['name']
                product['category'] = request.form['category']
                product['stock'] = int(request.form['stock'])
                product['price'] = float(request.form['price'])
                add_log("Updated", product["name"], product["category"], "Memperbarui produk.")
                flash('Product updated successfully!', 'success')
        return redirect(url_for('product_list'))
    return render_template('products.html', products=products)

@app.route('/transactions', methods=['GET', 'POST'])
def transactions_page():
    global transactions  # Pastikan menggunakan variabel yang benar
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])

        # Cari produk berdasarkan ID
        product = next((p for p in products if p['id'] == product_id), None)

        if product and quantity <= product['stock']:
            total_price = quantity * product['price']
            product['stock'] -= quantity  # Kurangi stok produk

            # Buat transaksi baru
            transaction = {
                "id": len(transactions) + 1,
                "product_name": product['name'],
                "category": product['category'],
                "quantity": quantity,
                "total_price": total_price,
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            transactions.append(transaction)  # Tambahkan ke daftar transaksi
            add_log("Transaksi", product["name"], product["category"], f"Sold {quantity} unit(s).")
            flash("Transaction completed successfully!", "success")
        else:
            flash("Insufficient stock or invalid product!", "danger")

        return redirect('/transactions')

    return render_template('transactions.html', products=products, transactions=transactions)

@app.route('/logs')
def logs_page():
    return render_template('logs.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
