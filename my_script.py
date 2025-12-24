import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

sys.stdout.reconfigure(encoding='utf-8')
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_bourse_trader_data():
    try:
        resp = requests.get("https://bourse-trader.ir/", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # ۱. استخراج آمارهای کلی
        def get_value_by_label(label):
            # جستجوی منعطف‌تر برای متن
            td = soup.find("td", string=lambda t: t and label in t)
            if td:
                val_td = td.find_next_sibling("td")
                if val_td:
                    return val_td.get_text(strip=True)
            return "پیدا نشد"

        stats = {
            "ارزش معاملات خرد": get_value_by_label("ارزش معاملات خرد"),
            "ورود پول حقیقی": get_value_by_label("ورود پول حقیقی"),
            "ورود پول صندوق درآمد ثابت": get_value_by_label("ورود پول صندوق درآمدثابت"),
            "ورود پول صندوق کالایی": get_value_by_label("ورود پول صندوق کالایی")
        }

        # ۲. استخراج جدول (با جستجوی منعطف در تمام جداول)
        top_real_money = []
        # پیدا کردن جدولی که هدر آن شامل "ورود پول حقیقی" باشد
        all_tables = soup.find_all("table")
        for table in all_tables:
            if "ورود پول حقیقی" in table.get_text():
                rows = table.find_all("tr")[1:] # نادیده گرفتن ردیف هدر
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
                break # وقتی جدول پیدا شد خارج شو

        return {"stats": stats, "top_inflow": top_real_money}
    except Exception as e:
        return {"error": str(e)}

def get_traders_arena_data():
    try:
        # استفاده از سشن برای حفظ کوکی‌ها
        session = requests.Session()
        resp = session.get("https://tradersarena.ir/", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # روش اول: جستجو با ID
        target = soup.find(id="transfer_commodity")
        
        # روش دوم (اگر اولی پیدا نشد): جستجو در کل متن صفحه برای یافتن الگوی عدد و B
        if not target:
            # این بخش تلاش می‌کند المانی که کلاس plus دارد و نزدیک به کلمه کالا/commodity هست را بیابد
            target = soup.find("td", {"class": "plus", "id": True}) 
            
        return target.get_text(strip=True) if target else "داده در لایه اول یافت نشد (احتمالا لود با JS)"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/fetch")
def fetch_all():
    return jsonify({
        "bourse_trader_data": get_bourse_trader_data(),
        "traders_arena": {"transfer_commodity": get_traders_arena_data()}
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
