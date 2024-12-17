import shutil
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import subprocess

from Database import Database

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

host = "localhost"
port = "5432"
database = "car_dealership"
user = "postgres"
password = "admin"
db = Database(host, port, database, user, password)
db.connect()

PROCESSED_IMAGES_DIR = 'static/processed_images'


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    login = request.form['login']
    password = request.form['password']

    user = db.authenticate_user(login, password)

    if not user:
        flash('Login successful!', 'success')
        return redirect(url_for('home'))
    else:
        flash('Invalid login or password', 'danger')
        return render_template('index.html')


@app.route('/upload_page')
def upload_page():
    return render_template('upload_page.html')


@app.route('/view')
def view():
    tables = db.get_tables()
    table_data = {}

    for table in tables:
        table_data[table] = db.get_table_data(table)

    return render_template('viewDataBase.html', table_data=table_data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['fullName']
        phone = request.form['phone']
        login = request.form['login']
        password = request.form['password']
        date_birth = request.form['dateBirth']
        region_id = request.form['regionId']
        date_registration = datetime.now().date()  # Assuming you want to set the current date

        # Store the user data in the session
        session['user_data'] = {
            'full_name': full_name,
            'phone': phone,
            'login': login,
            'password': password,
            'date_registration': date_registration,
            'date_birth': date_birth,
            'region_id': region_id
        }

        return redirect(url_for('select_user_type'))

    regions = db.get_table_form("region")
    return render_template('register.html', regions=regions)


@app.route('/select_user_type', methods=['GET', 'POST'])
def select_user_type():
    if request.method == 'POST':
        user_type = request.form['userType']
        return redirect(url_for('register_client' if user_type == 'client' else 'register_admin'))

    return render_template('select_user_type.html')


@app.route('/register_client', methods=['GET', 'POST'])
def register_client():
    if request.method == 'POST':
        coefficient = request.form['coefficient']
        user_data = session.get('user_data')

        db.add_client(
            user_data['full_name'],
            user_data['phone'],
            user_data['login'],
            user_data['password'],
            user_data['date_registration'],
            user_data['date_birth'],
            user_data['region_id'],
            coefficient
        )
        return redirect(url_for('view'))

    return render_template('register_client.html')

@app.route('/register-admin', methods=['GET', 'POST'])
def register_seller():
    if request.method == 'POST':
        position_id = request.form['position_id']
        shop_id = request.form['shop_id']
        user_data = session.get('user_data')

        db.add_seller(
            user_data['full_name'],
            user_data['phone'],
            user_data['login'],
            user_data['password'],
            user_data['date_registration'],
            user_data['date_birth'],
            user_data['region_id'],
            position_id,
            shop_id
        )
        return redirect(url_for('view'))

    positions = db.get_table_form("Positions")
    shops = db.get_table_form("ShopCars")
    return render_template('register_admin.html', positions=positions, shops=shops)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(request.url)

    file = request.files['image']
    if file.filename == '':
        return redirect(request.url)

    input_image_path = os.path.join('static', file.filename)
    file.save(input_image_path)

    command = [
        os.path.join('venv', 'Scripts', 'python.exe'),  # Python from the virtual environment
        os.path.abspath('yolov5/detect.py'),  # Absolute path to detect.py
        '--source', input_image_path,
        '--weights', 'yolov5/runs/train/exp7/weights/best.pt',
        '--conf', '0.5',
        '--project', PROCESSED_IMAGES_DIR
    ]
    subprocess.run(command)

    results_dir = os.path.join(PROCESSED_IMAGES_DIR, 'exp')  # Папка с результатами
    output_dir = os.path.join(PROCESSED_IMAGES_DIR, 'final_results')  # Папка для окончательных результатов

    os.makedirs(output_dir, exist_ok=True)

    if os.path.exists(results_dir):
        for image in os.listdir(results_dir):
            image_path = os.path.join(results_dir, image)
            shutil.move(image_path, output_dir)

        shutil.rmtree(results_dir, ignore_errors=True)

    processed_images = os.listdir(output_dir)
    if processed_images:
        processed_image_path = os.path.join('static', 'processed_images', 'final_results', processed_images[-1])
    else:
        processed_image_path = None

    return render_template('upload.html', processed_image=processed_image_path)


if __name__ == '__main__':
    app.run(debug=True)
    db.close()
