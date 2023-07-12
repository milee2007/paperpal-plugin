import json

import quart
import quart_cors
from quart import request
from essential_generators import DocumentGenerator

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of scores. Does not persist if Python session is restarted.
_SCORE = {}
_PARAGRAPHS = {}

@app.get("/paragraph/<string:username>")
async def get_paragraph(username):
    gen = DocumentGenerator()
    paragraph = gen.paragraph()
    _PARAGRAPHS[username] = paragraph
    if username not in _SCORE:
        _SCORE[username] = 0
    return quart.Response(response=json.dumps(paragraph), status=200)

@app.post("/paragraph/<string:username>")
async def check_paragraph(username):
    request = await quart.request.get_json(force=True)
    if username not in _PARAGRAPHS:
        return quart.Response(response='OK', status=404)
    updated_paragraph = request["paragraph"]
    original_paragraph = _PARAGRAPHS[username]
    if updated_paragraph == original_paragraph:
        _SCORE[username] += 100
        return quart.Response(response=json.dumps(_SCORE.get(username, 0)), status=200)
    return quart.Response(response=json.dumps("Please try again by fixing the grammar mistakes"), status=200)

@app.get("/.well-known/logo.jpeg")
async def plugin_logo():
    filename = '.well-known/logo.jpeg'
    return await quart.send_file(filename, mimetype='image/jpeg')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/.well-known/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open(".well-known/openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()