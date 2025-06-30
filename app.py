from flask import Flask, render_template, request, redirect, send_file
import os
from audio_utils import embed_message_in_audio, extract_message_from_audio
from image_utils import embed_message_pvd, extract_message_pvd
from video_utils import embed_message_in_video, extract_message_from_video

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

# --- AUDIO ---
@app.route('/audio', methods=['GET', 'POST'])
def audio():
    if request.method == 'POST':
        if 'embed' in request.form:
            audio_file = request.files['cover_audio']
            message = request.form['message']
            filename = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
            audio_file.save(filename)
            output = filename.replace('.wav', '_stego.wav')
            embed_message_in_audio(filename, message, output)
            return send_file(output, as_attachment=True)
        elif 'extract' in request.form:
            stego_file = request.files['stego_audio']
            filename = os.path.join(app.config['UPLOAD_FOLDER'], stego_file.filename)
            stego_file.save(filename)
            message = extract_message_from_audio(filename)
            return render_template('audio.html', extracted=message)
    return render_template('audio.html')

# --- IMAGE ---
@app.route('/image', methods=['GET', 'POST'])
def image():
    if request.method == 'POST':
        if 'embed' in request.form:
            image_file = request.files['cover_image']
            message = request.form['message']
            filename = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
            image_file.save(filename)
            output = filename.replace('.png', '_stego.png')
            embed_message_pvd(filename, message, output)
            return send_file(output, as_attachment=True)
        elif 'extract' in request.form:
            stego_file = request.files['stego_image']
            filename = os.path.join(app.config['UPLOAD_FOLDER'], stego_file.filename)
            stego_file.save(filename)
            message = extract_message_pvd(filename)
            return render_template('image.html', extracted=message)
    return render_template('image.html')

# --- VIDEO ---
@app.route('/video', methods=['GET', 'POST'])
def video():
    if request.method == 'POST':
        if 'embed' in request.form:
            video_file = request.files['cover_video']
            message = request.form['message']
            filename = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
            video_file.save(filename)
            output = filename.replace('.avi', '_stego.avi')
            embed_message_in_video(filename, message, output)
            return send_file(output, as_attachment=True)
        elif 'extract' in request.form:
            stego_file = request.files['stego_video']
            filename = os.path.join(app.config['UPLOAD_FOLDER'], stego_file.filename)
            stego_file.save(filename)
            message = extract_message_from_video(filename)
            return render_template('video.html', extracted=message)
    return render_template('video.html')

if __name__ == '__main__':
    app.run(debug=True)
