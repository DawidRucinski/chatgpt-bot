import openai
import config
from flask import Flask, jsonify, request, send_file
from io import BytesIO
from graphviz import Source
import openai
openai.api_key = config.DevelopmentConfig.OPENAI_KEY



app = Flask(__name__)
conversation_history = []


# Existing function
def get_response(prompt, **kwargs):
    global conversation_history
    model = kwargs.get('model', "gpt-3.5-turbo")

    if not conversation_history:
        conversation_history.append(
            {"role": "system", "content": "You are an assistant directed towards simplifying legal issues to people"})

    conversation_history.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(model=model, messages=conversation_history)

    try:
        answer = response["choices"][0]["message"]["content"].replace('\n', '<br>')
        conversation_history.append({"role": "assistant", "content": answer})
    except:
        answer = "Sorry I am not able to understand your question. Please rephrase your question."

    return answer


@app.route('/', methods=["POST"])
def chat_endpoint():
    prompt = request.json['prompt']

    gpt_response = get_response(prompt)

    # Check if the response contains graph code
    graph_code = None
    if '[GRAPH]' in gpt_response and '[/GRAPH]' in gpt_response:
        start = gpt_response.index('[GRAPH]') + 7
        end = gpt_response.index('[/GRAPH]')
        graph_code = gpt_response[start:end].strip()
        gpt_response = gpt_response.replace(f'[GRAPH]{graph_code}[/GRAPH]', '').strip()

    return jsonify({'text': gpt_response, 'graph_code': graph_code})


@app.route('/generate_image', methods=["POST"])
def generate_image():
    graph_code = request.json['graph_code']
    source = Source(graph_code)

    img_bytes = source.pipe(format='png')
    img_io = BytesIO(img_bytes)

    return send_file(img_io, mimetype='image/png', as_attachment=False, cache_timeout=0)