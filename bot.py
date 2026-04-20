import telebot
import requests
import time
from google import genai

# --- TOKEN & API KEYS ---
TELEGRAM_TOKEN = "8667282272:AAGx9qoKDCr-2j6JTHW0oRhXXO8_OfBSzas"
GEMINI_API_KEY = "AIzaSyBrOEyTbWQhu5hQKaNNadsW2l0QdmMSHqA"
NEWSDATA_API_KEY = "pub_5171f9c689bb4542880d74e0a73d1bee"

# Gemini setup
client = genai.Client(api_key=GEMINI_API_KEY)

# Telegram bot setup
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def analyze_with_gemini(news_text):
    try:
        # لێرەدا ناوی مۆدێلەکەمان گۆڕیوە بۆ شێوازە فەرمییەکە
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"وەک پسپۆڕێکی کریپتۆ ئەم هەواڵە بە کوردی شیکار بکە: {news_text}"
        )
        return response.text
    except Exception as e:
        # ئەگەر دووبارە 404 بوو، ئەمە تاقی بکەرەوە
        try:
            response = client.models.generate_content(
                model="models/gemini-1.5-flash", # لێرە models/ مان بۆ زیاد کرد
                contents=f"وەک پسپۆڕێکی کریپتۆ ئەم هەواڵە بە کوردی شیکار بکە: {news_text}"
            )
            return response.text
        except Exception as e2:
            print(f"Gemini Error: {e2}")
            return "⚠️ مۆدێلەکە لەسەر سێرڤەر نەدۆزرایەوە."

def get_news():
    """Get crypto news"""
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q=crypto&language=en"
    try:
        response = requests.get(url).json()
        return response.get("results", [])
    except:
        return []

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🚀 بۆتە زیرەکە چالاک بوو!\nهەواڵی کریپتۆ دەهێنرێت و Gemini شیکاری بۆ دەکات."
    )

    already_sent = set()

    while True:
        try:
            news_list = get_news()
            for news in news_list:
                title = news.get("title")
                link = news.get("link")

                if title and title not in already_sent:
                    analysis = analyze_with_gemini(title)

                    final_msg = (
                        f"📰 **هەواڵ:** {title}\n\n"
                        f"🔗 {link}\n"
                        f"-----------------\n"
                        f"🤖 **شیکاری AI:**\n{analysis}"
                    )

                    bot.send_message(
                        message.chat.id,
                        final_msg,
                        parse_mode="Markdown"
                    )

                    already_sent.add(title)

                    # پاراستنی میمۆری
                    if len(already_sent) > 100:
                        already_sent.clear() 

            time.sleep(300) # هەموو ٥ خولەک جارێک پشکنین دەکات

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

bot.polling(none_stop=True)
