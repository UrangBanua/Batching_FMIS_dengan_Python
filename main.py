import time
import json
import locale
import pickle
import getpass
import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from colorama import Fore, Style

# Set lokalisasi atau regional ke Indonesia
locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
kduser='akuntansiBPKAD'

def proporsiAnggaran(caption):
    # Header Json
    headers_json = {
        'Accept: application/json'
        'Connection: keep-alive'
        'Sec-Fetch-Mode: cors'
        'Sec-Fetch-Site: same-origin'
    }
    print(Fore.BLUE + '\n~ mulai coba ambil data Anggaran' + Style.RESET_ALL)
    # Mengirim GET request ke halaman setelah login
    response = session.get(urlserver + '/dashboard/get-data-anggaran', stream=True)
    loadingPage('Fetching Data Anggaran ')
    # Parsing data JSON
    data_json = json.loads(response.text)
    try:    
        # Menampilkan data yang diinginkan
        r_anggaran = data_json['data']
        # Membaca data JSON sebagai DataFrame menggunakan Pandas
        df = pd.DataFrame(r_anggaran)
        # Mengonversi kolom 'Harga' dari string ke float
        df['total_anggaran'] = df['total_anggaran'].astype('Float64')
        df['total_realisasi'] = df['total_realisasi'].astype('Float64')
        # Menghitung proporsi realisasi anggaran
        df['proporsi'] = df['total_realisasi'] / df['total_anggaran']
        #.apply(lambda x: locale.currency(x, grouping=True))
        # Mengatur opsi tampilan angka desimal
        pd.options.display.float_format = locale.currency
        # Mengurutkan data berdasarkan proporsi secara menurun
        df_sorted = df.sort_values(by='proporsi', ascending=True)
        subset_df = df_sorted[['nmskpd', 'total_anggaran', 'persen_realisasi', 'persen_sisa']]
        print(Fore.LIGHTGREEN_EX + '')
        print(caption)
        # Menampilkan DataFrame ke output CLI
        print(subset_df)
        print('' + Style.RESET_ALL)

    except NameError:
        print(Fore.LIGHTYELLOW_EX + "Variabel x tidak didefinisikan" + Style.RESET_ALL)
    except ValueError:
        print(Fore.LIGHTYELLOW_EX + "Anda harus memasukkan angka" + Style.RESET_ALL)
    except requests.exceptions.RequestException as e:
        print(Fore.RED + 'Terjadi kesalahan pada permintaan:' + Style.RESET_ALL, str(e))
    except Exception as e:
        print(Fore.RED + '! Terjadi kesalahan lain >> logout/n' + Style.RESET_ALL, str(e))
    finally:
        print(Fore.LIGHTMAGENTA_EX + 'Selesai...' + Style.RESET_ALL)

# ~~~~~~~~~~~~~~~~~~~~ fungsi MENU UTAMA ~~~~~~~~~~~~~~~~~~~~
def main_menu():
    print("\n~~~~~~~~~~~~~~~~~~~~ Menu Utama ~~~~~~~~~~~~~~~~~~~~")
    print("1. Proporsi Anggaran vs Realisasi")
    print("2. BUD - Review")
    print("3. Tatausaha - Validasi")
    print("4. Bendahara - Review")
    print("5. Akuntansi - Posting")
    print("6. Akuntansi - Laporan")
    print("9. Keluar")

    choice = input("Masukkan pilihan Anda: ")

    if choice == "1":
        proporsiAnggaran('[ Proporsi Anggaran Terhadap Realisasi ]')
    elif choice == "2":
        print("menu 2")
    elif choice == "3":
        print("menu 3")
    elif choice == "4":
        print("menu 4")
    elif choice == "5":
        print("menu 5")
    elif choice == "6":
        print("menu 6")
    elif choice == "9":
        print("Terima kasih telah menggunakan program ini. Sampai jumpa!")
        return
    else:
        print("Pilihan tidak valid. Silakan masukkan pilihan yang benar.")

    return_to_menu()

# ~~~~~~~~~~~~~~~~~~~~ Fungsi kembali ke menu awal ~~~~~~~~~~~~~~~~~~~~ 
def return_to_menu():
    print("\n")
    choice = input("Ketik 'menu' untuk kembali ke menu utama atau 'keluar' untuk keluar: ")
    
    if choice.lower() == "menu":
        main_menu()
    elif choice.lower() == "keluar":
        print("Terima kasih telah menggunakan program ini. Sampai jumpa!")
        exit()
    else:
        print("Pilihan tidak valid. Silakan masukkan pilihan yang benar.")
        return_to_menu()

# ~~~~~~~~~~~~~~~~~~~~ Fungsi untuk menyimpan session cookies ke file ~~~~~~~~~~~~~~~~~~~~
def save_cookies(session, filename):
    with open(filename, 'wb') as f:
        pickle.dump(session.cookies, f)

# ~~~~~~~~~~~~~~~~~~~~ Fungsi untuk memuat session cookies dari file ~~~~~~~~~~~~~~~~~~~~
def load_cookies(session, filename):
    try:
        with open(filename, 'rb') as f:
            session.cookies.update(pickle.load(f))
    except FileNotFoundError:
        print(Fore.RED + '! File Session tidak ditemukan' + Style.RESET_ALL)

# ~~~~~~~~~~~~~~~~~~~~ fungsi loadingPage ~~~~~~~~~~~~~~~~~~~~
def loadingPage(caption):
    # Mengambil panjang konten respons
    content_length = response.headers.get('content-length')
    if content_length is None:
        content_length = len(response.content)

    # Inisialisasi tqdm dengan total berdasarkan panjang konten
    with tqdm(total=content_length, desc=caption, unit='B', unit_scale=True, ncols=70, bar_format='{desc}: |{bar}| {percentage:3.0f}%') as pbar:
        # Membaca dan menunggu respon
        for chunk in response.iter_content(1024):
            # Menggunakan fungsi sleep untuk simulasi waiting response
            time.sleep(0.05)
            pbar.set_postfix_str('waiting response...')
            pbar.update(len(chunk))

# ~~~~~~~~~~~~~~~~~~~~ fungsi logout ~~~~~~~~~~~~~~~~~~~~
def logout():    
    response = session.post(urlserver + '/logout')
    loadingPage('Logout... ')

# Buat session
print(Fore.BLUE + '~ memuat sesi awal' + Style.RESET_ALL)
session = requests.Session()
# Muat cookies jika ada
load_cookies(session, 'cookies.pkl')
# promt input parameter server login
urlserver = input('UrlServer :(default FMIS Kab. HST) ') or 'https://hulusungaitengahkab.fmis.id/2023'
# Mengirim GET request ke halaman sebelum login
response = session.get(urlserver)
# Parsing halaman dengan BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')
# Mendapatkan token dari halaman sebelum login
token = soup.find('input', {'name': '_token'})['value']
print(Fore.GREEN + '~ token didapatkan:', token + ' \n' + Style.RESET_ALL)

# Pengecekan apakah sudah langsung terpindah ke halaman dashboard
print(Fore.BLUE + '~ cek session apakah expired/tidak\n' + Style.RESET_ALL)
if response.status_code == 200 and '/dashboard' in response.url:
    print(Fore.GREEN + 'Halaman langsung terpindah ke Dashboard' + Style.RESET_ALL)
    # tambah code selanjutnya
else:
    print(Fore.BLUE + '~ session sudah expired, login dulu !' + Style.RESET_ALL)
    # promt input parameter server login
    kduser = input('Username  :(default akuntansiBPKAD) ') or 'akuntansiBPKAD'
    password = getpass.getpass('Password  : ')
    while not password:
        print(Fore.RED + '! Password tidak boleh kosong' + Style.RESET_ALL)
        password = getpass.getpass('Password  : ')
    print('')
    # URL halaman login
    login_url = urlserver + '/login'
    # Data login (sesuaikan dengan field input pada halaman login)
    payload_login = {
        '_token': token,
        'kduser': kduser,
        'password': password,
        'tahun': '2023'
    }
    # Header login
    headers_login = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    print(Fore.BLUE + '~ mulai coba login' + Style.RESET_ALL)
    # Mengirim POST request untuk login
    response = session.post(login_url, data=payload_login, headers=headers_login, stream=True)
    loadingPage('Logging in ')
    # Cek apakah login berhasil
    if response.status_code == 200:
        print(Fore.GREEN + 'Login berhasil' + Style.RESET_ALL,' :D\n')
        save_cookies(session, 'cookies.pkl')
    else:
        print(Fore.RED + '! Login gagal' + Style.RESET_ALL)
        print('! Respon HTTP:', response.status_code)
        print('! Pesan Kesalahan:', response.text)

# Menampilkan User dan Menu Utama
print(Fore.BLUE + '** Selamat Datang ' + kduser + ' **'  + Style.RESET_ALL)
main_menu()


    #logout()