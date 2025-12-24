import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

# ⚡ تنظیم UTF-8 برای خروجی فارسی
sys.stdout.reconfigure(encoding='utf-8')

# ========================
# 📌 تابع استخراج داده‌ها از سایت bourse-trader.ir
# ========================
def fetch_from_bourse_trader():
    try:
        resp = requests.get("https://bourse-trader.ir/", timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print("❌ خطا در اتصال به bourse-trader.ir:", e)
        return {"خطا": "اتصال برقرار نشد"}

    soup = BeautifulSoup(resp.text, "html.parser")
    data = {}

    def get_value_by_label(label):
        td = soup.find("td", string=lambda t: t and label in t)
        if not td:
            return "پیدا نشد"
        val_td = td.find_next_sibling("td")
        if not val_td:
            return "پیدا نشد"
        a = val_td.find("a")
        return a.get_text(strip=True) if a else val_td.get_text(strip=True)

    data["ارزش معاملات خرد"] = get_value_by_label("ارزش معاملات خرد")
    data["ورود پول حقیقی"] = get_value_by_label("ورود پول حقیقی")
    data["ورود پول صندوق درآمد ثابت"] = get_value_by_label("ورود پول صندوق درآمدثابت")
    data["ورود پول صندوق کالایی"] = get_value_by_label("ورود پول صندوق کالایی")

    return data
    
def fetch_top_real_money(soup):
    data = []
    
    # پیدا کردن تیبل مربوط به بیشترین ورود پول حقیقی
    header = soup.find("h2", string=lambda t: t and "بیشترین ورود پول حقیقی" in t)
    if not header:
        return ["پیدا نشد"]

    table = header.find_next("table")
    if not table:
        return ["پیدا نشد"]

    tbody = table.find("tbody")
    if not tbody:
        return ["پیدا نشد"]

    rows = tbody.find_all("tr")
    
    for r in rows:
        cols = r.find_all("td")
        if len(cols) < 5:
            continue
        
        data.append({
            "نماد": cols[0].get_text(strip=True),
            "قیمت آخر": cols[1].get_text(strip=True),
            "خرید حقیقی": cols[2].get_text(strip=True),
            "حجم": cols[3].get_text(strip=True),
            "ورود پول": cols[4].get_text(strip=True),
        })

    return data
    


# ========================
# 🌐 وب‌سرور Flask
# ========================
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ سرور فعال است. برای دریافت داده‌ها به /fetch بروید."

@app.route("/fetch")
def fetch_data():
    print("🚀 درخواست جدید برای گرفتن داده‌ها دریافت شد...")
    data = fetch_from_bourse_trader()
    print("✅ داده‌ها استخراج شدند")
    return jsonify(data)  # برمی‌گردونه به صورت JSON

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
