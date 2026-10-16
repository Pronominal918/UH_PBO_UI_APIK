
import csv
import os
from models import Produk, FILE_CSV


def muat_data(tampilkan_pesan=True):
    """Membaca produk.csv. Tampilan UI memanggilnya dengan tampilkan_pesan=False."""
    daftar_produk = []

    if not os.path.exists(FILE_CSV):
        if tampilkan_pesan:
            print("File produk.csv tidak ditemukan.")
        return daftar_produk

    with open(FILE_CSV, newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader, None)  # Lewati header pertama

        for row in reader:
            if len(row) < 4:
                continue

            # Lewati header tambahan jika ada
            if row[2].strip().lower() == "harga":
                continue

            try:
                produk = Produk(
                    nama=row[0].strip(),
                    kategori=row[1].strip(),
                    harga=int(row[2].strip()),
                    stok=int(row[3].strip())
                )

                daftar_produk.append(produk)

            except ValueError:
                if tampilkan_pesan:
                    print(f"Data tidak valid, dilewati: {row}")

    return daftar_produk


def tampilkan_produk():
    daftar_produk = muat_data()

    if not daftar_produk:
        print("Tidak ada data produk.")
        return

    print("\n=== DAFTAR PRODUK TOKO ONLINE ===\n")

    print(
        f"{'Nama Produk':25}"
        f"{'Kategori':18}"
        f"{'Harga (Rp)':15}"
        f"{'Stok'}"
    )

    print("-" * 70)

    for produk in daftar_produk:
        print(
            f"{produk.nama:25}"
            f"{produk.kategori:18}"
            f"{produk.harga:<15}"
            f"{produk.stok}"
        )

    print("-" * 70)
    print(f"Total Produk: {len(daftar_produk)}")


def main():
    """Menu teks lama (tetap tersedia, dipakai oleh: python main.py --cli)."""
    while True:
        print("\n=== MENU ===")
        print("1. Tampilkan Produk")
        print("2. Refresh Data")
        print("0. Keluar")

        pilihan = input("Pilih: ")

        if pilihan == "1":
            tampilkan_produk()

        elif pilihan == "2":
            print("Data dimuat ulang...")
            tampilkan_produk()

        elif pilihan == "0":
            print("Program selesai.")
            break

        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    # Dijalankan langsung -> tampilan UI katalog langsung muncul.
    from UI import jalankan
    jalankan("katalog")
