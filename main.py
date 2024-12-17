import shutil

from flask import Flask, render_template, request, redirect
import os
import subprocess

from Database import Database

app = Flask(__name__)

host = "localhost"  # или IP-адрес вашего сервера
port = "5432"
database = "car_dealership"
user = "postgres"
password = "admin"
db = Database(host, port, database, user, password)
db.connect()

PROCESSED_IMAGES_DIR = 'static/processed_images'


@app.route('/')
def index():
    return render_template('index.html')


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
        os.path.join('venv', 'Scripts', 'python.exe'),  # Используем Python из виртуального окружения
        'yolov5/detect.py',
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


if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")

    db.close()
