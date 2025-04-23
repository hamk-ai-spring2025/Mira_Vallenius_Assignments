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

try:
    parsed = json.loads(response_text)
    print("✅ JSON OK!")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))  # Tulostaa nätisti
except json.JSONDecodeError as e:
    print("❌ JSON ERROR:", e)
    print("Raw response:", response_text)

