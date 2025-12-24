import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

# تنظیم UTF-8 برای خروجی کنسول
sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
# نمایش درست حروف فارسی در خروجی JSON
app.config['JSON_AS_ASCII'] = False

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_market_stats():
    try:
        # درخواست به سایت اصلی
        resp = requests.get("https://bourse-trader.ir/", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # تابع کمکی برای پیدا کردن مقدار بر اساس عنوان (Label)
        def get_value(label):
            td = soup.find("td", string=lambda t: t and label in t)
            if td:
                val_td = td.find_next_sibling("td")
                if val_td:
                    # اگر داخلش لینک <a> بود متن لینک را بگیر، در غیر این صورت متن خود تگ را
                    a = val_td.find("a")
                    return a.get_text(strip=True) if a else val_td.get_text(strip=True)
            return "یافت نشد"

        # استخراج فقط موارد مورد نیاز
        data = {
            "ارزش معاملات خرد": get_value("ارزش معاملات خرد"),
            "ورود پول حقیقی": get_value_by_label("ورود پول حقیقی"),
            "ورود پول صندوق درآمد ثابت": get_value("ورود پول صندوق درآمدثابت"),
            "ورود پول صندوق کالایی": get_value("ورود پول صندوق کالایی")
        }
        return data

    except Exception as e:
        return {"error": f"خطا در دریافت اطلاعات: {str(e)}"}

# --- مسیرهای Flask ---

@app.route("/")
def home():
    return "✅ سرور فعال است. برای دریافت آمار به /fetch بروید."

@app.route("/fetch")
def fetch():
    print("🔄 در حال به‌روزرسانی آمار بورس...")
    results = get_market_stats()
    return jsonify(results)

if __name__ == "__main__":
    # اجرا روی پورت 10000
    app.run(host="0.0.0.0", port=10000)
