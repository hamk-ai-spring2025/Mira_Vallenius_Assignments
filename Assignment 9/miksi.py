import json

response_text = '''
{
  "description": "Indulge in the luxurious softness of our thick, plush wool throw, crafted from premium, mulesing-free wool.  Perfect for adding warmth and style to any living space.  A thoughtful gift for discerning home decorators.",
  "slogans": [
    "Unwind in ultimate comfort.",
    "Luxury redefined, naturally.",
    "The perfect blend of style and sustainability."
  ]
}
'''

data = json.loads(response_text)
print("Tuotekuvaus:", data["description"])
print("Sloganit:")
for s in data["slogans"]:
    print("-", s)
