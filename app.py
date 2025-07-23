from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_PATH = "anaj.db"

def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anaj (
            NO INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            ItemName TEXT,
            Weight REAL,
            BuyingPrice REAL,
            SellingPrice REAL
        )
    """)
    connection.commit()
    connection.close()

def add_hisab(item, weight, buyingprice, sellingprice):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO anaj (Date, ItemName, Weight, BuyingPrice, SellingPrice)
        VALUES (?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d"), item, weight, buyingprice, sellingprice))
    connection.commit()
    connection.close()

def get_hisab():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT NO , Date, ItemName, Weight, BuyingPrice, SellingPrice, (SellingPrice - BuyingPrice) AS Profit
        FROM anaj
        ORDER BY NO
    """)
    rows = cursor.fetchall()
    connection.close()
    return rows

def get_totals():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            SUM(Weight), 
            SUM(BuyingPrice), 
            SUM(SellingPrice),
            SUM(SellingPrice - BuyingPrice) AS TotalProfit
        FROM anaj
    """)
    totals = cursor.fetchone()
    connection.close()
    return totals  # (total_weight, total_buying, total_selling, total_profit)

def get_itemwise_totals():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT 
            ItemName,
            SUM(Weight),
            SUM(BuyingPrice),
            SUM(SellingPrice),
            SUM(SellingPrice - BuyingPrice) AS Profit
        FROM anaj
        GROUP BY ItemName
    """)
    results = cursor.fetchall()
    connection.close()
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        i = 0
        while True:
            prefix = f'items[{i}]'
            item = request.form.get(f'{prefix}[itemname]')
            if not item:
                break

            weight = request.form.get(f'{prefix}[weight]')
            buying_price = request.form.get(f'{prefix}[buyingprice]')
            selling_price = request.form.get(f'{prefix}[sellingprice]')

            if weight and buying_price and selling_price:
                add_hisab(item, float(weight), float(buying_price), float(selling_price))

            i += 1

        return redirect('/')

    Hisabs = get_hisab()
    totals = get_totals()
    itemwise_totals = get_itemwise_totals()
    return render_template('index.html', Hisabs=Hisabs, totals=totals, itemwise_totals=itemwise_totals)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
