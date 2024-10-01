from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

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

# ログイン状態を確認するデコレーター
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'staff_id' not in session:
            flash('ログインが必要です。')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# トップページ（ログインフォームを配置）
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        # データベース接続
        conn = get_db_connection()
        staff = conn.execute('SELECT * FROM staff WHERE name = ?', (name,)).fetchone()
        conn.close()

        # スタッフが存在し、パスワードが一致するか確認
        if staff and check_password_hash(staff['password'], password):
            session['staff_id'] = staff['id']
            session['staff_name'] = staff['name']
            session['staff_role'] = staff['role']
            flash('ログイン成功しました！')
            return redirect(url_for('dashboard'))
        else:
            flash('名前またはパスワードが正しくありません。')

    return render_template('index.html')

# ダッシュボードページ
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', staff_name=session['staff_name'], staff_role=session['staff_role'])

# 商品入力ページの表示と入力処理
@app.route('/product/new', methods=['GET', 'POST'])
@login_required
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
@login_required
def product_list():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM PRODUCT WHERE is_deleted = 0').fetchall()
    conn.close()
    return render_template('product_list.html', products=products)

# 商品編集ページの表示と編集処理
@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def product_edit(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM PRODUCT WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        category_id = request.form['category_id']
        price = request.form['price']
        notes = request.form['notes']
        image_file = request.files['image_file']

        if not name or not category_id or not price:
            flash('商品名とカテゴリーID、価格は必須です！')
            return redirect(url_for('product_edit', id=id))

        # 画像の更新処理
        if image_file:
            filename = image_file.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_url = f'uploads/{filename}'
        else:
            image_url = product['image_url']

        conn.execute('UPDATE PRODUCT SET name = ?, category_id = ?, price = ?, image_url = ?, notes = ? WHERE id = ?',
                     (name, category_id, price, image_url, notes, id))
        conn.commit()
        conn.close()
        flash('商品が正常に更新されました！')
        return redirect(url_for('product_list'))

    conn.close()
    return render_template('product_edit.html', product=product)

# 商品の削除
@app.route('/product/delete/<int:id>', methods=['POST'])
@login_required
def product_delete(id):
    conn = get_db_connection()
    conn.execute('UPDATE PRODUCT SET is_deleted = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('商品が削除されました！（論理削除）')
    return redirect(url_for('product_list'))

# 削除された商品の復元
@app.route('/product/restore/<int:id>', methods=['POST'])
@login_required
def product_restore(id):
    conn = get_db_connection()
    conn.execute('UPDATE PRODUCT SET is_deleted = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('商品が復元されました！')
    return redirect(url_for('product_list'))

# 在庫の入出庫ページ
@app.route('/stock/movement', methods=['GET', 'POST'])
@login_required
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

# 入出庫履歴の編集
@app.route('/stock/movement/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def stock_movement_edit(id):
    conn = get_db_connection()
    movement = conn.execute('SELECT * FROM STOCK_MOVEMENT WHERE id = ?', (id,)).fetchone()
    products = conn.execute('SELECT id, name FROM PRODUCT').fetchall()
    staff = conn.execute('SELECT id, name FROM STAFF').fetchall()

    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        staff_id = request.form['staff_id']
        movement_type = request.form['movement_type']
        movement_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn.execute('UPDATE STOCK_MOVEMENT SET product_id = ?, quantity = ?, movement_date = ?, staff_id = ?, movement_type = ? WHERE id = ?',
                     (product_id, quantity, movement_date, staff_id, movement_type, id))
        conn.commit()
        conn.close()
        flash('入出庫履歴が正常に更新されました！')
        return redirect(url_for('stock_movement_history'))

    conn.close()
    return render_template('stock_movement_edit.html', movement=movement, products=products, staff=staff)

# 入出庫履歴の削除
@app.route('/stock/movement/delete/<int:id>', methods=['POST'])
@login_required
def stock_movement_delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM STOCK_MOVEMENT WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('入出庫履歴が削除されました！')
    return redirect(url_for('stock_movement_history'))

# 入出庫履歴の表示
@app.route('/stock/movement/history')
@login_required
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

# スタッフ登録ページの表示と登録処理
@app.route('/staff/register', methods=['GET', 'POST'])
@login_required
def staff_register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']
        
        # 必須項目のチェック
        if not name or not password or not role:
            flash('すべてのフィールドを入力してください。')
            return redirect(url_for('staff_register'))
        
        # パスワードのハッシュ化（必ずこれを使って保存）
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        # データベースにスタッフ情報を保存
        conn = get_db_connection()
        conn.execute('INSERT INTO staff (name, password, role) VALUES (?, ?, ?)',
                     (name, hashed_password, role))
        conn.commit()
        conn.close()
        flash('スタッフが正常に登録されました！')
        return redirect(url_for('staff_register'))

    return render_template('staff_register.html')

@app.route('/logout')
def logout():
    # セッションをクリアしてログアウト
    session.clear()
    flash('ログアウトしました。')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False)
