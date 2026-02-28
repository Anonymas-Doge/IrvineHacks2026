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
def get_recipe():
    pass