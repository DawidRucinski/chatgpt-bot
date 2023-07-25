import base64

from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
import config
import openai
import aiapi
import tempfile
import openai
import config
from flask import Flask, jsonify, request, send_file
from io import BytesIO
from graphviz import Source
import openai
openai.api_key = config.DevelopmentConfig.OPENAI_KEY


import re

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)



def page_not_found(e):
  return render_template('404.html'), 404


app = Flask(__name__)
app.config.from_object(config.config['development'])

app.register_error_handler(404, page_not_found)


@app.route('/', methods = ['POST', 'GET'])
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

if __name__ == '__main__':
    load_dotenv()
    app.run(host='0.0.0.0', port='8888', debug=True)
