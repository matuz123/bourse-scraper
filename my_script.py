import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

# ⚡ تنظیم UTF-8 برای خروجی صحیح فارسی در کنسول
sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
# برای اینکه خروجی JSON در مرورگر فارسی بماند و کد نشود
app.config['JSON_AS_ASCII'] = False

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ==========================================
# 1️⃣ تابع استخراج از سایت bourse-trader.ir
# ==========================================
def get_bourse_trader_data():
    try:
        resp = requests.get("https://bourse-trader.ir/", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # الف) استخراج آمارهای کلی
        def get_value_by_label(label):
            td = soup.find("td", string=lambda t: t and label in t)
            if td:
                val_td = td.find_next_sibling("td")
                if val_td:
                    a = val_td.find("a")
                    return a.get_text(strip=True) if a else val_td.get_text(strip=True)
            return "پیدا نشد"

        stats = {
            "ارزش معاملات خرد": get_value_by_label("ارزش معاملات خرد"),
            "ورود پول حقیقی": get_value_by_label("ورود پول حقیقی"),
            "ورود پول صندوق درآمد ثابت": get_value_by_label("ورود پول صندوق درآمدثابت"),
            "ورود پول صندوق کالایی": get_value_by_label("ورود پول صندوق کالایی")
        }

        # ب) استخراج جدول بیشترین ورود پول حقیقی
        top_real_money = []
        header = soup.find("h2", string=lambda t: t and "بیشترین ورود پول حقیقی" in t)
        if header:
            table = header.find_next("table")
            if table and table.find("tbody"):
                rows = table.find("tbody").find_all("tr")
                for r in rows:
                    cols = r.find_all("td")
                    if len(cols) >= 5:
                        top_real_money.append({
                            "نماد": cols[0].get_text(strip=True),
                            "قیمت آخر": cols[1].get_text(strip=True),
                            "خرید حقیقی": cols[2].get_text(strip=True),
                            "حجم": cols[3].get_text(strip=True),
                            "ورود پول": cols[4].get_text(strip=True),
                        })

        return {"stats": stats, "top_inflow": top_real_money}
    except Exception as e:
        return {"error": f"Bourse-Trader Error: {str(e)}"}

# ==========================================
# 2️⃣ تابع استخراج از سایت tradersarena.ir
# ==========================================
def get_traders_arena_data():
    try:
        resp = requests.get("https://tradersarena.ir/", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # استخراج بر اساس ID درخواستی شما
        target = soup.find(id="transfer_commodity")
        return target.get_text(strip=True) if target else "المان یافت نشد"
    except Exception as e:
        return f"TradersArena Error: {str(e)}"

# ==========================================
# 🌐 تنظیمات وب‌سرور Flask
# ==========================================
@app.route("/")
def home():
    return "✅ سرور فعال است. برای دریافت تمام داده‌ها به /fetch بروید."

@app.route("/fetch")
def fetch_all():
    print("🚀 در حال استخراج داده‌ها از هر دو سایت...")
    
    # دریافت داده‌ها
    bourse_data = get_bourse_trader_data()
    arena_commodity = get_traders_arena_data()
    
    # ترکیب نتایج در یک دیکشنری واحد
    final_output = {
        "bourse_trader_data": bourse_data,
        "traders_arena": {
            "transfer_commodity": arena_commodity
        }
    }
    
    print("✅ داده‌ها با موفقیت ترکیب شدند.")
    return jsonify(final_output)

if __name__ == "__main__":
    # پورت 10000 معمولاً برای سرویس‌هایی مثل Render استفاده می‌شود
    app.run(host="0.0.0.0", port=10000)
