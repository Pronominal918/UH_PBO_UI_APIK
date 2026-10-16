
import csv
import os
import re
from models import Produk, FILE_CSV


def _ke_angka(teks, label, galat, kunci):
    """Ubah teks jadi bilangan bulat >= 0. Jika salah, isi galat[kunci]."""
    teks = (teks or "").strip().replace(".", "")  # '75.000' dianggap 75000

    if not teks:
        galat[kunci] = f"{label} wajib diisi"
        return None

    if not re.fullmatch(r"-?\d+", teks):
        galat[kunci] = f"{label} harus berupa angka bulat"
        return None

    nilai = int(teks)
    if nilai < 0:
        galat[kunci] = f"{label} tidak boleh negatif"
        return None

    return nilai


def periksa_produk(nama, kategori, harga_input, stok_input):
    """Validasi data dari form UI.

    Mengembalikan (produk, galat). Jika ada yang salah, produk = None dan
    galat berisi pesan per kolom: {'nama': ..., 'kategori': ..., 'harga': ..., 'stok': ...}
    """
    nama = (nama or "").strip()
    kategori = (kategori or "").strip()
    galat = {}

    if not nama:
        galat["nama"] = "Nama produk wajib diisi"
    if not kategori:
        galat["kategori"] = "Kategori wajib diisi"

    harga = _ke_angka(harga_input, "Harga", galat, "harga")
    stok = _ke_angka(stok_input, "Stok", galat, "stok")

    if galat:
        return None, galat

    return Produk(nama, kategori, harga, stok), {}


def simpan_ke_csv(produk):
    """Menambahkan satu produk ke akhir produk.csv (header dibuat jika file baru)."""
    file_exists = os.path.exists(FILE_CSV) and os.path.getsize(FILE_CSV) > 0
    perlu_baris_baru = False

    if file_exists:
        with open(FILE_CSV, "rb") as file:
            file.seek(-1, os.SEEK_END)
            perlu_baris_baru = file.read(1) not in (b"\n", b"\r")

    with open(FILE_CSV, "a", newline="", encoding="utf-8") as file:
        if perlu_baris_baru:
            file.write("\r\n")

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Nama", "Kategori", "Harga", "Stok"])

        writer.writerow(produk.to_list())


def simpan_produk():
    print("\n=== TAMBAH DATA PRODUK ===")

    nama = input("Nama produk : ").strip()
    kategori = input("Kategori    : ").strip()
    harga_input = input("Harga (Rp)  : ").strip()
    stok_input = input("Stok        : ").strip()

    if not nama or not kategori or not harga_input or not stok_input:
        print("\n[PERINGATAN] Semua kolom harus diisi!\n")
        return

    try:
        harga = int(harga_input)
        stok = int(stok_input)

        if harga < 0 or stok < 0:
            print("\n[PERINGATAN] Harga dan stok tidak boleh negatif!\n")
            return

    except ValueError:
        print("\n[PERINGATAN] Harga dan stok harus berupa angka!\n")
        return

    produk = Produk(nama, kategori, harga, stok)
    simpan_ke_csv(produk)

    print("\n[BERHASIL] Produk berhasil ditambahkan.\n")


def main():
    """Menu teks lama (tetap tersedia, dipakai oleh: python main.py --cli)."""
    while True:
        print("=== MENU TAMBAH PRODUK ===")
        print("1. Tambah Produk")
        print("0. Keluar")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            simpan_produk()

        elif pilihan == "0":
            print("Program selesai.")
            break

        else:
            print("Pilihan tidak valid.\n")


if __name__ == "__main__":
    # Dijalankan langsung -> tampilan UI form "Tambah produk" langsung muncul.
    from UI import jalankan
    jalankan("tambah")
