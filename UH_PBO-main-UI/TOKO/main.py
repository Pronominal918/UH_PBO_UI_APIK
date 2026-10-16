
"""
TOKO ONLINE - titik awal program.

Cara menjalankan:
    python main.py            -> tampilan UI (file UI.py) langsung muncul
    python main.py --cli      -> menu teks versi lama
"""

import sys

import tambah_produk
import tampil_produk


# ======================================================================
#  MENU TEKS LAMA (dipertahankan, dipanggil dengan: python main.py --cli)
# ======================================================================

def buka_tambah_produk():
    tambah_produk.main()


def buka_tampil_produk():
    tampil_produk.main()


def menu_utama():
    while True:
        print("\n" + "=" * 40)
        print(" SISTEM TOKO ONLINE ".center(40, "="))
        print("=" * 40)
        print("1. Tambah Produk")
        print("2. Tampilkan Produk")
        print("0. Keluar")
        print("=" * 40)

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            buka_tambah_produk()

        elif pilihan == "2":
            buka_tampil_produk()

        elif pilihan == "0":
            print("Terima kasih telah menggunakan toko online.")
            break

        else:
            print("Pilihan tidak valid!")


if __name__ == "__main__":
    if "--cli" in sys.argv:
        menu_utama()
    else:
        from UI import jalankan
        jalankan("katalog")
