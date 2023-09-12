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
        img = img.resize((300, 300), Image.LANCZOS)
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
    if otsu_value < 50:
        category = "Keruh Sekali"
    elif otsu_value < 100:
        category = "Lumayan Keruh"
    else:
        category = "Air Bersih"

    # Simpan gambar hasil thresholding
    _, buffer = cv2.imencode('.jpg', thresholded_image)
    result_image_data = BytesIO(buffer)
    
    return otsu_value, category

def send_image(chat_id, image_path, filename, caption):
    with open(image_path, 'rb') as photo_file:
        files = {
            'photo': ('halo.jpg', photo_file),
        }
    
        data = {
            'chat_id': chat_id,
            'caption': caption
        }
        
        response = requests.post(endpoint('sendPhoto'), data=data, files=files)
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
        
    return "welcome"

@app.route('/upload', methods=['POST'])
def upload_image():
    # check request
    if 'image' not in request.files:
        return "No image file provided", 400
    
    # process image
    image_path, filename = image_proccess(request.files['image'])
    
    # otsu proccess
    otsu_value, category = otsu_proccess(image_path)

    # send message to telegram
    users = read_json('user.json')
    response = None
    if users:
        for user in users:
            response = send_image(chat_id=user,
                                image_path=image_path,
                                filename=filename,
                                caption=caption(otsu_value, category))
    # remove file
    os.remove(image_path)
    
    if response is None:
        return "Tidak ada user"
    
    elif response.status_code == 200:
        return "Berhasil mengirim gambar."
    else:
        return f"Gagal mengirim foto. Status Code: {response.status_code}\n{response.text}"

if __name__ == 'main':
    app.run(host='0.0.0.0', port=5000)