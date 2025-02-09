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
        "reset": "\033[0m"  # Untuk mengembalikan warna ke default
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
        print(color_text("API Key disimpan dalam file.", "green"))

    return api_key

def create_order(api_key, service_id, operator):
    try:
        quantity = int(input(color_text("Masukkan jumlah nomor yang ingin dipesan: ", "green")))
    except ValueError:
        print(color_text("Jumlah order harus berupa angka positif.", "red"))
        return
    if quantity <= 0:
        print(color_text("Jumlah order harus berupa angka positif.", "red"))
        return

    success_numbers = []

    for _ in range(quantity):
        url = f"https://virtusim.com/api/json.php?api_key={api_key}&action=order&service={service_id}&operator={operator}"
        response = requests.get(url)

        if response.status_code != 200:
            print(color_text(f"Error: {response.text}", "red"))
            continue

        result = response.json()
        if result.get("status"):
            success_numbers.append(result["data"].get("number"))
        else:
            print(color_text(f"Order Gagal: {result['data'].get('msg')}", "red"))

    if success_numbers:
        print(color_text("Order Berhasil:", "green"))
        for number in success_numbers:
            print(color_text(number, "green"))

def get_active_orders(api_key):
    url = f"https://virtusim.com/api/json.php?api_key={api_key}&action=active_order"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(color_text("Gagal mengambil data order aktif.", "red"))
        return []

    result = response.json()
    if result.get("status") and result.get("data"):
        return result["data"]
    else:
        print(color_text("Orderan kosong bro", "red"))
        return []

def resend_order(api_key, order_id):
    """
    Fungsi untuk mengirim ulang order berdasarkan ID order.
    """
    url = f"https://virtusim.com/api/json.php?api_key={api_key}&action=set_status&id={order_id}&status=3"
    response = requests.get(url)
    result = response.json()

    if result.get("status"):
        print(color_text(f"Order {order_id} berhasil diresend.", "green"))
    else:
        print(color_text(f"Gagal resend order {order_id}: {result['data'].get('msg')}", "red"))


def monitor_sms(api_key, interval=5, resend_interval=120):
    """
    Memantau SMS terbaru dan melakukan resend pada order yang sudah menerima SMS setiap 2 menit.
    """
    print(color_text("Memulai pemantauan SMS terbaru...", "green"))
    latest_sms = []
    number_index = {}
    last_resend_time = time.time()

    while True:
        # Ambil order aktif
        orders = get_active_orders(api_key)

        if orders:
            for order in orders:
                # Periksa jika order sudah menerima SMS
                if order.get("status") == "Otp Diterima" and order.get("sms"):
                    # Tampilkan detail SMS baru
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

                        print(color_text("SMS Baru Diterima:", "green"))
                        print(color_text(f"Nomor Urut: {sms_data['order_number']}", "cyan"))
                        print(color_text(f"Nomor: {sms_data['number']}", "cyan"))
                        print(color_text(f"OTP: {sms_data['otp']}", "green"))
                        print(color_text(f"Service: {sms_data['service_name']}", "green"))
                        print(color_text("------------------------------------", "green"))

                    # Resend order jika waktu resend terpenuhi
                    if time.time() - last_resend_time >= resend_interval:
                        print(color_text(f"Resend Order untuk nomor {order['number']}...", "green"))
                        resend_order(api_key, order["id"])

            # Perbarui waktu terakhir melakukan resend
            if time.time() - last_resend_time >= resend_interval:
                last_resend_time = time.time()

        else:
            print(color_text("Tidak ada SMS baru. Memeriksa lagi...", "red"))
            number_index.clear()

        time.sleep(interval)



def cancel_or_resend_order(api_key):
    orders = get_active_orders(api_key)

    if not orders:
        print(color_text("Tidak ada order aktif untuk dikelola.", "red"))
        return

    # Tampilkan daftar order
    print(color_text("Daftar Order Aktif:", "green"))
    for idx, order in enumerate(orders, 1):
        print(color_text(f"{idx}. ID: {order['id']} | Nomor: {order['number']}", "green"))

    # Meminta input untuk rentang dan aksi
    choice = input(color_text("Masukkan nomor order yang ingin dikelola (contoh 1-3): ", "green")).strip()
    action = input(color_text("Apa yang ingin Anda lakukan pada order tersebut:\n1. Cancel\n2. Resend\nPilihan (1/2): ", "green")).strip()

    # Validasi awal input
    valid_actions = {"1", "2"}
    if action not in valid_actions:
        print(color_text("Pilihan aksi tidak valid.", "red"))
        return

    try:
        # Validasi dan parsing rentang input
        start, end = map(int, choice.split('-'))
        if start < 1 or end > len(orders) or start > end:
            raise ValueError("Rentang tidak valid.")
        selected_orders = orders[start - 1:end]
    except ValueError:
        print(color_text("Rentang atau format input tidak valid.", "red"))
        return

    # Aksi batch pada order yang dipilih
    urls = []
    for order in selected_orders:
        order_id = order["id"]
        status = "2" if action == "1" else "3"  # Cancel = 2, Resend = 3
        urls.append(f"https://virtusim.com/api/json.php?api_key={api_key}&action=set_status&id={order_id}&status={status}")

    # Kirim semua request dalam batch
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            if result.get("status"):
                action_text = "dibatalkan" if action == "1" else "diresend"
                print(color_text(f"Order {result['data']['id']} berhasil {action_text}.", "green"))
            else:
                print(color_text(f"Gagal memproses order: {result['data'].get('msg')}", "red"))
        else:
            print(color_text(f"Gagal mengakses API untuk URL: {url}", "red"))

    print(color_text("Proses selesai untuk semua order yang dipilih.", "green"))

def main_menu(api_key, service_id, operator):
    while True:
        # Tampilkan judul saat program dimulai
        clear_screen()
        display_title()
        print(color_text("\n✨ Selamat datang di Menu Utama! ✨", "cyan"))  # Warna cyan untuk judul
        print(color_text("1. 📱 Permintaan Nomor Baru yang Lebih Personal", "blue"))  # Warna biru untuk opsi
        print(color_text("2. 🔍 Periksa Status Order yang Sedang Berjalan", "blue"))  # Warna biru untuk opsi
        print(color_text("3. 📦 Manajemen Order Anda dengan Mudah", "blue"))  # Warna biru untuk opsi
        print(color_text("4. 📩 Pemantauan SMS Masuk yang Real-Time", "blue"))  # Warna biru untuk opsi
        print(color_text("5. ❌ Keluar dari Program dengan Tenang", "red"))  # Warna merah untuk opsi keluar

        choice = input(color_text("💬 Silakan pilih opsi (1-5) dengan bijak: ", "green"))  # Warna hijau untuk prompt input



        if choice == "1":
            print(color_text("📱 Pilih Layanan Operator:", "green"))
            print(color_text("1️⃣ GOJEK 🚗 - Layanan transportasi cepat dan mudah", "green"))
            print(color_text("2️⃣ WHATSAPP 💬 - Layanan pesan instan yang terhubung dengan nomor baru", "green"))
            choice_service = input(color_text("🔢 Pilih Layanan (1/2): ", "green"))
            if choice_service == "1":
                service_id = "305"
            elif choice_service == "2":
                service_id = "6155"

            create_order(api_key, service_id, operator)
            backmenu = input(color_text("🔙 Kembali ke menu utama? (y/n): ", "green"))
            if backmenu == "y":
                continue
            else:
                break
        elif choice == "2":
            orders = get_active_orders(api_key)
            if orders:
                for order in orders:
                    print(color_text(f"🆔 ID: {order['id']} | 📞 Nomor: {order['number']} | 📊 Status: {order['status']} | 🗓 Tanggal: {order['date']}", "green"))
            else:
                print(color_text("❗ Tidak ada pesanan aktif saat ini.", "red"))
            backmenu = input(color_text("🔙 Kembali ke menu utama? (y/n): ", "green"))
            if backmenu == "y":
                continue
            else:
                break
        elif choice == "3":
            cancel_or_resend_order(api_key)
            backmenu = input(color_text("🔙 Kembali ke menu utama? (y/n): ", "green"))
            if backmenu == "y":
                continue
            else:
                break
        elif choice == "4":
            monitor_sms(api_key)
            backmenu = input(color_text("🔙 Kembali ke menu utama? (y/n): ", "green"))
            if backmenu == "y":
                continue
            else:
                break
        elif choice == "5":
            print(color_text("👋 Sampai jumpa! Terima kasih telah menggunakan layanan kami. Semoga hari Anda menyenankan! 🌟", "yellow"))
            break
        else:
            print(color_text("❌ Pilihan tidak valid. Harap pilih antara 1-5.", "red"))


# Ambil API Key
service_id = ""
default_operator = "any"
api_key = get_api_key()

# Jalankan menu utama
main_menu(api_key, service_id, default_operator)
