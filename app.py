from flask import Flask, render_template, request, send_from_directory
from deepface import DeepFace
import os, random, traceback
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SONG_FOLDER'] = 'songs'

@app.route('/')
def home():
    return "Emotion Music Player is running!"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return render_template('index.html', error="No image uploaded")

    image = request.files['image']
    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)
    print(f"📸 Saved image to: {filepath}")

    try:
        print("🔍 Starting emotion analysis...")
        analysis = DeepFace.analyze(img_path=filepath, actions=['emotion'], detector_backend='opencv')
, enforce_detection=False)
        print("🔎 DeepFace output:", analysis)

        # Handle both list and dict formats
        if isinstance(analysis, list):
            emotion = analysis[0].get('dominant_emotion', 'neutral')
        elif isinstance(analysis, dict):
            emotion = analysis.get('dominant_emotion', 'neutral')
        else:
            emotion = 'neutral'

        print(f"😃 Detected emotion: {emotion}")
    except Exception as e:
        print("❌ Error analyzing image:")
        traceback.print_exc()
        return render_template('index.html', error=f"Error processing image: {str(e)}")
    finally:
        os.remove(filepath)

    emotion_folder = emotion if emotion in ['happy', 'sad', 'neutral'] else 'neutral'
    emotion_path = os.path.join(app.config['SONG_FOLDER'], emotion_folder)

    try:
        songs = [f for f in os.listdir(emotion_path) if f.endswith('.mp3')]
        if not songs:
            raise Exception("No songs found in folder")
        selected_song = random.choice(songs)
        song_url = f"/songs/{emotion_folder}/{selected_song}"
        print(f"🎵 Playing: {selected_song}")
    except Exception as e:
        print("❌ Error selecting song:")
        traceback.print_exc()
        return render_template('index.html', emotion=emotion, error=f"No songs found for emotion '{emotion_folder}'")

    return render_template('index.html', emotion=emotion, song_url=song_url)

@app.route('/songs/<emotion>/<filename>')
def serve_song(emotion, filename):
    return send_from_directory(
        os.path.join(app.config['SONG_FOLDER'], emotion),
        filename,
        mimetype='audio/mpeg'
    )

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    print("✅ Flask app is starting...")
    app.run(debug=True)