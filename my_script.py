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

    # ارزش معاملات خرد
    selector_val = "body > div.container-fullwidth.trader_container > div:nth-child(4) > div:nth-child(6) > div.col-xl-3.col-lg-6.col-md-5.col-sm-12.my-2 > div > div > table > tbody > tr:nth-child(4) > td.bl-colu > a"
    elem_val = soup.select_one(selector_val)
    data["ارزش معاملات خرد"] = elem_val.get_text(strip=True) if elem_val else "پیدا نشد"

    # ورود پول حقیقی
    selector_real = "body > div.container-fullwidth.trader_container > div:nth-child(4) > div:nth-child(6) > div.col-xl-3.col-lg-6.col-md-5.col-sm-12.my-2 > div > div > table > tbody > tr:nth-child(11) > td.bl-colu > a"
    elem_real = soup.select_one(selector_real)
    data["ورود پول حقیقی"] = elem_real.get_text(strip=True) if elem_real else "پیدا نشد"

    # ورود پول به صندوق درآمد ثابت
    selector_fixed = "body > div.container-fullwidth.trader_container > div:nth-child(4) > div:nth-child(6) > div.col-xl-3.col-lg-6.col-md-5.col-sm-12.my-2 > div > div > table > tbody > tr:nth-child(12) > td.bl-colu > a"
    elem_fixed = soup.select_one(selector_fixed)
    data["ورود پول صندوق درآمد ثابت"] = elem_fixed.get_text(strip=True) if elem_fixed else "پیدا نشد"

    # ورود پول به صندوق کالایی
    selector_commodity = "body > div.container-fullwidth.trader_container > div:nth-child(4) > div:nth-child(6) > div.col-xl-3.col-lg-6.col-md-5.col-sm-12.my-2 > div > div > table > tbody > tr:nth-child(13) > td.bl-colu > a"
    elem_commodity = soup.select_one(selector_commodity)
    data["ورود پول صندوق کالایی"] = elem_commodity.get_text(strip=True) if elem_commodity else "پیدا نشد"

    # بیشترین ورود پول حقیقی
    selector_top_real = "body > div.container-fullwidth.trader_container > div:nth-child(4) > div:nth-child(10) > div:nth-child(4) > div > div > table > tbody"
    table_real = soup.select_one(selector_top_real)
    if table_real:
        rows = table_real.find_all("tr")
        stocks = [r.get_text(" | ", strip=True) for r in rows]
        data["بیشترین ورود پول حقیقی"] = "\n".join(stocks) if stocks else "داده‌ای نیست"
    else:
        data["بیشترین ورود پول حقیقی"] = "پیدا نشد"

    # بیشترین ورود پول حقوقی
    selector_top_legal = "body > div.container-fullwidth.trader_container > div:nth-child(4) > div:nth-child(10) > div:nth-child(3) > div > div > table > tbody"
    table_legal = soup.select_one(selector_top_legal)
    if table_legal:
        rows = table_legal.find_all("tr")
        stocks = [r.get_text(" | ", strip=True) for r in rows]
        data["بیشترین ورود پول حقوقی"] = "\n".join(stocks) if stocks else "داده‌ای نیست"
    else:
        data["بیشترین ورود پول حقوقی"] = "پیدا نشد"

    # سهامی که از منفی به مثبت رفته‌اند
    selector_turned = "body > div.container-fullwidth.trader_container > div:nth-child(4) > div:nth-child(12) > div:nth-child(3) > div > div > table > tbody"
    table_turned = soup.select_one(selector_turned)
    if table_turned:
        rows = table_turned.find_all("tr")
        stocks = [r.get_text(" | ", strip=True) for r in rows]
        data["سهامی که از منفی به مثبت رفته‌اند"] = "\n".join(stocks) if stocks else "داده‌ای نیست"
    else:
        data["سهامی که از منفی به مثبت رفته‌اند"] = "پیدا نشد"

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
