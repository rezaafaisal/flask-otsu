from flask import Flask, render_template, request, redirect, url_for
from flask_restful import Api, Resource
# import cv2
import numpy as np
import base64

app = Flask(__name__)
api = Api(app)  # Membuat instance Flask-RESTful API

# def otsu_thresholding(image):
#     _, segmented_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     return segmented_image

@app.route('/')
def index():
    return '<h1>haloo</h1>'

# class ArduinoImageResource(Resource):
#     def post(self):
#         image_data = request.data  # Menerima gambar dari Arduino dalam format yang sesuai
#         original_asli = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_UNCHANGED)
#         original_image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_GRAYSCALE)
#         segmented_image = otsu_thresholding(original_image)

#         _, original_buffer = cv2.imencode('.png', original_image)
#         original_image_base64 = base64.b64encode(original_buffer).decode('utf-8')

#         _, segmented_buffer = cv2.imencode('.png', segmented_image)
#         segmented_image_base64 = base64.b64encode(segmented_buffer).decode('utf-8')

#         _, asli_buffer = cv2.imencode('.png', original_asli)
#         original_asli_base64 = base64.b64encode(asli_buffer).decode('utf-8')

#         return {
#             'original_asli_base64': original_asli_base64,
#             'original_image_base64': original_image_base64,
#             'segmented_image_base64': segmented_image_base64
#         }

# api.add_resource(ArduinoImageResource, '/receive_image')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')