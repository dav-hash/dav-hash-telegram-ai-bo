import telebot
import requests
import time
from google import genai
from google.genai import types

# --- TOKEN & API KEYS ---
# تێبینی: باشترە ئەمانە لە ناو Environment Variables ی Railway دابنێیت
TELEGRAM_TOKEN = "8667282272:AAGx9qoKDCr-2j6JTHW0oRhXXO8_OfBSzas"
GEMINI_API_KEY = "AIzaSyBrOEyTbWQhu5hQKaNNadsW2l0QdmMSHqA"
NEWSDATA_API_KEY = "pub_5171f9c689bb4542880d74e0a73d1bee"

# ڕێکخستنی Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# ڕێکخستنی بۆتی تێلیگرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def analyze_with_gemini(news_text):
    """شیکارکردنی هەواڵەکە بە Gemini"""
    prompt = (
        f"وەک پسپۆڕێکی بازاڕی دراوە ئەلیکترۆنییەکان، ئەم هەواڵە بخوێنەرەوە: '{news_text}'\n"
        "١. کاریگەرییەکەی چییە؟ (ئەرێنی، نەرێنی، یان بێلایەن)\n"
        "٢. ئایا کاتی کڕینە یان فرۆشتن؟\n"
        "٣. بە کوردییەکی زۆر کورت و پوخت وەڵام بدەرەوە. تەنها دەقی سادە بنووسە."
    )

    try:
        # لێرەدا کێشەی 404 چارەسەر کراوە بە دیاریکردنی ناوی ڕاستی مۆدێلەکە
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        
        if response and response.text:
            # لابردنی هێماکانی وەک * یان _ کە تێلیگرام تێک دەدەن
            clean_text = response.text.replace("*", "").replace("_", "").replace("`", "")
            return clean_text
        return "🤖 Gemini وەڵامێکی نەبوو."

    except Exception as e:
        print(f"Gemini Error: {e}")
        return "⚠️ ببورە، کێشەیەک لە شیکردنەوەدا ڕوویدا."

def get_news():
    """هێنانی هەواڵەکان"""
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q=crypto&language=en"
    try:
        response = requests.get(url, timeout=10).json()
        return response.get("results", [])
    except Exception as e:
        print(f"News API Error: {e}")
        return []

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 بۆتەکە چالاک بوو! ئێستا هەواڵەکان و شیکارییەکان وەردەگریت.")
    
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
                        f"📰 هەواڵ: {title}\n\n"
                        f"🔗 لینکی هەواڵ: {link}\n"
                        f"-----------------\n"
                        f"🤖 شیکاری زیرەک:\n{analysis}"
                    )

                    # ناردنی پەیامەکە بەبێ parse_mode بۆ ئەوەی کێشەی Markdown دروست نەبێت
                    bot.send_message(message.chat.id, final_msg)
                    
                    already_sent.add(title)
                    if len(already_sent) > 50:
                        already_sent.clear()
                    
                    time.sleep(5) # کەمێک وەستان بۆ ئەوەی تێلیگرام بلۆکمان نەکات

            time.sleep(300) # پشکنین هەموو ٥ خولەک جارێک
        except Exception as e:
            print(f"Main Loop Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    bot.polling(none_stop=True)
