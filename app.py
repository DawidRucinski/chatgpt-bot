import base64
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
import aiapi
import config
from graphviz import Source
import openai
import re

openai.api_key = config.DevelopmentConfig.OPENAI_KEY

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import os
from dotenv import load_dotenv

load_dotenv()
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

import os
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

# Path to the Stanford NER JAR file
stanford_ner_jar = os.getenv('NER_JAR')

# Path to the Stanford NER model file
stanford_ner_model = os.getenv('NER_MODEL')

# Initialize the Stanford NER tagger
ner_tagger = StanfordNERTagger(stanford_ner_model, stanford_ner_jar)



def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def page_not_found(e):
    return render_template('404.html'), 404


def is_law_related(text):
    # Tokenize the input text
    words = word_tokenize(text)

    # Perform NER using the Stanford NER tagger
    entities = ner_tagger.tag(words)

    # Check if any entities are classified as law-related
    law_related_labels = ["ORGANIZATION", "LAW"]  # You can add more labels based on your specific needs
    for word, label in entities:
        if label in law_related_labels:
            return True

    return False


app = Flask(__name__)
app.config.from_object(config.config['development'])

app.register_error_handler(404, page_not_found)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        prompt = request.json['prompt']

        gpt_response = aiapi.get_response(prompt)

        # Check if the response contains graph code
        graph_code = None
        if '[GRAPH]' in gpt_response and '[/GRAPH]' in gpt_response:
            start = gpt_response.index('[GRAPH]') + 7
            print("graph")
            end = gpt_response.index('[/GRAPH]')
            graph_code = gpt_response[start:end].strip()
            gpt_response = gpt_response.replace(f'[GRAPH]{graph_code}[/GRAPH]', '').strip()
            print(gpt_response)
            graph_code = remove_html_tags(graph_code)
        return jsonify({'text': gpt_response, 'graphviz_code': graph_code})

    return render_template('index.html', **locals())


@app.route('/generate_image', methods=['POST'])
def generate_image():
    print("Generate Image Endpoint Called")
    graph_code = request.json['graph_code']
    s = Source(graph_code, format="png")
    print(graph_code)
    img_data = s.pipe()
    return jsonify({'image_data': base64.b64encode(img_data).decode('utf-8')})


def preprocess_prompt(prompt):
    # Tokenization
    tokens = word_tokenize(prompt)

    # Lowercasing
    tokens = [token.lower() for token in tokens]

    # Remove stopwords and punctuation
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token.isalnum() and token not in stop_words]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Join tokens back into a sentence
    preprocessed_prompt = ' '.join(tokens)
    return preprocessed_prompt


if __name__ == '__main__':
    load_dotenv()
    app.run(host='0.0.0.0', port='8888', debug=True)
