import requests
import time
import os

def color_text(text, color):
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m"
    }
    return f"{colors[color]}{text}{colors['reset']}"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def display_title():
    print(color_text("==========================================", "green"))
    print(color_text("          🔥 BIMA PROJECT 🔥          ", "yellow"))
    print(color_text("   # Your Virtual Number Manager #   ", "cyan"))
    print(color_text("         Owner: @bima.gunawan         ", "magenta"))
    print(color_text("==========================================", "green"))

def get_api_key():
    api_key_file = "apivirtu.txt"
    if os.path.exists(api_key_file):
        with open(api_key_file, "r") as file:
            api_key = file.read().strip()
    else:
        api_key = input(color_text("Masukkan API Key Anda: ", "green")).strip()
        with open(api_key_file, "w") as file:
            file.write(api_key)
        print(color_text("✅ API Key disimpan dalam file.", "green"))
    return api_key

def create_order(api_key, service_id, operator):
    try:
        quantity = int(input(color_text("Masukkan jumlah nomor yang ingin dipesan: ", "green")))
    except ValueError:
        print(color_text("Jumlah order harus berupa angka positif.", "red"))
        return
    if quantity <= 0:
        print(color_text("Jumlah order harus lebih dari 0.", "red"))
        return

    success_numbers = []
    for _ in range(quantity):
        url = f"https://virtusim.com/api/json.php?api_key={api_key}&action=order&service={service_id}&operator={operator}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(color_text(f"❌ Error: {response.text}", "red"))
            continue
        
        result = response.json()
        if result.get("status"):
            success_numbers.append(result["data"].get("number"))
        else:
            print(color_text(f"⚠️ Order Gagal: {result['data'].get('msg')}", "red"))

    if success_numbers:
        print(color_text("✅ Order Berhasil! Berikut nomor yang berhasil dipesan:", "green"))
        for number in success_numbers:
            print(color_text(f"📱 {number}", "blue"))

def get_active_orders(api_key):
    url = f"https://virtusim.com/api/json.php?api_key={api_key}&action=active_order"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(color_text("❌ Gagal mengambil data order aktif.", "red"))
        return []
    
    result = response.json()
    if result.get("status") and result.get("data"):
        return result["data"]
    else:
        print(color_text("⚠️ Tidak ada order aktif saat ini.", "red"))
        return []

def monitor_sms(api_key, interval=5):
    print(color_text("📡 Memulai pemantauan SMS terbaru...", "green"))
    latest_sms = []
    number_index = {}

    while True:
        orders = get_active_orders(api_key)

        if orders:
            for order in orders:
                if order.get("status") == "Otp Diterima" and order.get("sms"):
                    sms_data = {
                        "number": order.get("number"),
                        "otp": order.get("otp"),
                        "sms": order.get("sms"),
                        "service_name": order.get("service_name")
                    }

                    if sms_data["number"] not in number_index:
                        number_index[sms_data["number"]] = len(number_index) + 1

                    sms_data["order_number"] = number_index[sms_data["number"]]

                    if sms_data not in latest_sms:
                        latest_sms.append(sms_data)
                        latest_sms.sort(key=lambda x: x["order_number"])
                        
                        print(color_text("📩 SMS Baru Diterima!", "green"))
                        print(color_text(f"📌 Nomor Urut: {sms_data['order_number']}", "cyan"))
                        print(color_text(f"📌 Nomor: {sms_data['number']}", "cyan"))
                        print(color_text(f"🔑 Kode OTP: {sms_data['otp']}", "green"))
                        print(color_text(f"🔹 Layanan: {sms_data['service_name']}", "blue"))
                        print(color_text("------------------------------------", "green"))
        else:
            print(color_text("🚀 Tidak ada SMS baru. Memeriksa lagi...", "yellow"))
            number_index.clear()
        
        time.sleep(interval)

if __name__ == "__main__":
    clear_screen()
    display_title()
    api_key = get_api_key()
    monitor_sms(api_key)
