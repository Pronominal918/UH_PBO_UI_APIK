
"""
UI.py - seluruh tampilan (antarmuka) TOKO ONLINE, memakai Tkinter bawaan Python.
Dibuka dari main.py, atau langsung: python UI.py
"""

import re
import sys
import zlib

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import font as tkfont
except ImportError:  # Python tanpa Tkinter
    tk = None

import tambah_produk
import tampil_produk
from models import Produk, format_rupiah


# ======================================================================
#  TEMA: warna, ukuran, font
# ======================================================================

INK = "#12263F"          # biru tua: navbar & banner
INK_HOVER = "#1F3B5F"
SOFT = "#9FB3CC"         # teks lembut di atas biru tua
PAGE = "#F3F6FA"         # latar halaman
PUTIH = "#FFFFFF"
GARIS = "#DCE3ED"
BAYANG = "#E3E9F2"
TEKS2 = "#5B6B82"        # teks sekunder
KUNING = "#FFC233"       # label harga & tombol utama
KUNING_GELAP = "#F2AD0C"
HIJAU = "#14916B"
ORANYE = "#E8710A"
MERAH = "#D93B3B"
ABU = "#9AA6B8"
ABU_TAG = "#D3DAE5"
FOKUS = "#2F6FED"

WARNA_KATEGORI = {
    "pakaian": "#2F6FED", "baju": "#2F6FED", "kaos": "#2F6FED", "fashion": "#2F6FED",
    "sepatu": "#F26B3A", "sandal": "#F26B3A",
    "tas": "#0E9F8E", "ransel": "#0E9F8E",
    "elektronik": "#7C5CFA", "gadget": "#7C5CFA",
    "aksesoris": "#E0488B", "jam": "#E0488B",
    "makanan": "#E5484D", "minuman": "#E5484D", "buah": "#E5484D",
}
WARNA_CADANGAN = ["#2F6FED", "#F26B3A", "#0E9F8E", "#7C5CFA", "#E0488B", "#2E8B57", "#0D8BB8", "#C2410C"]

IKON_KATEGORI = [
    ("kaos", ("pakaian", "baju", "kaos", "fashion", "celana", "jaket")),
    ("sepatu", ("sepatu", "sandal", "sneaker")),
    ("tas", ("tas", "ransel", "koper")),
    ("headset", ("elektronik", "gadget", "audio", "headset")),
    ("jam", ("aksesoris", "jam", "perhiasan")),
    ("apel", ("makanan", "minuman", "snack", "buah", "kuliner")),
]

CARD_W, CARD_H = 232, 282   # ukuran kartu produk (satuan desain)
TILE_W, TILE_H = 88, 124    # ukuran tombol kategori
GAP = 20

SCALE = 1.0                 # skala layar (diisi saat program mulai)
F = {}                      # kumpulan font (diisi saat program mulai)


def px(n):
    """Ubah ukuran desain menjadi piksel sesuai skala layar."""
    return int(round(n * SCALE)) if n else 0


def siapkan_tema(root):
    global SCALE
    SCALE = 1.0
    if sys.platform != "darwin":
        try:
            SCALE = min(3.0, max(1.0, root.winfo_fpixels("1i") / 96.0))
        except Exception:
            SCALE = 1.0

    keluarga = set(tkfont.families(root))
    nama = next((f for f in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter", "Roboto",
                             "Ubuntu", "Noto Sans", "DejaVu Sans", "Arial") if f in keluarga),
                "Helvetica")
    tambah = 3 if sys.platform == "darwin" else 0

    def buat(ukuran, tebal=False):
        return tkfont.Font(root=root, family=nama, size=ukuran + tambah,
                           weight="bold" if tebal else "normal")

    F.update({
        "brand": buat(15, True), "judul": buat(22, True), "h2": buat(13, True),
        "body": buat(10), "body_b": buat(10, True), "input": buat(11),
        "kecil": buat(9), "kecil_b": buat(9, True),
        "nama": buat(11, True), "harga": buat(11, True),
        "tile": buat(9, True), "tile_k": buat(8),
        "tombol": buat(10, True), "toast": buat(10, True),
    })


# ======================================================================
#  ALAT GAMBAR (kanvas)
# ======================================================================

def campur(hex_warna, rasio, dengan="#FFFFFF"):
    """Campur dua warna. rasio=0 -> warna asli, 1 -> 'dengan'."""
    a = [int(hex_warna[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(dengan[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * rasio) for x, y in zip(a, b))


def rrect(c, x0, y0, x1, y1, r=12, **kw):
    """Persegi panjang bersudut membulat."""
    r = max(0, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    titik = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
             x1, y1 - r, x1, y1, x1 - r, y1, x0 + r, y1,
             x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
    return c.create_polygon(titik, smooth=True, splinesteps=12, **kw)


def skala(c):
    """Perbesar semua gambar di kanvas sesuai skala layar (untuk layar resolusi tinggi)."""
    if SCALE != 1.0:
        c.scale("all", 0, 0, SCALE, SCALE)


def potong(teks, font, lebar):
    """Potong teks dengan '…' bila lebih lebar dari 'lebar' (piksel)."""
    if font.measure(teks) <= lebar:
        return teks
    while teks and font.measure(teks + "…") > lebar:
        teks = teks[:-1]
    return teks.rstrip() + "…"


def bungkus(teks, font, lebar, maks=2):
    """Bagi teks menjadi maksimal 'maks' baris."""
    baris, sekarang = [], ""
    for kata in teks.split():
        kata = potong(kata, font, lebar)
        coba = (sekarang + " " + kata).strip()
        if font.measure(coba) <= lebar:
            sekarang = coba
        else:
            baris.append(sekarang)
            sekarang = kata
    if sekarang:
        baris.append(sekarang)
    if len(baris) > maks:
        baris = baris[:maks - 1] + [potong(" ".join(baris[maks - 1:]), font, lebar)]
    return baris or [""]


def rapikan(teks):
    teks = (teks or "").strip() or "Lainnya"
    return teks[:1].upper() + teks[1:]


def _kata(teks):
    return re.findall(r"\w+", (teks or "").lower())


def warna_kategori(kategori):
    for kata in _kata(kategori):
        if kata in WARNA_KATEGORI:
            return WARNA_KATEGORI[kata]
    return WARNA_CADANGAN[zlib.crc32((kategori or "").lower().encode("utf-8")) % len(WARNA_CADANGAN)]


def jenis_ikon(kategori):
    kata = set(_kata(kategori))
    for jenis, kunci in IKON_KATEGORI:
        if kata & set(kunci):
            return jenis
    return "default"


def gambar_ikon(c, cx, cy, jenis, s, isi, latar, terang, aksen):
    """Ikon produk sederhana, digambar dari bentuk dasar (tanpa file gambar)."""

    def T(*v):
        return [(cx if i % 2 == 0 else cy) + n * s for i, n in enumerate(v)]

    def lebar(n):
        return max(1.0, n * s * SCALE)

    if jenis == "kaos":
        c.create_polygon(T(-14, -30, -6, -30, -4, -24, 4, -24, 6, -30, 14, -30, 32, -17, 24, -3,
                           15, -9, 15, 30, -15, 30, -15, -9, -24, -3, -32, -17), fill=isi, outline="")

    elif jenis == "sepatu":
        c.create_polygon(T(-32, -16, -14, -16, -10, -6, 4, 0, 20, 6, 32, 12, 34, 22, -32, 22),
                         fill=isi, outline="")
        rrect(c, *T(-34, 15, 36, 25), 5 * s, fill=terang, outline="")
        for garis in ((-9, -5, -3, -11), (-3, -1, 3, -7), (3, 3, 9, -3)):
            c.create_line(*T(*garis), fill=aksen, width=lebar(2.5), capstyle="round")

    elif jenis == "tas":
        c.create_arc(*T(-11, -34, 11, 2), start=0, extent=180, style="arc", outline=isi, width=lebar(5))
        rrect(c, *T(-22, -16, 22, 32), 10 * s, fill=isi, outline="")
        rrect(c, *T(-14, 8, 14, 26), 5 * s, fill=terang, outline="")
        c.create_line(*T(-17, -3, 17, -3), fill=aksen, width=lebar(2), capstyle="round")

    elif jenis == "headset":
        c.create_arc(*T(-27, -34, 27, 24), start=0, extent=180, style="arc", outline=isi, width=lebar(6))
        rrect(c, *T(-34, -6, -18, 26), 7 * s, fill=isi, outline="")
        rrect(c, *T(18, -6, 34, 26), 7 * s, fill=isi, outline="")
        rrect(c, *T(-30, 2, -22, 18), 3 * s, fill=terang, outline="")
        rrect(c, *T(22, 2, 30, 18), 3 * s, fill=terang, outline="")

    elif jenis == "jam":
        rrect(c, *T(-10, -36, 10, 36), 4 * s, fill=terang, outline="")
        c.create_rectangle(*T(21, -4, 26, 4), fill=isi, outline="")
        c.create_oval(*T(-21, -21, 21, 21), fill=isi, outline="")
        c.create_oval(*T(-16, -16, 16, 16), fill="", outline=terang, width=lebar(1.5))
        c.create_line(*T(0, 0, 0, -11), fill=aksen, width=lebar(3), capstyle="round")
        c.create_line(*T(0, 0, 8, 5), fill=aksen, width=lebar(3), capstyle="round")

    elif jenis == "apel":
        c.create_oval(*T(-25, -18, 3, 28), fill=isi, outline="")
        c.create_oval(*T(-3, -18, 25, 28), fill=isi, outline="")
        c.create_line(*T(0, -16, 3, -30), fill=isi, width=lebar(3), capstyle="round")
        c.create_polygon(T(4, -29, 17, -35, 19, -24, 8, -22), fill=terang, outline="")

    else:  # tas belanja
        c.create_arc(*T(-10, -30, 10, 6), start=0, extent=180, style="arc", outline=isi, width=lebar(4))
        c.create_polygon(T(-22, -10, 22, -10, 27, 32, -27, 32), fill=isi, outline="")


def gambar_kartu(c, p):
    """Gambar satu kartu produk di kanvas c."""
    c.delete("all")
    W, H = CARD_W, CARD_H
    habis = p.stok <= 0
    kat = rapikan(p.kategori)
    utama = ABU if habis else warna_kategori(kat)
    tint = campur(utama, 0.16)
    terang = campur(utama, 0.72)

    # kartu + bayangan tipis
    rrect(c, 3, 5, W - 3, H - 1, 16, fill=BAYANG, outline="")
    rrect(c, 3, 2, W - 3, H - 4, 16, fill=PUTIH, outline=GARIS)

    # bidang ilustrasi
    rrect(c, 4, 3, W - 4, 136, 15, fill=utama, outline="")
    c.create_rectangle(4, 80, W - 4, 136, fill=utama, outline="")
    c.create_oval(W / 2 - 48, 20, W / 2 + 48, 116, fill=tint, outline="")
    gambar_ikon(c, W / 2, 68, jenis_ikon(kat), 1.0, PUTIH, tint, terang, utama)

    # label harga (seperti tag gantung) menimpa batas ilustrasi
    teks_harga = format_rupiah(p.harga)
    lebar_tag = F["harga"].measure(teks_harga) / SCALE + 38
    rrect(c, 14, 122, 14 + lebar_tag, 150, 9, fill=ABU_TAG if habis else KUNING, outline="")
    c.create_oval(23, 132.5, 30, 139.5, fill=PUTIH, outline="")
    c.create_text(38, 136, text=teks_harga, anchor="w", font=F["harga"], fill=INK)

    # nama (maks 2 baris)
    for i, baris in enumerate(bungkus(p.nama, F["nama"], (W - 32) * SCALE, 2)):
        c.create_text(16, 161 + i * 20, text=baris, anchor="nw", font=F["nama"], fill=INK)

    # kategori
    c.create_oval(16, 210, 24, 218, fill=utama, outline="")
    c.create_text(30, 214, text=potong(kat, F["kecil"], (W - 46) * SCALE), anchor="w",
                  font=F["kecil"], fill=TEKS2)

    c.create_line(16, 232, W - 16, 232, fill="#EDF1F6")

    # status stok
    if habis:
        status, warna = "Habis", MERAH
    elif p.stok <= 5:
        status, warna = "Hampir habis", ORANYE
    else:
        status, warna = "Tersedia", HIJAU
    c.create_oval(16, 242, 24, 250, fill=warna, outline="")
    c.create_text(30, 246, text=status, anchor="w", font=F["kecil_b"], fill=warna)
    c.create_text(W - 16, 246, text=f"Stok {p.stok}", anchor="e", font=F["kecil"], fill=TEKS2)

    rrect(c, 16, 258, W - 16, 264, 3, fill="#EDF1F6", outline="")
    if p.stok > 0:
        isi = (W - 32) * min(p.stok / 20.0, 1.0)
        rrect(c, 16, 258, 16 + max(isi, 6), 264, 3, fill=warna, outline="")

    skala(c)


# ======================================================================
#  KOMPONEN: tombol & kolom isian bersudut membulat
# ======================================================================

_Canvas = tk.Canvas if tk else object


class Tombol(_Canvas):
    def __init__(self, master, teks, perintah, bg, warna, hover, fg,
                 font=None, pad_x=20, pad_y=11, radius=12, garis=None):
        self.font = font or F["tombol"]
        self.teks, self.perintah = teks, perintah
        self.warna, self.hover, self.fg = warna, hover, fg
        self.radius, self.garis = radius, garis
        self.w = self.font.measure(teks) + px(pad_x * 2)
        self.h = self.font.metrics("linespace") + px(pad_y * 2)
        super().__init__(master, width=self.w, height=self.h, bg=bg,
                         highlightthickness=0, bd=0, cursor="hand2")
        self._di_atas = False
        self.bind("<Enter>", lambda e: self._atur_hover(True))
        self.bind("<Leave>", lambda e: self._atur_hover(False))
        self.bind("<Button-1>", lambda e: self.perintah())
        self._gambar()

    def _atur_hover(self, nilai):
        self._di_atas = nilai
        self._gambar()

    def ubah(self, warna, hover, fg):
        self.warna, self.hover, self.fg = warna, hover, fg
        self._gambar()

    def _gambar(self):
        self.delete("all")
        rrect(self, 1, 1, self.w - 1, self.h - 1, px(self.radius),
              fill=self.hover if self._di_atas else self.warna, outline=self.garis or "")
        self.create_text(self.w / 2, self.h / 2, text=self.teks, font=self.font, fill=self.fg)


class Kolom(_Canvas):
    """Kolom isian bersudut membulat: bisa berupa Entry atau Combobox, dengan placeholder."""

    def __init__(self, master, bg, placeholder="", values=None, prefix=None, ikon=None,
                 on_change=None, on_enter=None, tinggi=46, lebar=200):
        super().__init__(master, width=px(lebar), height=px(tinggi), bg=bg, highlightthickness=0, bd=0)
        self.placeholder, self.prefix, self.ikon = placeholder, prefix, ikon
        self.on_change = on_change
        self.fokus = self.galat = self.ph_aktif = self._tahan = False
        self.var = tk.StringVar()

        if values is not None:
            self.w = ttk.Combobox(self, textvariable=self.var, values=values,
                                  style="Toko.TCombobox", font=F["input"])
            self.w.bind("<<ComboboxSelected>>", lambda e: self._tulis())
        else:
            self.w = tk.Entry(self, textvariable=self.var, font=F["input"], relief="flat", bd=0,
                              highlightthickness=0, bg=PUTIH, fg=INK, insertbackground=INK)
        self._jendela = self.create_window(0, 0, window=self.w, anchor="w")

        self.var.trace_add("write", self._tulis)
        self.w.bind("<FocusIn>", self._masuk)
        self.w.bind("<FocusOut>", self._keluar)
        if on_enter:
            self.w.bind("<Return>", lambda e: on_enter())
        self.bind("<Configure>", lambda e: self._gambar())
        self.bind("<Button-1>", lambda e: self.w.focus_set())
        self._tampil_ph()

    # --- nilai ---
    def nilai(self):
        return "" if self.ph_aktif else self.var.get()

    def isi(self, teks):
        self._tahan = True
        self.var.set(teks)
        self._tahan = False
        self.ph_aktif = False
        self._warna_teks(INK)
        if not teks and not self.fokus:
            self._tampil_ph()

    def kosongkan(self):
        self.isi("")

    def set_galat(self, nilai):
        self.galat = nilai
        self._gambar()

    # --- placeholder ---
    def _warna_teks(self, warna):
        try:
            self.w.configure(foreground=warna) if isinstance(self.w, ttk.Combobox) else self.w.configure(fg=warna)
        except tk.TclError:
            pass

    def _tampil_ph(self):
        if self.placeholder and not self.var.get():
            self._tahan = True
            self.var.set(self.placeholder)
            self._tahan = False
            self.ph_aktif = True
            self._warna_teks("#8A97AB")

    def _masuk(self, _e=None):
        self.fokus = True
        if self.ph_aktif:
            self._tahan = True
            self.var.set("")
            self._tahan = False
            self.ph_aktif = False
            self._warna_teks(INK)
        self._gambar()

    def _keluar(self, _e=None):
        self.fokus = False
        if not self.var.get():
            self._tampil_ph()
        self._gambar()

    def _tulis(self, *_):
        if self._tahan:
            return
        if self.on_change:
            self.on_change()

    # --- gambar ---
    def _gambar(self):
        self.delete("latar")
        w, h = max(self.winfo_width(), 20), max(self.winfo_height(), 20)
        if self.galat:
            warna, tebal = MERAH, 2
        elif self.fokus:
            warna, tebal = FOKUS, 2
        else:
            warna, tebal = GARIS, 1
        rrect(self, 1, 1, w - 1, h - 1, px(12), fill=PUTIH, outline=warna, width=tebal, tags="latar")
        self.tag_lower("latar")

        x = px(16)
        if self.ikon == "cari":
            r, y = px(6), h / 2 - px(1)
            self.create_oval(x, y - r, x + 2 * r, y + r, outline=TEKS2, width=2, tags="latar")
            self.create_line(x + 2 * r - px(1), y + r - px(1), x + 2 * r + px(5), y + r + px(5),
                             fill=TEKS2, width=2, capstyle="round", tags="latar")
            x += px(30)
        if self.prefix:
            self.create_text(x, h / 2, text=self.prefix, anchor="w", font=F["body_b"], fill=TEKS2, tags="latar")
            x += F["body_b"].measure(self.prefix) + px(10)
        self.coords(self._jendela, x, h / 2)
        self.itemconfigure(self._jendela, width=max(10, w - x - px(14)))


# ======================================================================
#  APLIKASI
# ======================================================================

def _angka(teks, default):
    teks = (teks or "").replace(".", "").strip()
    return int(teks) if teks.isdigit() else default


def _di_dalam(widget, induk):
    while widget is not None:
        if widget is induk:
            return True
        widget = getattr(widget, "master", None)
    return False


class TokoApp:
    URUTAN = ["Terbaru", "Harga terendah", "Harga tertinggi", "Nama A-Z", "Stok terbanyak"]

    def __init__(self, root, halaman="katalog"):
        self.root = root
        self.produk = []
        self.kategori = {}        # kunci -> [label, jumlah]
        self.kat_aktif = None
        self.halaman = None
        self.kartu, self.tiles = [], []
        self.kolom, self.err = {}, {}
        self._kolom = self._kolom_tile = 0
        self._after_cari = self._after_toast = None

        self._siapkan_jendela()
        self._siapkan_gaya()
        self._bangun_navbar()
        self._bangun_badan()

        self.lbl_toast = tk.Label(root, font=F["toast"], fg="white", padx=px(20), pady=px(12),
                                  wraplength=px(640))

        for peristiwa in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            root.bind_all(peristiwa, self._roda)
        root.bind("<Control-f>", lambda e: self.fokus_cari())

        self.muat_ulang()
        self.tampilkan(halaman)

    # ---------------- jendela & gaya ----------------
    def _siapkan_jendela(self):
        r = self.root
        r.title("Toko Online")
        r.configure(bg=PAGE)
        lebar = min(px(1180), r.winfo_screenwidth() - px(60))
        tinggi = min(px(780), r.winfo_screenheight() - px(100))
        r.geometry(f"{lebar}x{tinggi}+{max(0, (r.winfo_screenwidth() - lebar) // 2)}"
                   f"+{max(0, (r.winfo_screenheight() - tinggi) // 3)}")
        r.minsize(min(px(860), lebar), min(px(600), tinggi))

    def _siapkan_gaya(self):
        try:
            s = ttk.Style(self.root)
            s.theme_use("clam")
            s.configure("Toko.TCombobox", fieldbackground=PUTIH, background=PUTIH, foreground=INK,
                        bordercolor=PUTIH, lightcolor=PUTIH, darkcolor=PUTIH, arrowcolor=TEKS2,
                        borderwidth=0, padding=0, relief="flat")
            s.map("Toko.TCombobox", fieldbackground=[("readonly", PUTIH)], bordercolor=[("focus", PUTIH)],
                  lightcolor=[("focus", PUTIH)], darkcolor=[("focus", PUTIH)])
            s.configure("Urut.TCombobox", fieldbackground=PUTIH, background=PUTIH, foreground=INK,
                        bordercolor=GARIS, lightcolor=PUTIH, darkcolor=PUTIH, arrowcolor=TEKS2,
                        padding=px(6), relief="flat")
            s.map("Urut.TCombobox", fieldbackground=[("readonly", PUTIH)], foreground=[("readonly", INK)])
            s.layout("Toko.Vertical.TScrollbar",
                     [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [
                         ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])
            s.configure("Toko.Vertical.TScrollbar", background="#C6D0DE", troughcolor=PAGE,
                        bordercolor=PAGE, lightcolor="#C6D0DE", darkcolor="#C6D0DE", width=px(10))
            s.map("Toko.Vertical.TScrollbar", background=[("active", "#A9B6C8")],
                  lightcolor=[("active", "#A9B6C8")], darkcolor=[("active", "#A9B6C8")])
            self.root.option_add("*TCombobox*Listbox.font", F["input"])
            self.root.option_add("*TCombobox*Listbox.background", PUTIH)
            self.root.option_add("*TCombobox*Listbox.foreground", INK)
            self.root.option_add("*TCombobox*Listbox.selectBackground", KUNING)
            self.root.option_add("*TCombobox*Listbox.selectForeground", INK)
        except tk.TclError:
            pass

    # ---------------- navbar ----------------
    def _bangun_navbar(self):
        nav = tk.Frame(self.root, bg=INK)
        nav.pack(fill="x")
        isi = tk.Frame(nav, bg=INK)
        isi.pack(fill="x", padx=px(32), pady=px(14))
        isi.columnconfigure(1, weight=1)

        merek = tk.Frame(isi, bg=INK)
        merek.grid(row=0, column=0, sticky="w")
        logo = tk.Canvas(merek, width=px(44), height=px(44), bg=INK, highlightthickness=0)
        logo.pack(side="left")
        rrect(logo, 0, 0, 44, 44, 12, fill=KUNING, outline="")
        gambar_ikon(logo, 22, 23, "default", 0.5, INK, KUNING, "#E0A100", INK)
        skala(logo)
        tk.Label(merek, text="Toko Online", font=F["brand"], bg=INK, fg="white").pack(side="left", padx=(px(12), 0))

        self.cari = Kolom(isi, bg=INK, placeholder="Cari produk atau kategori", ikon="cari",
                          on_change=self._jadwal_cari, tinggi=44, lebar=240)
        self.cari.grid(row=0, column=1, sticky="ew", padx=px(40))

        menu = tk.Frame(isi, bg=INK)
        menu.grid(row=0, column=2, sticky="e")
        self.tb_katalog = Tombol(menu, "Katalog", self.buka_katalog, INK, INK, INK_HOVER, "white")
        self.tb_katalog.pack(side="left")
        self.tb_tambah = Tombol(menu, "Tambah produk", self.buka_tambah_produk, INK, INK, INK_HOVER, "white")
        self.tb_tambah.pack(side="left", padx=(px(6), 0))

    # ---------------- badan ----------------
    def _bangun_badan(self):
        self.badan = tk.Frame(self.root, bg=PAGE)
        self.badan.pack(fill="both", expand=True)
        self.badan.rowconfigure(0, weight=1)
        self.badan.columnconfigure(0, weight=1)
        self._bangun_katalog()
        self._bangun_tambah()

    # ---- halaman katalog ----
    def _bangun_katalog(self):
        hal = self.hal_katalog = tk.Frame(self.badan, bg=PAGE)
        hal.grid(row=0, column=0, sticky="nsew")
        hal.rowconfigure(0, weight=1)
        hal.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(hal, bg=PAGE, highlightthickness=0, yscrollincrement=px(36))
        bar = ttk.Scrollbar(hal, orient="vertical", command=self.canvas.yview,
                            style="Toko.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=bar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        bar.grid(row=0, column=1, sticky="ns")

        self.isi = tk.Frame(self.canvas, bg=PAGE)
        self._jendela_isi = self.canvas.create_window(0, 0, window=self.isi, anchor="nw")
        self.canvas.bind("<Configure>", self._ukuran_kanvas)
        self.isi.bind("<Configure>", lambda e: self._perbarui_scroll())

        # banner biru tua: judul + tombol kategori
        band = tk.Frame(self.isi, bg=INK)
        band.pack(fill="x")
        dalam = tk.Frame(band, bg=INK)
        dalam.pack(fill="x", padx=px(32), pady=(px(8), px(22)))
        tk.Label(dalam, text="Pilih produk favoritmu", font=F["judul"], bg=INK, fg="white").pack(anchor="w")
        self.lbl_sub = tk.Label(dalam, text="", font=F["body"], bg=INK, fg=SOFT)
        self.lbl_sub.pack(anchor="w", pady=(px(4), px(18)))
        self.frame_tile = tk.Frame(dalam, bg=INK)
        self.frame_tile.pack(fill="x")

        # baris hasil + urutan
        baris = tk.Frame(self.isi, bg=PAGE)
        baris.pack(fill="x", padx=px(32), pady=(px(24), px(8)))
        self.lbl_hasil = tk.Label(baris, text="", font=F["h2"], bg=PAGE, fg=INK)
        self.lbl_hasil.pack(side="left")
        self.var_urut = tk.StringVar(value=self.URUTAN[0])
        pilih = ttk.Combobox(baris, textvariable=self.var_urut, values=self.URUTAN, state="readonly",
                             width=16, style="Urut.TCombobox", font=F["body"])
        pilih.pack(side="right")
        pilih.bind("<<ComboboxSelected>>", lambda e: self._render_katalog())
        tk.Label(baris, text="Urutkan", font=F["body"], bg=PAGE, fg=TEKS2).pack(side="right", padx=(0, px(10)))

        # daftar kartu
        self.frame_grid = tk.Frame(self.isi, bg=PAGE)
        self.frame_grid.pack(fill="x", padx=px(32 - GAP / 2), pady=(0, px(32)))

    # ---- halaman tambah produk ----
    def _bangun_tambah(self):
        hal = self.hal_tambah = tk.Frame(self.badan, bg=PAGE)
        hal.grid(row=0, column=0, sticky="nsew")
        self.pusat = tk.Frame(hal, bg=PAGE)
        self.pusat.pack(fill="both", expand=True, padx=px(32), pady=px(28))
        hal.bind("<Configure>", self._ukuran_tambah)

        tk.Label(self.pusat, text="Tambah produk", font=F["judul"], bg=PAGE, fg=INK).pack(anchor="w")
        tk.Label(self.pusat, text="Isi data di bawah. Kartu di sebelah kanan menunjukkan tampilan produk di katalog.",
                 font=F["body"], bg=PAGE, fg=TEKS2).pack(anchor="w", pady=(px(4), px(18)))

        isi = tk.Frame(self.pusat, bg=PAGE)
        isi.pack(fill="x")
        isi.columnconfigure(0, weight=1)

        kartu = tk.Frame(isi, bg=PUTIH, highlightthickness=1, highlightbackground=GARIS, highlightcolor=GARIS)
        kartu.grid(row=0, column=0, sticky="new")
        dalam = tk.Frame(kartu, bg=PUTIH)
        dalam.pack(fill="x", padx=px(28), pady=px(24))

        self._buat_field(dalam, "nama", "Nama produk", placeholder="Contoh: Kaos Polos").pack(fill="x")
        self._buat_field(dalam, "kategori", "Kategori", placeholder="Pilih atau ketik kategori baru",
                         values=[]).pack(fill="x")
        baris = tk.Frame(dalam, bg=PUTIH)
        baris.pack(fill="x")
        baris.columnconfigure(0, weight=1, uniform="f")
        baris.columnconfigure(1, weight=1, uniform="f")
        self._buat_field(baris, "harga", "Harga", placeholder="75000", prefix="Rp").grid(
            row=0, column=0, sticky="ew", padx=(0, px(8)))
        self._buat_field(baris, "stok", "Stok", placeholder="20").grid(
            row=0, column=1, sticky="ew", padx=(px(8), 0))

        tombol = tk.Frame(dalam, bg=PUTIH)
        tombol.pack(fill="x", pady=(px(8), 0))
        Tombol(tombol, "Simpan produk", self.simpan, PUTIH, KUNING, KUNING_GELAP, INK,
               pad_x=28, pad_y=12).pack(side="left")
        Tombol(tombol, "Kosongkan", self.kosongkan_form, PUTIH, PUTIH, "#EEF2F8", INK,
               pad_x=22, pad_y=12, garis=GARIS).pack(side="left", padx=(px(10), 0))

        kanan = tk.Frame(isi, bg=PAGE)
        kanan.grid(row=0, column=1, sticky="n", padx=(px(28), 0))
        tk.Label(kanan, text="Tampilan di katalog", font=F["body_b"], bg=PAGE, fg=TEKS2).pack(
            anchor="w", pady=(0, px(8)))
        self.kartu_pratinjau = tk.Canvas(kanan, width=px(CARD_W), height=px(CARD_H), bg=PAGE,
                                         highlightthickness=0)
        self.kartu_pratinjau.pack()
        self._pratinjau()

    def _buat_field(self, induk, kunci, judul, **kw):
        blok = tk.Frame(induk, bg=PUTIH)
        tk.Label(blok, text=judul, font=F["body_b"], bg=PUTIH, fg=INK).pack(anchor="w", pady=(0, px(6)))
        kolom = Kolom(blok, bg=PUTIH, on_change=lambda k=kunci: self._berubah_form(k),
                      on_enter=self.simpan, **kw)
        kolom.pack(fill="x")
        err = tk.Label(blok, text="", font=F["kecil"], bg=PUTIH, fg=MERAH, anchor="w")
        err.pack(fill="x", pady=(px(4), px(6)))
        self.kolom[kunci], self.err[kunci] = kolom, err
        return blok

    def _ukuran_tambah(self, e):
        sisi = max(px(32), (e.width - px(1060)) // 2)
        self.pusat.pack_configure(padx=sisi)

    # ---------------- navigasi ----------------
    def tampilkan(self, halaman):
        self.halaman = halaman
        katalog = halaman == "katalog"
        (self.hal_katalog if katalog else self.hal_tambah).tkraise()
        if katalog:
            self.cari.grid()
            self.canvas.yview_moveto(0)
        else:
            self.cari.grid_remove()
            self.kolom["nama"].w.focus_set()
        aktif, biasa = (KUNING, KUNING_GELAP, INK), (INK, INK_HOVER, "white")
        self.tb_katalog.ubah(*(aktif if katalog else biasa))
        self.tb_tambah.ubah(*(biasa if katalog else aktif))

    def buka_katalog(self):
        self.tampilkan("katalog")

    def buka_tambah_produk(self):
        self.tampilkan("tambah")

    def fokus_cari(self):
        self.buka_katalog()
        self.cari.w.focus_set()

    # ---------------- data ----------------
    def muat_ulang(self):
        self.produk = tampil_produk.muat_data(tampilkan_pesan=False)
        self.kategori = {}
        for p in self.produk:
            label = rapikan(p.kategori)
            kunci = label.lower()
            if kunci in self.kategori:
                self.kategori[kunci][1] += 1
            else:
                self.kategori[kunci] = [label, 1]
        if self.kat_aktif not in self.kategori:
            self.kat_aktif = None

        n, k = len(self.produk), len(self.kategori)
        self.lbl_sub.configure(text=f"{n} produk dari {k} kategori" if n else "Belum ada produk di katalog")

        saran = [v[0] for v in self.kategori.values()]
        for contoh in ("Pakaian", "Sepatu", "Tas", "Elektronik", "Aksesoris"):
            if contoh.lower() not in self.kategori:
                saran.append(contoh)
        self.kolom["kategori"].w.configure(values=saran)

        self._bangun_tiles()
        self._render_katalog()

    def _terfilter(self):
        q = self.cari.nilai().strip().lower()
        hasil = []
        for p in self.produk:
            if self.kat_aktif and rapikan(p.kategori).lower() != self.kat_aktif:
                continue
            if q and q not in p.nama.lower() and q not in p.kategori.lower():
                continue
            hasil.append(p)

        urut = self.var_urut.get()
        if urut == "Harga terendah":
            hasil.sort(key=lambda p: p.harga)
        elif urut == "Harga tertinggi":
            hasil.sort(key=lambda p: -p.harga)
        elif urut == "Nama A-Z":
            hasil.sort(key=lambda p: p.nama.lower())
        elif urut == "Stok terbanyak":
            hasil.sort(key=lambda p: -p.stok)
        else:
            hasil.reverse()
        return hasil

    # ---------------- tombol kategori ----------------
    def _bangun_tiles(self):
        for t in self.tiles:
            t.destroy()
        self.tiles = []
        daftar = [(None, "Semua", len(self.produk))] + [(k, v[0], v[1]) for k, v in self.kategori.items()]
        for kunci, label, jumlah in daftar:
            self.tiles.append(self._buat_tile(kunci, label, jumlah))
        self._susun_tiles(paksa=True)

    def _buat_tile(self, kunci, label, jumlah):
        c = tk.Canvas(self.frame_tile, width=px(TILE_W), height=px(TILE_H), bg=INK,
                      highlightthickness=0, cursor="hand2")
        aktif = kunci == self.kat_aktif
        utama, jenis = ("#4C6A92", "default") if kunci is None else (warna_kategori(label), jenis_ikon(label))
        rrect(c, 4, 4, TILE_W - 4, 84, 18, fill=utama, outline=KUNING if aktif else "", width=3 if aktif else 1)
        gambar_ikon(c, TILE_W / 2, 44, jenis, 0.78, PUTIH, utama, campur(utama, 0.70), utama)
        c.create_text(TILE_W / 2, 99, text=potong(label, F["tile"], (TILE_W - 4) * SCALE),
                      font=F["tile"], fill=KUNING if aktif else PUTIH)
        c.create_text(TILE_W / 2, 116, text=f"{jumlah} produk", font=F["tile_k"], fill=SOFT)
        skala(c)
        c.bind("<Button-1>", lambda e, k=kunci: self.pilih_kategori(k))
        return c

    def _susun_tiles(self, paksa=False):
        if not self.tiles:
            return
        lebar = self.canvas.winfo_width() - 2 * px(32)
        kolom = max(1, (lebar + px(10)) // (px(TILE_W) + px(10)))
        if not paksa and kolom == self._kolom_tile:
            return
        self._kolom_tile = kolom
        for i, t in enumerate(self.tiles):
            t.grid(row=i // kolom, column=i % kolom, padx=(0, px(10)), pady=(0, px(6)), sticky="w")

    def pilih_kategori(self, kunci):
        self.kat_aktif = None if kunci == self.kat_aktif else kunci
        self._bangun_tiles()
        self._render_katalog()

    # ---------------- daftar kartu ----------------
    def _jadwal_cari(self):
        if self._after_cari:
            self.root.after_cancel(self._after_cari)
        self._after_cari = self.root.after(140, self._render_katalog)

    def _render_katalog(self):
        for w in self.frame_grid.winfo_children():
            w.destroy()
        for i in range(40):
            self.frame_grid.columnconfigure(i, weight=0)
        self.kartu = []
        self._kolom = 0

        hasil = self._terfilter()
        q = self.cari.nilai().strip()
        judul = f"{self.kategori[self.kat_aktif][0]} ({len(hasil)})" if self.kat_aktif else f"Semua produk ({len(hasil)})"
        if q:
            judul += f" untuk “{q}”"
        self.lbl_hasil.configure(text=judul)

        if not self.produk:
            self._kosong("Katalog masih kosong", "Tambahkan produk pertama, lalu produk akan tampil di sini.",
                         "Tambah produk", self.buka_tambah_produk)
        elif not hasil:
            self._kosong("Produk tidak ditemukan", "Coba kata kunci lain atau pilih kategori Semua.",
                         "Tampilkan semua produk", self._reset_filter)
        else:
            for p in hasil:
                c = tk.Canvas(self.frame_grid, width=px(CARD_W), height=px(CARD_H), bg=PAGE,
                              highlightthickness=0)
                gambar_kartu(c, p)
                self.kartu.append(c)
            self._susun(paksa=True)
        self._perbarui_scroll()

    def _kosong(self, judul, isi, teks_tombol, perintah):
        self.frame_grid.columnconfigure(0, weight=1)
        kosong = tk.Frame(self.frame_grid, bg=PAGE)
        kosong.grid(row=0, column=0, sticky="ew", pady=px(48))
        tk.Label(kosong, text=judul, font=F["h2"], bg=PAGE, fg=INK).pack()
        tk.Label(kosong, text=isi, font=F["body"], bg=PAGE, fg=TEKS2).pack(pady=(px(6), px(18)))
        Tombol(kosong, teks_tombol, perintah, PAGE, KUNING, KUNING_GELAP, INK, pad_x=24, pad_y=11).pack()

    def _reset_filter(self):
        self.kat_aktif = None
        self.cari.kosongkan()
        self._bangun_tiles()
        self._render_katalog()

    def _susun(self, paksa=False):
        if not self.kartu:
            return
        lebar = self.canvas.winfo_width() - 2 * px(32) + px(GAP)
        kolom = max(1, lebar // (px(CARD_W) + px(GAP)))
        if not paksa and kolom == self._kolom:
            return
        self._kolom = kolom
        for i in range(40):
            self.frame_grid.columnconfigure(i, weight=1 if i < kolom else 0)
        for i, c in enumerate(self.kartu):
            c.grid(row=i // kolom, column=i % kolom, padx=px(GAP / 2), pady=px(GAP / 2), sticky="w")

    # ---------------- scroll ----------------
    def _ukuran_kanvas(self, e):
        self.canvas.itemconfigure(self._jendela_isi, width=e.width)
        self._susun()
        self._susun_tiles()
        self._perbarui_scroll()

    def _perbarui_scroll(self):
        tinggi = max(self.isi.winfo_reqheight(), self.canvas.winfo_height())
        self.canvas.configure(scrollregion=(0, 0, self.canvas.winfo_width(), tinggi))

    def _roda(self, e):
        if self.halaman != "katalog":
            return
        try:
            di = self.root.winfo_containing(e.x_root, e.y_root)
        except (KeyError, tk.TclError):
            return
        if not _di_dalam(di, self.hal_katalog):
            return
        if getattr(e, "num", 0) == 4:
            langkah = -3
        elif getattr(e, "num", 0) == 5:
            langkah = 3
        elif sys.platform == "darwin":
            langkah = -1 if e.delta > 0 else 1
        else:
            langkah = (-1 if e.delta > 0 else 1) * max(1, abs(e.delta) // 120) * 3
        self.canvas.yview_scroll(langkah, "units")

    # ---------------- form tambah produk ----------------
    def _berubah_form(self, kunci):
        if self.kolom[kunci].galat:
            self.kolom[kunci].set_galat(False)
            self.err[kunci].configure(text="")
        self._pratinjau()

    def _pratinjau(self):
        nama = self.kolom["nama"].nilai().strip() or "Nama produk"
        kat = self.kolom["kategori"].nilai().strip() or "Kategori"
        harga = _angka(self.kolom["harga"].nilai(), 0)
        stok_teks = self.kolom["stok"].nilai().strip()
        stok = _angka(stok_teks, 0) if stok_teks else 10
        gambar_kartu(self.kartu_pratinjau, Produk(nama, kat, harga, stok))

    def kosongkan_form(self):
        for kunci, kolom in self.kolom.items():
            kolom.kosongkan()
            kolom.set_galat(False)
            self.err[kunci].configure(text="")
        self._pratinjau()
        self.kolom["nama"].w.focus_set()

    def simpan(self):
        nilai = {k: kolom.nilai() for k, kolom in self.kolom.items()}
        produk, galat = tambah_produk.periksa_produk(nilai["nama"], nilai["kategori"],
                                                     nilai["harga"], nilai["stok"])
        for kunci, kolom in self.kolom.items():
            pesan = galat.get(kunci, "")
            self.err[kunci].configure(text=pesan)
            kolom.set_galat(bool(pesan))
        if galat:
            pertama = next(k for k in ("nama", "kategori", "harga", "stok") if k in galat)
            self.kolom[pertama].w.focus_set()
            return

        try:
            tambah_produk.simpan_ke_csv(produk)
        except OSError:
            self.toast("Produk belum tersimpan. Tutup produk.csv jika sedang dibuka di aplikasi lain, lalu coba lagi.",
                       MERAH, 6000)
            return

        self.kosongkan_form()
        self.muat_ulang()
        self.toast(f"{produk.nama} disimpan ke katalog", HIJAU)

    # ---------------- notifikasi ----------------
    def toast(self, teks, warna=INK, durasi=2800):
        if self._after_toast:
            self.root.after_cancel(self._after_toast)
        self.lbl_toast.configure(text=teks, bg=warna)
        self.lbl_toast.place(relx=0.5, rely=1.0, y=-px(28), anchor="s")
        self.lbl_toast.lift()
        self._after_toast = self.root.after(durasi, self.lbl_toast.place_forget)


# ======================================================================
#  PINTU MASUK
# ======================================================================

def jalankan(halaman="katalog"):
    """Membuka jendela UI toko. halaman: 'katalog' atau 'tambah'."""
    if tk is None:
        print("Tkinter tidak ditemukan di instalasi Python ini, menjalankan menu teks.")
        from main import menu_utama
        menu_utama()
        return

    if sys.platform == "win32":  # agar tulisan tajam di layar resolusi tinggi
        try:
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    root = tk.Tk()
    siapkan_tema(root)
    TokoApp(root, halaman)
    root.mainloop()


if __name__ == "__main__":
    jalankan("katalog")
