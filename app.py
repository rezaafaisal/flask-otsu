from flask import Flask, request, jsonify, send_file
import cv2
import numpy as np
from io import BytesIO

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return "haloo"

@app.route('/upload_image', methods=['POST'])
def upload_image():
    return request
    # if 'image' not in request.files:
    #     return "No image file provided", 400

    # image_file = request.files['image']
    # image_data = image_file.read()

    # # Ubah data gambar menjadi format yang dapat digunakan oleh OpenCV
    # image_np = np.frombuffer(image_data, np.uint8)
    # image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    # # Analisis citra menggunakan Otsu Thresholding
    # gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # _, thresholded_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # # Hitung nilai Otsu
    # otsu_value = cv2.mean(thresholded_image)[0]

    # # Tentukan kategori berdasarkan nilai Otsu
    # if otsu_value < 50:
    #     category = "Keruh Sekali"
    # elif otsu_value < 100:
    #     category = "Lumayan Keruh"
    # else:
    #     category = "Air Bersih"

    # # Simpan gambar hasil thresholding
    # _, buffer = cv2.imencode('.jpg', thresholded_image)
    # result_image_data = BytesIO(buffer)

    # return jsonify({
    #     'otsu_value': otsu_value,
    #     'category': category,
    #     'original_image': send_file(BytesIO(image_data), mimetype='image/jpeg'),
    #     'thresholded_image': send_file(result_image_data, mimetype='image/jpeg')
    # })

if __name__ == 'main':
    app.run(host='0.0.0.0', port=5000)