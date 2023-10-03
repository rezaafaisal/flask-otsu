from flask import Flask, request, jsonify
import requests
import cv2
import numpy as np
import os
from io import BytesIO
from PIL import Image
from datetime import datetime
import pytz
from werkzeug.utils import secure_filename
import json
import logging

app = Flask(__name__)

token = '6391112787:AAGs2P9-7ELdc634teCC7e7wKysqIqa7A7g'

def endpoint(method):
    url = 'https://api.telegram.org/bot'+token+'/'+method
    return url
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'jpg', 'png', 'jpeg'}

def caption(otsu, category):
    now = datetime.now(pytz.timezone('Asia/Makassar'))
    datenow = "{day}-{month}-{year}, {hour}:{minute} WITA".format(
                day=now.day,
                month=now.month,
                year=now.year,
                hour=now.hour,
                minute=now.minute)

    text = f"Tanggal\t:\n{datenow}\n\nNilai Otsu\t: {round(otsu, 2)}\nKualitas\t: {category}"
    return text

def image_proccess(image_request):
    # save image from request to directory
    if image_request and allowed_file(image_request.filename):
        filename = secure_filename(image_request.filename)
        image_path = os.path.join('images', filename)
        image_request.save(image_path)
    
        # compress image
        img = Image.open(image_path)
        img = img.resize((600, 600), Image.LANCZOS)
        img = img.convert('RGB')
        img.save(image_path, optimize=True, quality=95)
        return image_path, filename
    return "Something errors"

def otsu_proccess(image_path):
    gray_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresholded_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Hitung nilai Otsu
    otsu_value = cv2.mean(thresholded_image)[0]

    # Tentukan kategori berdasarkan nilai Otsu
    if otsu_value <= 35:
        category = "Air rendaman harus diganti"
    elif otsu_value >= 70 and otsu_value <= 36:
        category = "Air rendaman lumayan keruh"
    else:
        category = "Air rendaman masih jernih"


    # Simpan gambar hasil thresholding
    output_path = 'images/threshold.jpg'
    cv2.imwrite(output_path, thresholded_image)
    
    return otsu_value, category, output_path

def send_image(chat_id, image_path, result_img, filename, caption):
    files = {
        'original': open(image_path, 'rb'),
        'result' : open(result_img, 'rb')
    }
    
    data = {
        'chat_id': chat_id,
        'media': json.dumps([
            {'type': 'photo', 'media': 'attach://original'},
            {'type': 'photo', 'media': 'attach://result'},
        ])
    }
    
    text = {
        'chat_id': chat_id,
        'text': caption
    }
        
    response = requests.post(endpoint('sendMediaGroup'), data=data, files=files)
    if response.status_code == 200:
        requests.post(endpoint('sendMessage'), data=text)
    
    return response
    
def send_message(chat_id, text):
    url = endpoint('sendMessage')
    data = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, data=data)
    return response

def parse_message(message_data):
    chat_id = message_data['message']['chat']['id']
    message = message_data['message']['text']
    return chat_id, message.lower()

def write_json(data, filename):
    json_string = json.dumps(data)
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)

def read_json(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    return data

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        app.logger.debug('this is a DEBUG message')
        app.logger.info('this is an INFO message')
        app.logger.warning('this is a WARNING message')
        app.logger.error('this is an ERROR message')
        app.logger.critical('this is a CRITICAL message')
        
    if request.method == 'POST':
        data = request.get_json()
        chat_id, message_text = parse_message(data)
        
        new_data = read_json('user.json')
        # add new subscriber
        if message_text == '/start':
            if chat_id not in new_data:
                new_data.append(chat_id)
                write_json(new_data, 'user.json')
                response_text = 'Anda akan mendapatkan notifikasi mengenai kualitas air rendaman merica\nketik /stop untuk berhenti mendapatkan notifikasi'
            else:
                response_text = 'Anda sudah terdaftar.'
        
        # remove from subscriber
        elif message_text == '/stop':
            if chat_id in new_data:
                new_data.remove(chat_id)
                write_json(new_data, 'user.json')
                response_text = 'Anda tidak akan mendapatkan notifikasi lagi, Terima kasih!'
            else:
                response_text = 'Anda sudah tidak terdaftar lagi.'
        
        elif message_text == '/help':
            response_text = 'Halo selamat datang di toko kami, untuk petunjuknya silahkan ikuti perintah dibawah :\n/start untuk mulai mendapatkan notifikasi secara rutin dari sistem\n\n/stop untuk berhenti mendapatkan notifikasi dari sistem'
        
        elif 'gelud' in message_text:
            response_text = 'skuy sharelok nya dong puh!'
            
        elif 'sepuh' in message_text:
            response_text = 'Aaa sepuh bisa aja, ajarin dong sepuh. Tingki wingki dipsi lala Puhhh Sepuhhh'
        
        else:
            response_text = 'Perintah tidak dikenali. Ketik /help untuk bantuan'
            
        # send message
        response = send_message(chat_id, response_text)
        
        if response.status_code == 200:
            return "Berhasil mengirim pesan."
        else:
            return f"Gagal mengirim pesan. Status Code: {response.status_code}\n{response.text}"
        
    return "welcome to mobile legend"

@app.route('/upload', methods=['POST'])
def upload_image():
    # check request
    if 'image' not in request.files:
        return "No image file provided", 400
    
    # process image
    image_path, filename = image_proccess(request.files['image'])
    
    # otsu proccess
    otsu_value, category, result_img = otsu_proccess(image_path)

    # send message to telegram
    users = read_json('user.json')
    response = None
    if users:
        for user in users:
            response = send_image(chat_id=user,
                                image_path=image_path,
                                result_img=result_img,
                                filename=filename,
                                caption=caption(otsu_value, category))
    # remove file
    os.remove(image_path)
    os.remove(result_img)
    
    if response is None:
        return "Tidak ada user"
    
    elif response.status_code == 200:
        return "Berhasil mengirim gambar."
    else:
        return f"Gagal mengirim foto. Status Code: {response.status_code}\n{response.text}"

@app.route('/send-text', methods=['POST'])
def send_text():
    text = request.form['text']
    return text

if __name__ == 'main':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
else:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)