from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# アップロードフォルダの設定
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# SQLiteデータベースに接続
def get_db_connection():
    conn = sqlite3.connect('cafe_management.db')
    conn.row_factory = sqlite3.Row
    return conn

# 商品入力ページの表示と入力処理
@app.route('/product/new', methods=['GET', 'POST'])
def product_input():
    if request.method == 'POST':
        name = request.form['name']
        category_id = request.form['category_id']
        image_file = request.files['image_file']
        price = request.form['price']
        notes = request.form['notes']

        if not name or not category_id or not price:
            flash('商品名とカテゴリーID、価格は必須です！')
            return redirect(url_for('product_input'))

        # 画像ファイルの保存
        if image_file:
            filename = image_file.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_url = f'uploads/{filename}'
        else:
            image_url = None

        conn = get_db_connection()
        conn.execute('INSERT INTO PRODUCT (name, category_id, image_url,price, notes) VALUES (?, ?, ?, ?, ?)',
                     (name, category_id, image_url, price, notes))
        conn.commit()
        conn.close()
        flash('商品が正常に追加されました！')
        return redirect(url_for('product_input'))

    return render_template('product_input.html')

# 商品一覧ページの表示
@app.route('/product/list', methods=['GET'])
def product_list():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM PRODUCT').fetchall()
    conn.close()
    return render_template('product_list.html', products=products)

# 在庫の入出庫ページ
@app.route('/stock/movement', methods=['GET', 'POST'])

def stock_movement():
    conn = get_db_connection()
    products = conn.execute('SELECT id, name FROM PRODUCT').fetchall()  # 商品情報を取得
    staff = conn.execute('SELECT id, name FROM STAFF').fetchall()  # スタッフ情報を取得

    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        staff_id = request.form['staff_id']
        movement_type = request.form['movement_type']
        movement_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 現在の日時

        if not product_id or not quantity or not staff_id or not movement_type:
            flash('すべてのフィールドを入力してください！')
            return redirect(url_for('stock_movement'))

        conn.execute('INSERT INTO STOCK_MOVEMENT (product_id, quantity, movement_date, staff_id, movement_type) VALUES (?, ?, ?, ?, ?)',
                     (product_id, quantity, movement_date, staff_id, movement_type))
        conn.commit()
        conn.close()
        flash('在庫が正常に更新されました！')
        return redirect(url_for('stock_movement'))

    conn.close()
    return render_template('stock_movement.html', products=products, staff=staff)

# 入出庫履歴の表示
@app.route('/stock/movement/history')
def stock_movement_history():
    conn = get_db_connection()
    movements = conn.execute('''
        SELECT sm.id, p.name AS product_name, sm.quantity, sm.movement_date, s.name AS staff_name, sm.movement_type
        FROM STOCK_MOVEMENT sm
        JOIN PRODUCT p ON sm.product_id = p.id
        JOIN STAFF s ON sm.staff_id = s.id
        ORDER BY sm.movement_date DESC
    ''').fetchall()
    conn.close()
    return render_template('stock_movement_history.html', movements=movements)


if __name__ == '__main__':
    app.run(debug=True)
