import random
import numpy as np
import json
from typing import Tuple
import requests
import unicodedata
from datetime import datetime

def text_processing(
        text: str
):
    text_processed = text.upper()
    text_processed = unicodedata.normalize('NFD', text_processed).encode('ascii', 'ignore').decode('utf-8')
    return text_processed

def generate_random_word_deprecated(
        client
) -> str:    
    random_seed = random.randint(0, 99999)
    completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": f"Pick a random English word. This request has ID {random_seed}. Return as JSON: {{\"word\": \"<random_word>\"}}"
            }
        ],
        temperature=0.9,
        top_p=1.0,                  # controla la probabilidad acumulada de sampling
        frequency_penalty=0.5,      # para evitar repeticiones
        presence_penalty=0.5,       # para favorecer novedad
    )

    initial_random_word = json.loads(completion.choices[0].message.content)["word"]
    initial_random_word = text_processing(initial_random_word)
    print(initial_random_word)
    return initial_random_word

def generate_random_word_deprecated2():
    url = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt"
    response = requests.get(url)
    common_words = response.text.splitlines()

    # Filtramos las 5000 primeras más comunes, y evitamos palabras muy cortas
    filtered_words = [w for w in common_words[:5000] if len(w) > 3]
    initial_random_word = random.choice(filtered_words)
    initial_random_word = text_processing(initial_random_word)
    print(initial_random_word)
    return initial_random_word

def generate_random_word():

    url = "https://raw.githubusercontent.com/Softcatala/catalan-dict-tools/refs/heads/master/frequencies/frequencies-dict-forms.txt"
    response = requests.get(url)
    common_words = response.text.splitlines()
    common_words = np.char.split(common_words, ',')
    common_words = np.array([w[0].strip() for w in common_words])

    # Filtramos las 5000 primeras más comunes, y evitamos palabras muy cortas
    filtered_words = [w for w in common_words[:5000] if len(w) > 3 and 'l·l' not in w.lower()]

    today_seed = int(datetime.now().strftime('%Y%m%d'))
    random.seed(today_seed)

    initial_random_word = random.choice(filtered_words)
    initial_random_word = text_processing(initial_random_word)
    print(initial_random_word)
    return initial_random_word

def cosine_similarity(
        a: np.ndarray, 
        b: np.ndarray
) -> float:
    a = a.flatten()
    b = b.flatten()
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def calculate_cosine_similarity_value(
        api_url,
        token,
        word1: str,
        word2: str
) -> float:
    
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "inputs": {
            "source_sentence": word1.lower(),
            "sentences": [word2.lower()]
        }
    }

    response = requests.post(api_url, headers=headers, json=data)
    value = response.json()[0]

    return value


def calculate_cosine_similarity_value_deprecated1(
        client,
        word1: str,
        word2: str
) -> Tuple[float, np.ndarray, np.ndarray]:
    embedding1 = client.encode(
        word1
    )

    embedding2 = client.encode(
    word2
    )

    cosine_similarity_value = cosine_similarity(embedding1, embedding2)
    return cosine_similarity_value, embedding1, embedding2

def calculate_cosine_similarity_value_deprecated2(
        client,
        word1: str,
        word2: str
) -> Tuple[float, np.ndarray, np.ndarray]:
    response = client.embeddings.create(
        input=word1,
        model="text-embedding-3-small"
    )
    embedding1 = np.array(response.data[0].embedding)

    response = client.embeddings.create(
    input=word2,
    model="text-embedding-3-small"
    )
    embedding2 = np.array(response.data[0].embedding)

    cosine_similarity_value = cosine_similarity(embedding1, embedding2)
    return cosine_similarity_value, embedding1, embedding2