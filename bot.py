import telebot
import requests
import time
from google import genai
from google.genai import types

# --- TOKEN & API KEYS ---
TELEGRAM_TOKEN = "8667282272:AAGx9qoKDCr-2j6JTHW0oRhXXO8_OfBSzas"
GEMINI_API_KEY = "AIzaSyBrOEyTbWQhu5hQKaNNadsW2l0QdmMSHqA"
NEWSDATA_API_KEY = "pub_5171f9c689bb4542880d74e0a73d1bee"

# Gemini setup
client = genai.Client(api_key=GEMINI_API_KEY)

# Telegram bot setup
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def analyze_with_gemini(news_text):
    """Analyze crypto news with Gemini"""
    prompt = (
        f"وەک پسپۆڕێکی بازاڕی دراوە ئەلیکترۆنییەکان، ئەم هەواڵە بخوێنەرەوە: '{news_text}'\n"
        "١. کاریگەرییەکەی چییە؟ (ئەرێنی، نەرێنی، یان بێلایەن)\n"
        "٢. ئایا کاتی کڕینە یان فرۆشتن؟\n"
        "٣. بە کوردییەکی زۆر کورت و پوخت وەڵام بدەرەوە. تەنها تێکستی سادە بەکاربهێنە بەبێ هێمای ئەستێرە یان مارکداون."
    )

    try:
        # چارەسەری هەڵەی 404 بە بەکارهێنانی ناوی دروستی مۆدێل
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=300,
                temperature=0.7
            )
        )
        
        if response and response.text:
            # پاککردنەوەی دەقەکە لە هەر هێمایەکی مارکداون کە تێلیگرام تێک دەدات
            return response.text.replace("*", "").replace("_", "").replace("`", "")
        else:
            return "🤖 Gemini وەڵامێکی بەردەستی نەبوو."

    except Exception as e:
        print(f"Gemini Error: {e}")
        return "⚠️ شیکردنەوە بۆ ئەم هەواڵە بەردەست نییە."

def get_news():
    """Get crypto news"""
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q=crypto&language=en"
    try:
        response = requests.get(url, timeout=10).json()
        return response.get("results", [])
    except Exception as e:
        print(f"News API Error: {e}")
        return []

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🚀 بۆتە زیرەکە چالاک بوو!\nهەواڵە نوێیەکانی کریپتۆ لێرە بڵاو دەکرێنەوە."
    )

    already_sent = set()

    while True:
        try:
            news_list = get_news()

            for news in news_list:
                title = news.get("title")
                link = news.get("link")

                if title and title not in already_sent:
                    # ئەنجامدانی شیکاری
                    analysis = analyze_with_gemini(title)

                    # دروستکردنی پەیامەکە بە تێکستێکی سادە
                    final_msg = (
                        f"📰 هەواڵ: {title}\n\n"
                        f"🔗 لینکی هەواڵ: {link}\n"
                        f"-----------------\n"
                        f"🤖 شیکاری زیرەک:\n{analysis}"
                    )

                    # ناردنی پەیامەکە بەبێ parse_mode بۆ ئەوەی تووشی Crash نەبێت
                    bot.send_message(message.chat.id, final_msg)

                    already_sent.add(title)

                    # پاراستنی میمۆری (ئەگەر لیستەکە زۆر بوو پاکی بکەرەوە)
                    if len(already_sent) > 50:
                        already_sent.clear()

                    # کەمێک وەستان لە نێوان پەیامەکان
                    time.sleep(5)

            # پشکنین هەموو ٥ خولەک جارێک
            time.sleep(300)

        except Exception as e:
            print(f"Main Loop Error: {e}")
            time.sleep(60)

# دەستپێکردنی بۆتەکە
if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
