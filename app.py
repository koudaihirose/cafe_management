from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

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
        notes = request.form['notes']

        if not name or not category_id:
            flash('商品名とカテゴリーIDは必須です！')
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
        conn.execute('INSERT INTO PRODUCT (name, category_id, image_url, notes) VALUES (?, ?, ?, ?)',
                     (name, category_id, image_url, notes))
        conn.commit()
        conn.close()
        flash('商品が正常に追加されました！')
        return redirect(url_for('product_input'))

    return render_template('product_input.html')

if __name__ == '__main__':
    app.run(debug=True)
