<<<<<<< HEAD
import os
import requests
import flask
from flask_cors import CORS
from dotenv import load_dotenv
import google.genai as genai
import json
import re

load_dotenv() # load env file

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY: raise RuntimeError("GEMINI API KEY NOT SET!")
client = genai.Client(api_key=GEMINI_API_KEY)

RECIPE_URL = "https://recipe-api.com/api/v1/recipes"

app = flask.Flask(__name__)
CORS(app)

@app.route("/chat", methods=["GET"])
def chat():
    # data = flask.request.get_json(force=True)
    # prompt = data.get("prompt")
    recipe = flask.request.args.get("q")
    difficulty = flask.request.args.get("difficulty")

    content = []
    content.append({
        "role": "user",
        "parts": [
            {
                "text":
                '''given a tuple (food-item, difficulty: 'easy'|'medium'|'hard'), return a step by step recipe for it.
                easy difficulty should be a quick easy recipe without rare ingredents.
                hard difficulty should be gordan ramsey level gormet version of recipe.
                You should return In a valid JSON form in the structure:
                \\{
                  dish: NAME_OF_DISH,
                  instructions: [
                    [time, instruction],
                    [time, instruction]
                  ]
                  storageTime: NUMBER_OF_DAYS_BEFORE_FOOD_GOES_BAD
                \\}
                time should be in minutes, and only appear if it is time where the cooker can step away from the kitchen (i.e. 30: int, if instruction is "boil for 30 minutes)
                if not, time can be null.
                return nothing else but the raw json, (do not have it wrapped in a markdown block it should go through json.loads() in python w/o error)
                ''' 
            }
        ]
    })
    content.append({
        "role": "user",
        "parts": [{"text":f"({recipe}, {difficulty})"}]
    })

    if not recipe:
        flask.abort(400, "Missing 'dish'")
    if not difficulty in ["easy", "medium", "hard"]:
        flask.abort(400, "Invalid Difficulty")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content
        )

        parsed_text = response.text[8:-3]
        print("response:\n", parsed_text)
        return flask.jsonify(
            parse_json(parsed_text)
        )

    except Exception as e:
        flask.abort(500, str(e))

def parse_recipe():
    ...
# returns id of first recipe that fits query
@app.route("/getRecipe")
=======
def parse_recipe(data):
    item_name = data["data"]["name"]
    instructions = []
    for i in data["data"]["instructions"]:
        text = i["text"]
        duration = i["structured"]["duration"] if i["structured"]["duration"] else None
        action = i["structured"]["action"] if i["structured"]["action"] else None
        temperature = i["structured"]["temperature"]["fahrenheit"] if i["structured"]["temperature"]["fahrenheit"] else None
        instructions.append((text, action, duration,  temperature))
    #return instructions
>>>>>>> 16ea7f175d7fdbe90621743f016d2c0d4f19c1ea
def get_recipe():
    query_string = flask.request.args.get("q")
    res = requests.get(f"{RECIPE_URL}?q={query_string}", headers={
     "Content-Type": "application/json",
     "X-API-Key": os.getenv("API_KEY")
    })
    print(os.getenv("API_KEY"))
    print("RES")
    print(res)
    if not res.ok: flask.abort(500, "could not get data from recipes api")
    if len(res.json()["data"]) == 0: flask.abort(400, "given query is not a valid recipe in the api")

    return res.json()["data"][0]["id"]

@app.route("/getInstruction/<id>")
def get_instruction(id="06ff1c50-c861-4585-a575-4ad9b9dd9707"):
    res = requests.get(f"{RECIPE_URL}/{id}", headers={
     "Content-Type": "application/json",
     "X-API-Key": os.getenv("API_KEY")
    })

    if not res.ok: flask.abort(500, "could not get data from recipes api")

    return res.json()

def parse_json(text):
    match = re.match(r"\{.*\}", text, re.S)
    if not match: return TypeError("Not given valid json")
    return json.loads(match.group(0))

if __name__ == "__main__":
    app.run(debug=True)