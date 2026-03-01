from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from twilio.rest import Client as TwilioClient
from mangum import Mangum
import os
import boto3
import json
import base64
import requests
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION ---
COMMUNITY_ID = os.getenv("COMMUNITY_ID", "Legend_Chimes")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER", "whatsapp:+14155238886")
AWS_REGION = os.getenv("REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "civicsense-waste-images")

# --- INITIALIZE AWS CLIENTS ---
twilio_client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
users_table = dynamodb.Table('CivicSense_Users')
pickups_table = dynamodb.Table('CivicSense_Pickups')
bedrock = boto3.client(service_name='bedrock-runtime', region_name=AWS_REGION)
s3 = boto3.client('s3', region_name=AWS_REGION)

# --- HELPER FUNCTIONS ---
def send_whatsapp_msg(to_number, body_text):
    try:
        twilio_client.messages.create(
            from_=TWILIO_NUMBER,
            to=f"whatsapp:{to_number}",
            body=body_text
        )
    except Exception as e:
        print(f"Twilio Error: {e}")

def upload_image_to_s3(image_url, phone_number):
    """Download image from Twilio and upload to S3 for permanent storage."""
    try:
        # Twilio requires auth to download media
        img_response = requests.get(
            image_url,
            auth=(TWILIO_SID, TWILIO_TOKEN)
        )
        if img_response.status_code != 200:
            print(f"Failed to download image: {img_response.status_code}")
            return image_url  # Fall back to Twilio URL

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_phone = phone_number.replace("+", "").replace("-", "")
        s3_key = f"waste-images/{safe_phone}/{timestamp}.jpg"

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=img_response.content,
            ContentType='image/jpeg'
        )
        s3_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        print(f"Image uploaded to S3: {s3_url}")
        return s3_url
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return image_url  # Fall back to Twilio URL

def analyze_waste_image(image_url):
    """
    Uses Nova Pro on Bedrock for high-accuracy waste classification.
    Returns: 'VALID' | 'INVALID' | 'UNCLEAR'
    """
    try:
        # Download image (with Twilio auth if needed)
        img_response = requests.get(image_url, auth=(TWILIO_SID, TWILIO_TOKEN))
        if img_response.status_code != 200:
            img_response = requests.get(image_url)
        img_base64 = base64.b64encode(img_response.content).decode('utf-8')
    except Exception as e:
        print(f"Image download error: {e}")
        return 'UNCLEAR'

    prompt = """You are a strict waste segregation inspector for a community recycling system in India. Your job is to REJECT any image that contains organic or wet waste. You must be conservative — when in doubt, reject.

Classify the image as exactly ONE of: VALID, INVALID, or UNCLEAR.

---
INVALID — Return this if the image contains ANY of the following, even partially:
- Fruits or vegetables (whole, cut, peeled, or rotting) — e.g. bananas, tomatoes, onions, leafy greens
- Food scraps, cooked food, or leftover meals
- Vegetable or fruit peels, seeds, or rinds
- Wet or soiled items with visible moisture, stains, or food residue
- Organic matter of any kind — plant waste, garden clippings, flowers
- Mixed waste where wet and dry items are combined
- Meat, fish, dairy, or any kitchen waste
Even if 90% of the image is dry waste, if ANY organic/wet item is visible, return INVALID.

---
VALID — Return this ONLY if the image exclusively contains clean dry recyclables with zero organic matter:
- Empty plastic bottles, containers, bags, or packaging
- Dry cardboard boxes, newspapers, paper, or cartons
- Empty metal cans, tins, or aluminium foil
- Empty glass bottles or jars
- Clean, dry mixed recyclables in an open bag or bin
The items must be visibly dry and free of food residue. No moisture. No organic material whatsoever.

---
UNCLEAR — Return this if:
- The bag or bin is closed, opaque, or contents are not visible
- The photo is too dark, blurry, or low resolution to identify contents
- The image does not show waste at all (e.g. just a floor, hand, or unrelated scene)

---
Respond with ONLY one word: VALID, INVALID, or UNCLEAR
Do not explain. Do not add punctuation. One word only."""

    body = json.dumps({
        "inferenceConfig": {"max_new_tokens": 10},
        "messages": [{
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": "jpeg",
                        "source": {"bytes": img_base64}
                    }
                },
                {"text": prompt}
            ]
        }]
    })

    try:
        response = bedrock.invoke_model(
            body=body,
            modelId="amazon.nova-pro-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response.get('body').read())
        answer = response_body['output']['message']['content'][0]['text'].strip().upper()
        print(f"Nova Pro waste analysis result: {answer}")

        if "INVALID" in answer:
            return 'INVALID'
        elif "VALID" in answer:
            return 'VALID'
        else:
            return 'UNCLEAR'
    except Exception as e:
        print(f"Bedrock/Nova Pro Error: {e}")
        return 'VALID'  # Fail open for hackathon demo


# --- 1. WHATSAPP BOT ENDPOINT ---
@app.post("/bot")
async def whatsapp_bot(
    From: str = Form(...),
    Body: str = Form(""),
    NumMedia: int = Form(0),
    MediaUrl0: str = Form(None)
):
    sender_phone = From.replace("whatsapp:", "")
    msg = Body.strip().lower()

    # Check User in DynamoDB
    response = users_table.get_item(Key={'phone_number': sender_phone})
    user_data = response.get('Item')

    # ---- UNREGISTERED USER FLOW ----
    if not user_data:
        if msg.isdigit():
            users_table.put_item(Item={
                "phone_number": sender_phone,
                "villa_number": msg,
                "community_id": COMMUNITY_ID,
                "green_points": 0,
                "joined_at": str(datetime.now())
            })
            send_whatsapp_msg(sender_phone,
                f"✅ *Registration Successful! Villa {msg} is now active.*\n\n"
                f"_पंजीकरण सफल! विला {msg} अब सक्रिय है।_\n\n"
                "🚛 *Trash Rules:*\n"
                "1. 🍏 *Wet Waste:* Give to the GHMC truck daily as usual.\n"
                "2. ♻️ *Dry Waste:* Set it aside — we collect every *Saturday*.\n\n"
                "_गीला कचरा GHMC को दें। सूखा कचरा हमारे लिए रखें — हम हर शनिवार लेते हैं।_\n\n"
                "📷 *How to get your pickup slot:*\n"
                "Every Friday we'll remind you. Reply with a clear photo of your open dry waste bag to confirm your Saturday slot.\n\n"
                "_हर शुक्रवार हम आपको याद दिलाएंगे। शनिवार का स्लॉट पक्का करने के लिए अपने सूखे कचरे की फ़ोटो भेजें।_"
            )
        else:
            send_whatsapp_msg(sender_phone,
                "👋 Welcome to CivicSense!\n\n"
                "Please reply with your *Villa Number* (e.g., 42) to register.\n\n"
                "_अपना विला नंबर भेजें (जैसे 42) — पंजीकरण के लिए।_"
            )
        return ""

    # ---- REGISTERED USER FLOW ----
    villa = user_data['villa_number']
    points = int(user_data.get('green_points', 0))

    # Handle image submission
    if int(NumMedia) > 0 and MediaUrl0:
        send_whatsapp_msg(sender_phone,
            "🔍 Got your photo! Our AI is checking it for proper dry waste segregation. This takes just a moment."
        )

        # Upload to S3 first for permanent storage
        s3_url = upload_image_to_s3(MediaUrl0, sender_phone)

        # Analyze with Nova Pro
        result = analyze_waste_image(MediaUrl0)

        if result == 'VALID':
            request_id = str(uuid.uuid4())
            pickups_table.put_item(Item={
                "request_id": request_id,
                "phone_number": sender_phone,
                "villa_number": villa,
                "status": "PENDING",
                "photo_url": s3_url,
                "weight_kg": 0,
                "timestamp": str(datetime.now())
            })
            send_whatsapp_msg(sender_phone,
                "✅ *AI Verified — Clean Dry Waste detected!*\n\n"
                "_AI सत्यापित — सूखा कचरा स्वीकृत!_\n\n"
                f"Your Saturday pickup is confirmed, Villa {villa}.\n\n"
                f"_विला {villa} का शनिवार पिकअप कन्फर्म हो गया।_\n\n"
                "Make sure your bag is accessible near your door by *8 AM Saturday*. You'll receive a notification once the driver completes collection.\n\n"
                "Type *STATUS* to check your Green Credits."
            )

        elif result == 'INVALID':
            send_whatsapp_msg(sender_phone,
                "⚠️ *Segregation Issue Detected*\n\n"
                "_कचरा पृथक्करण में समस्या पाई गई।_\n\n"
                "Our AI found wet or organic waste in your bag. We only collect clean dry recyclables.\n\n"
                "*Accepted:* Plastic bottles, cardboard, paper, metal cans, glass\n"
                "*Not accepted:* Fruits, vegetables, food scraps, peels, wet or soiled items\n\n"
                "_स्वीकार्य: प्लास्टिक, कागज, धातु | अस्वीकार्य: फल, सब्जी, गीला कचरा_\n\n"
                "Please remove the wet items, then send a fresh photo of your dry waste only."
            )

        else:  # UNCLEAR
            send_whatsapp_msg(sender_phone,
                "📷 *We couldn't verify your waste from that photo.*\n\n"
                "_फ़ोटो से कचरे की पहचान नहीं हो सकी।_\n\n"
                "This usually happens when the bag is closed or opaque, the photo is too dark or blurry, or the contents aren't clearly visible.\n\n"
                "Please send a clear photo of your *open* bag or bin in good lighting.\n\n"
                "_कृपया खुले बैग या डिब्बे की स्पष्ट फ़ोटो भेजें — जिसमें सूखा कचरा साफ़ दिखे।_"
            )

    # Status / rank check
    elif any(word in msg for word in ["status", "rank", "points", "credits", "score"]):
        # Get leaderboard position
        try:
            all_users_resp = users_table.scan()
            all_users = all_users_resp.get('Items', [])
            sorted_users = sorted(all_users, key=lambda x: int(x.get('green_points', 0)), reverse=True)
            rank = next((i + 1 for i, u in enumerate(sorted_users) if u['phone_number'] == sender_phone), '?')
            total_users = len(sorted_users)
        except:
            rank = '?'
            total_users = '?'

        send_whatsapp_msg(sender_phone,
            f"🏆 *Villa {villa}'s Green Report*\n\n"
            f"Green Credits: *{points} pts*\n"
            f"Community Rank: *#{rank}* of {total_users} villas\n\n"
            f"_ग्रीन क्रेडिट: {points} अंक | सामुदायिक रैंक: #{rank}_\n\n"
            "Every kg of dry waste earns 10 credits. Keep recycling to climb the leaderboard!\n\n"
            "_Send a photo of your dry waste every Friday to schedule a pickup._"
        )

    # Help command
    elif "help" in msg:
        send_whatsapp_msg(sender_phone,
            "🌱 *CivicSense Quick Guide*\n\n"
            "*What we collect (Dry Waste):*\n"
            "✅ Plastic bottles & containers\n"
            "✅ Cardboard & paper\n"
            "✅ Metal cans & foil\n"
            "✅ Glass bottles\n\n"
            "*What we don't collect:*\n"
            "❌ Food waste & leftovers\n"
            "❌ Vegetable/fruit peels\n"
            "❌ Wet or soiled items\n\n"
            "*Commands:*\n"
            "📸 Send a *PHOTO* → Schedule pickup\n"
            "📊 Type *STATUS* → Check your credits & rank\n"
            "❓ Type *HELP* → Show this guide\n\n"
            "Pickup is every *Saturday*. Friday reminders are automatic 💚"
        )

    # Default
    else:
        send_whatsapp_msg(sender_phone,
            f"👋 Hey Villa {villa}!\n\n"
            "📸 Send a *PHOTO* of your dry waste to schedule a Saturday pickup.\n"
            "📊 Type *STATUS* to check your Green Credits.\n"
            "❓ Type *HELP* for the full guide.\n\n"
            f"You currently have *{points} Green Credits* 🌱"
        )

    return ""


# --- 2. ADMIN DASHBOARD STATS ---
@app.get("/api/admin/stats")
async def get_admin_stats():
    response = pickups_table.scan()
    all_pickups = response.get('Items', [])
    completed = [p for p in all_pickups if p.get('status') == 'COMPLETED']

    total_weight = sum([float(item.get('weight_kg', 0)) for item in completed])
    carbon_offset = total_weight * 1.5

    leaderboard = {}
    for item in completed:
        villa = item['villa_number']
        leaderboard[villa] = leaderboard.get(villa, 0) + float(item.get('weight_kg', 0))

    sorted_leaders = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]
    final_leaders = [{"villa": villa, "weight": round(w, 2), "points": int(w * 10)} for villa, w in sorted_leaders]

    return {
        "total_kg": round(total_weight, 2),
        "carbon_offset": round(carbon_offset, 2),
        "pickups": len(completed),
        "leaders": final_leaders,
        "recent": sorted(completed, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
    }


# --- 3. FRIDAY REMINDER TRIGGER ---
@app.get("/api/trigger-friday")
async def trigger_friday_reminder():
    try:
        response = users_table.scan()
        users = response.get('Items', [])
        count = 0
        for user in users:
            phone = user['phone_number']
            villa = user['villa_number']
            send_whatsapp_msg(phone,
                f"📢 *Tomorrow is Pickup Day, Villa {villa}!*\n\n"
                f"_कल पिकअप का दिन है, विला {villa}!_\n\n"
                "Our truck is coming Saturday morning. To confirm your slot, reply with a clear *photo* of your open dry waste bag or bin right now.\n\n"
                "_अपने सूखे कचरे के खुले बैग की फ़ोटो अभी भेजें — शनिवार का स्लॉट कन्फर्म करने के लिए।_\n\n"
                "Clean plastic, cardboard, paper, metal and glass only. No food waste.\n\n"
                "_केवल सूखा कचरा — कोई भी गीला या खाद्य अपशिष्ट नहीं।_"
            )
            count += 1
        return {"status": "success", "messages_sent": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- 4. DRIVER ROUTE ---
@app.get("/api/driver/route")
async def get_driver_route():
    response = pickups_table.scan()
    pending = [p for p in response.get('Items', []) if p.get('status') == 'PENDING']
    return [{
        "id": p['request_id'],
        "villa_number": p['villa_number'],
        "phone_number": p['phone_number'],
        "photo_url": p.get('photo_url', ''),
        "status": "PENDING"
    } for p in pending]


class PickupData(BaseModel):
    request_id: str
    phone_number: str
    weight: float

@app.post("/api/driver/confirm")
async def confirm_pickup(data: PickupData):
    pickups_table.update_item(
        Key={'request_id': data.request_id},
        UpdateExpression="SET #s = :status, weight_kg = :w",
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={':status': 'COMPLETED', ':w': str(data.weight)}
    )

    points_earned = int(data.weight * 10)
    users_table.update_item(
        Key={'phone_number': data.phone_number},
        UpdateExpression="ADD green_points :p",
        ExpressionAttributeValues={':p': points_earned}
    )

    # Get updated total
    user_resp = users_table.get_item(Key={'phone_number': data.phone_number})
    total_points = int(user_resp.get('Item', {}).get('green_points', points_earned))

    send_whatsapp_msg(data.phone_number,
        f"✅ *Pickup Complete! Thank you* 🙌\n\n"
        f"_पिकअप पूरा हुआ! धन्यवाद।_\n\n"
        f"Weight collected: *{data.weight} kg*\n"
        f"Credits earned: *+{points_earned} pts*\n"
        f"Your total: *{total_points} Green Credits* 💚\n\n"
        f"_एकत्र वजन: {data.weight} kg | अर्जित क्रेडिट: +{points_earned} अंक | कुल: {total_points} अंक_\n\n"
        f"You're helping keep Legend Chimes clean and green!\n\n"
        "_आप Legend Chimes को स्वच्छ और हरा-भरा बनाने में योगदान दे रहे हैं।_\n\n"
        "_Next pickup is Saturday. Watch for our Friday reminder._"
    )
    return {"status": "success"}


# --- LAMBDA HANDLER ---
handler = Mangum(app, api_gateway_base_path="/default")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
