
import os

# produk.csv selalu dicari di folder yang sama dengan file ini,
# jadi program bisa dijalankan dari folder mana pun.
FILE_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "produk.csv")


def format_rupiah(angka):
    """75000 -> 'Rp 75.000'"""
    return "Rp " + f"{angka:,}".replace(",", ".")


class Produk:
    def __init__(self, nama, kategori, harga, stok):
        self.nama = nama
        self.kategori = kategori
        self.harga = harga
        self.stok = stok

    def to_list(self):
        return [self.nama, self.kategori, self.harga, self.stok]

    def __str__(self):
        return f"{self.nama} ({self.kategori}) - Rp{self.harga} - Stok: {self.stok}"


class Pelanggan:
    def __init__(self, id_pelanggan, nama, no_hp, alamat):
        self.id = id_pelanggan
        self.nama = nama
        self.no_hp = no_hp
        self.alamat = alamat

    def to_list(self):
        return [self.id, self.nama, self.no_hp, self.alamat]

    def __str__(self):
        return f"{self.nama} ({self.id}) - {self.no_hp}"
