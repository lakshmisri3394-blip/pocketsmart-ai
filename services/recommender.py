import os
import json
import re
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
except Exception:
    genai = None

PLATFORM_URLS = {
    "Amazon": "https://www.amazon.in/s?k={}",
    "Flipkart": "https://www.flipkart.com/search?q={}",
    "IKEA": "https://www.ikea.com/in/en/search/?q={}",
    "Swiggy": "https://www.swiggy.com/search?query={}",
    "Zomato": "https://www.zomato.com/search?query={}",
    "OYO": "https://www.oyorooms.com/search?location={}"
}

def platform_link(platform, query):
    base = PLATFORM_URLS.get(platform, "https://www.google.com/search?q={}")
    return base.format(quote_plus(query))

def fallback(category, data):
    budget = float(data.get("budget", 0))
    if category == "home":
        return {
            "summary": f"Home setup plan for a budget of ₹{budget:,.0f}.",
            "budget_breakdown": [
                {"category":"Lighting","amount":round(budget*0.15)},
                {"category":"Furniture","amount":round(budget*0.45)},
                {"category":"Decor","amount":round(budget*0.20)},
                {"category":"Storage","amount":round(budget*0.15)},
                {"category":"Buffer","amount":round(budget*0.05)}
            ],
            "recommendations": [
                {"item":"LED ceiling light","reason":"Energy-efficient and practical","platform":"Amazon","estimated_price":max(500,round(budget*.08)),"search_link":platform_link("Amazon","LED ceiling light")},
                {"item":"Compact furniture","reason":"Balances utility and available space","platform":"IKEA","estimated_price":max(1500,round(budget*.25)),"search_link":platform_link("IKEA","compact furniture")},
                {"item":"Wall decor","reason":"Adds personality without consuming floor space","platform":"Flipkart","estimated_price":max(500,round(budget*.08)),"search_link":platform_link("Flipkart","wall decor")}
            ]
        }
    if category == "party":
        guests=int(data.get("guests",1))
        return {
            "summary": f"Party plan for {guests} guests within ₹{budget:,.0f}.",
            "budget_breakdown": [
                {"category":"Food","amount":round(budget*.50)},
                {"category":"Decoration","amount":round(budget*.15)},
                {"category":"Venue","amount":round(budget*.20)},
                {"category":"Entertainment","amount":round(budget*.10)},
                {"category":"Buffer","amount":round(budget*.05)}
            ],
            "recommendations": [
                {"item":"Catering / food package","reason":"Largest allocation because food is central to the event","platform":"Swiggy","estimated_price":round(budget*.50),"search_link":platform_link("Swiggy","party catering")},
                {"item":"Decor package","reason":"Simple decor keeps the event attractive","platform":"Amazon","estimated_price":round(budget*.15),"search_link":platform_link("Amazon","party decoration")},
                {"item":"Venue search","reason":"Choose a venue that fits guest count and travel needs","platform":"OYO","estimated_price":round(budget*.20),"search_link":platform_link("OYO",data.get("venue","party venue"))}
            ]
        }
    return {
        "summary": f"Jewelry plan for a {data.get('occasion','special')} occasion within ₹{budget:,.0f}.",
        "budget_breakdown": [
            {"category":"Main jewelry","amount":round(budget*.60)},
            {"category":"Earrings","amount":round(budget*.20)},
            {"category":"Accessories","amount":round(budget*.10)},
            {"category":"Buffer","amount":round(budget*.10)}
        ],
        "recommendations": [
            {"item":"Occasion-matched necklace","reason":"Choose based on neckline, outfit color and occasion","platform":"Amazon","estimated_price":round(budget*.60),"search_link":platform_link("Amazon",f"{data.get('style','elegant')} necklace")},
            {"item":"Matching earrings","reason":"Creates a coordinated look","platform":"Flipkart","estimated_price":round(budget*.20),"search_link":platform_link("Flipkart",f"{data.get('style','elegant')} earrings")}
        ]
    }

def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start:end+1])
    raise ValueError("No JSON object found")

def gemini_recommend(category, data, image_bytes=None):
    key=os.getenv("GEMINI_API_KEY")
    if not key or genai is None:
        return fallback(category, data)

    genai.configure(api_key=key)
    # The supplied project specification names Gemini 1.5 Flash Pro.
    model_name=os.getenv("GEMINI_MODEL","gemini-1.5-flash")
    model=genai.GenerativeModel(model_name)

    common = """You are PocketSmart AI, a budget-aware recommendation assistant.
Return ONLY valid JSON. Do not claim real-time stock or exact live prices.
Use estimated prices and clearly label them as estimates.
Structure:
{
 "summary": "...",
 "budget_breakdown": [{"category":"...", "amount":0}],
 "recommendations": [
   {"item":"...", "reason":"...", "platform":"Amazon|Flipkart|IKEA|Swiggy|Zomato|OYO",
    "estimated_price":0}
 ]
}
Keep the total suggested spend within the user's budget."""
    if category=="home":
        prompt=common+f"""
Category: Home Interior
Budget: ₹{data['budget']}
Room: {data['room_type']}
Style: {data['style']}
Items/quantities: {data['items']}
Notes: {data['notes']}
"""
    elif category=="party":
        prompt=common+f"""
Category: Party Planning
Budget: ₹{data['budget']}
Guests: {data['guests']}
Event: {data['event_type']}
Venue preference: {data['venue']}
Preferences: {data['preferences']}
"""
    else:
        prompt=common+f"""
Category: Jewelry
Budget: ₹{data['budget']}
Occasion: {data['occasion']}
Style: {data['style']}
Outfit description: {data['outfit_description']}
"""
    contents=[prompt]
    if image_bytes:
        contents.append({"mime_type":"image/jpeg","data":image_bytes})
        contents.append("Use the outfit image only to infer broad color/style coordination. Do not identify the person.")

    try:
        response=model.generate_content(contents)
        result=extract_json(response.text)
        for item in result.get("recommendations",[]):
            platform=item.get("platform","Amazon")
            item["search_link"]=platform_link(platform,item.get("item","product"))
        return result
    except Exception:
        return fallback(category,data)
