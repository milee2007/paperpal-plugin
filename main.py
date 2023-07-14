import json

import quart
import quart_cors
from quart import request
from essential_generators import DocumentGenerator

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keeps track of scores. Does not persist if Python session is restarted.
_SCORE = {}
_PARAGRAPHS = {}

# Generates a random paragraph, needs to be replaced with sample text from Paper Pal 
@app.get("/paragraph/<string:username>")
async def get_paragraph(username):
    gen = DocumentGenerator()
    paragraph = gen.paragraph()
    # replace the above 2 lines with API call to Paper Pal to get sample texts
    _PARAGRAPHS[username] = paragraph
    if username not in _SCORE:
        _SCORE[username] = 0 
    return quart.Response(response=json.dumps(paragraph), status=200)

# Checks if the paragraph sent by the user is correct, needs to be changed to see if theres any edit made and respective scores are added 
@app.post("/paragraph/<string:username>")
async def check_paragraph(username):
    request = await quart.request.get_json(force=True)
    if username not in _PARAGRAPHS:
        return quart.Response(response='OK', status=404)
    updated_paragraph = request["paragraph"]
    original_paragraph = _PARAGRAPHS[username]
    # 100 points are added if correct but should be changed to scores being respective of the type of error corrected
    if updated_paragraph == original_paragraph: # instead of this, call Paper Pal API to verify if all mistakes are fixed 
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