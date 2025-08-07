import os
import random
import yaml
import numpy as np
from flask import Flask, render_template, request, session, send_from_directory

from utils.functions import generate_random_word, calculate_cosine_similarity_value, text_processing
from datetime import datetime

# Cargar configuración
"""
def load_config(path: str = "config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

HUGGING_FACE_API_URL = config["hugging_face"]["api_url"]
HUGGING_FACE_TOKEN = config["hugging_face"]["token"]
"""
HUGGING_FACE_API_URL = os.getenv("HUGGING_FACE_API_URL")
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

# Iniciar Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/sw.js')
def monetag_verification():
    return send_from_directory('static', 'sw.js')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        today = datetime.now().strftime('%Y%m%d')

        if session.get('winner') and session.get('winner_date') == today:
            return render_template(
                "index.html",
                word1=session["word1"],
                word2=session["word2"],
                system_word=session['winner_word'],
                similarity_percent=100,
                message=f"You win! The word was: {session['winner_word']}"
            )
        else:
            session.clear()

    if 'initial_random_word' not in session:
        # Setup game
        initial_random_word = generate_random_word()
        word1 = "TORRADA"
        word2 = "EMPANADA"
        sim1 = calculate_cosine_similarity_value(HUGGING_FACE_API_URL, HUGGING_FACE_TOKEN, initial_random_word, word1)
        sim2 = calculate_cosine_similarity_value(HUGGING_FACE_API_URL, HUGGING_FACE_TOKEN, initial_random_word, word2)

        if sim1 > sim2:
            system_word, system_sim = word1, sim1
        else:
            system_word, system_sim = word2, sim2

        # Guardar estado
        session['initial_random_word'] = initial_random_word
        session['system_word'] = system_word
        session['system_similarity'] = system_sim
        session['word1'] = word1
        session['word2'] = word2

        similarity_percent = int(round(system_sim * 100, 0))

        return render_template("index.html", word1=word1, word2=word2, system_word=system_word, similarity_percent=similarity_percent, message=None)
    
    # POST (guess)
    guess = text_processing(request.form['guess'])

    target = session['initial_random_word']
    word1 = session['word1']
    word2 = session['word2']
    system_word = session["system_word"]
    
    if guess == system_word:
        similarity_percent = int(round(session['system_similarity'] * 100, 0))
        return render_template(
            "index.html",
            word1=word1,
            word2=word2,
            system_word=system_word,
            similarity_percent=similarity_percent,
            message=None
        )
    if word1 == system_word:
        word2 = guess
        session['word2'] = word2
    else:
        word1 = guess
        session['word1'] = word1

    winner = guess == target

    if winner:
        message = f"You win! The word was: {target}"
        session['winner'] = True
        session['winner_word'] = target
        session['winner_date'] = datetime.now().strftime('%Y%m%d')

        return render_template("index.html", word1=word1, word2=word2, system_word=guess, similarity_percent=100, message=message)

    sim = calculate_cosine_similarity_value(HUGGING_FACE_API_URL, HUGGING_FACE_TOKEN, target, guess)

    if sim > session['system_similarity']:
        session['system_word'] = guess
        session['system_similarity'] = sim

    similarity_percent = int(round(session['system_similarity'] * 100, 0))

    return render_template("index.html", word1=word1, word2=word2, system_word=session['system_word'], similarity_percent=similarity_percent, message=None)

if __name__ == '__main__':
    app.run(debug=True)
