import customtkinter as ctk
import json
import os
from datetime import datetime
from tkinter import messagebox

# Konfigurasi Tampilan dan Tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class KasirAngkringanApp(ctk.CTk):
    """
    Aplikasi Kasir Angkringan dengan GUI modern, manajemen menu,
    dan pencetakan nota. Versi Fullscreen.
    """
    def __init__(self):
        super().__init__()

        # --- Konfigurasi Window Utama ---
        self.title("👨‍🍳 Kasir Angkringan ")
        # Baris ini membuat aplikasi menjadi layar penuh secara default
        self.attributes('-fullscreen', True)

        # Menambahkan fungsi untuk keluar dari mode fullscreen dengan menekan tombol <Escape>
        self.bind("<Escape>", self.keluar_fullscreen)

        # --- Inisialisasi Data ---
        self.file_menu = "menu.json"
        self.menu_data = self.muat_menu()
        self.keranjang = {}
        self.total_belanja = 0.0

        # --- Membuat UI ---
        self.buat_widget()
        self.perbarui_tampilan_menu_pesanan()
        self.perbarui_dropdown_menu_kelola()
        
    def keluar_fullscreen(self, event=None):
        """Fungsi untuk keluar dari mode fullscreen."""
        # Menonaktifkan atribut fullscreen
        self.attributes("-fullscreen", False)
        # Opsi: Setelah keluar, buat jendela menjadi maximized (memenuhi layar tapi masih ada taskbar)
        self.state("zoomed")


    # =====================================================================
    #  FUNGSI LOGIKA & UTILITAS
    # =====================================================================

    def _bersihkan_input_angka(self, teks_input):
        """Membersihkan string input dari karakter non-numerik."""
        if not teks_input:
            return "0"
        return teks_input.replace("Rp", "").replace(",", "").replace(".", "").strip()

    def muat_menu(self):
        """Memuat data menu dari file JSON."""
        if not os.path.exists(self.file_menu):
            data_default = {
                "Nasi Kucing": 2500, "Sate Usus": 2000, "Sate Telur Puyuh": 3000,
                "Gorengan": 1000, "Es Teh": 3000, "Kopi Jos": 5000
            }
            with open(self.file_menu, 'w') as f:
                json.dump(data_default, f, indent=4)
            return data_default
        try:
            with open(self.file_menu, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            messagebox.showerror("Error", "Gagal memuat file menu.json.")
            return {}

    def simpan_menu(self):
        """Menyimpan data menu ke file JSON."""
        try:
            with open(self.file_menu, 'w') as f:
                json.dump(self.menu_data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan menu: {e}")

    # =====================================================================
    #  PEMBUATAN WIDGET / UI
    # =====================================================================

    def buat_widget(self):
        """Membuat dan menata semua elemen UI di window."""
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        frame_kiri = ctk.CTkFrame(self, corner_radius=15)
        frame_kiri.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        tab_view = ctk.CTkTabview(frame_kiri, corner_radius=10)
        tab_view.pack(expand=True, fill="both", padx=15, pady=15)
        tab_pesan = tab_view.add("🛒 Pesan Menu")
        tab_kelola = tab_view.add("⚙️ Kelola Menu")

        self.frame_kanan = ctk.CTkFrame(self, corner_radius=15)
        self.frame_kanan.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        self.frame_kanan.grid_rowconfigure(1, weight=1)
        self.frame_kanan.grid_columnconfigure(0, weight=1)

        label_pesan = ctk.CTkLabel(tab_pesan, text="Pilih Menu untuk Dipesan", font=ctk.CTkFont(size=18, weight="bold"))
        label_pesan.pack(pady=(10, 5))
        self.frame_menu_pesanan = ctk.CTkScrollableFrame(tab_pesan, label_text="Daftar Menu Tersedia")
        self.frame_menu_pesanan.pack(expand=True, fill="both", padx=10, pady=10)

        self.buat_widget_kelola_menu(tab_kelola)
        self.buat_widget_keranjang_pembayaran()


    def buat_widget_kelola_menu(self, parent_tab):
        label_pilih_menu = ctk.CTkLabel(parent_tab, text="Pilih Menu untuk Diedit/Dihapus", font=ctk.CTkFont(size=14))
        label_pilih_menu.pack(pady=(15, 5))
        
        self.opsi_menu_kelola = ctk.CTkOptionMenu(parent_tab, values=list(self.menu_data.keys()), command=self.pilih_menu_untuk_diedit)
        self.opsi_menu_kelola.pack(pady=5, padx=20, fill="x")
        self.opsi_menu_kelola.set("Pilih Menu...")

        frame_form = ctk.CTkFrame(parent_tab, fg_color="transparent")
        frame_form.pack(pady=20, padx=20, fill="x")
        frame_form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_form, text="Nama Menu:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.entry_nama_menu = ctk.CTkEntry(frame_form, placeholder_text="cth: Gorengan Tahu")
        self.entry_nama_menu.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(frame_form, text="Harga (Rp):").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.entry_harga_menu = ctk.CTkEntry(frame_form, placeholder_text="cth: 1000 atau 1.000")
        self.entry_harga_menu.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        frame_tombol = ctk.CTkFrame(parent_tab, fg_color="transparent")
        frame_tombol.pack(pady=10, padx=20, fill="x")
        
        tombol_tambah = ctk.CTkButton(frame_tombol, text="➕ Tambah Menu Baru", command=self.tambah_menu)
        tombol_tambah.pack(side="left", expand=True, padx=5)

        tombol_simpan = ctk.CTkButton(frame_tombol, text="💾 Simpan Perubahan", command=self.simpan_perubahan_menu)
        tombol_simpan.pack(side="left", expand=True, padx=5)

        tombol_hapus = ctk.CTkButton(frame_tombol, text="❌ Hapus Menu", command=self.hapus_menu, fg_color="#D32F2F", hover_color="#B71C1C")
        tombol_hapus.pack(side="left", expand=True, padx=5)

    def buat_widget_keranjang_pembayaran(self):
        label_keranjang = ctk.CTkLabel(self.frame_kanan, text="Keranjang Belanja", font=ctk.CTkFont(size=18, weight="bold"))
        label_keranjang.grid(row=0, column=0, pady=(15, 10), padx=20)
        
        self.teks_keranjang = ctk.CTkTextbox(self.frame_kanan, font=("Consolas", 12), state="disabled", corner_radius=10)
        self.teks_keranjang.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")

        frame_total = ctk.CTkFrame(self.frame_kanan, corner_radius=10, fg_color="#1E4D2B")
        frame_total.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        frame_total.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_total, text="TOTAL:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.label_total = ctk.CTkLabel(frame_total, text="Rp 0", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_total.grid(row=0, column=1, padx=15, pady=10, sticky="e")
        
        frame_pembayaran = ctk.CTkFrame(self.frame_kanan, fg_color="transparent")
        frame_pembayaran.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        frame_pembayaran.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_pembayaran, text="Uang Bayar (Rp):").grid(row=0, column=0, sticky="w")
        self.entry_bayar = ctk.CTkEntry(frame_pembayaran, placeholder_text="cth: 50000 atau 50.000")
        self.entry_bayar.grid(row=0, column=1, sticky="ew", padx=(10,0))
        
        ctk.CTkLabel(frame_pembayaran, text="Kembalian:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", pady=(10,0))
        self.label_kembalian = ctk.CTkLabel(frame_pembayaran, text="Rp 0", font=ctk.CTkFont(weight="bold"))
        self.label_kembalian.grid(row=1, column=1, sticky="ew", padx=(10,0), pady=(10,0))

        self.tombol_bayar = ctk.CTkButton(self.frame_kanan, text="💸 Bayar & Hitung Kembalian", command=self.proses_pembayaran)
        self.tombol_bayar.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.tombol_cetak = ctk.CTkButton(self.frame_kanan, text="📄 Cetak & Simpan Nota", state="disabled", command=self.cetak_nota)
        self.tombol_cetak.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
    
    # =====================================================================
    #  FUNGSI UNTUK MEMPERBARUI TAMPILAN (REFRESH UI)
    # =====================================================================

    def perbarui_tampilan_menu_pesanan(self):
        for widget in self.frame_menu_pesanan.winfo_children():
            widget.destroy()

        for nama, harga in sorted(self.menu_data.items()):
            frame_item = ctk.CTkFrame(self.frame_menu_pesanan)
            frame_item.pack(fill="x", padx=5, pady=5)
            
            label_nama_harga = ctk.CTkLabel(frame_item, text=f"{nama} - Rp {harga:,.0f}", anchor="w")
            label_nama_harga.pack(side="left", fill="x", expand=True, padx=10, pady=10)
            
            entry_jumlah = ctk.CTkEntry(frame_item, width=50, placeholder_text="Jml")
            entry_jumlah.pack(side="left", padx=5)
            
            tombol_tambah_keranjang = ctk.CTkButton(frame_item, text="➕", width=30,
                command=lambda n=nama, p=harga, e=entry_jumlah: self.tambah_ke_keranjang(n, p, e))
            tombol_tambah_keranjang.pack(side="left", padx=(0, 5))

    def perbarui_tampilan_keranjang(self):
        self.teks_keranjang.configure(state="normal")
        self.teks_keranjang.delete("1.0", "end")
        
        if not self.keranjang:
            self.teks_keranjang.insert("end", "Keranjang masih kosong...")
            self.total_belanja = 0.0
        else:
            header = f"{'Nama Item':<20}{'Jml':>5}{'Harga':>12}{'Subtotal':>15}\n"
            divider = "-"*52 + "\n"
            self.teks_keranjang.insert("end", header + divider)
            
            total = 0
            for nama, detail in self.keranjang.items():
                subtotal = detail["jumlah"] * detail["harga"]
                total += subtotal
                line = f"{nama:<20}{detail['jumlah']:>5}{detail['harga']:>12,.0f}{subtotal:>15,.0f}\n"
                self.teks_keranjang.insert("end", line)
            self.total_belanja = total
        
        self.label_total.configure(text=f"Rp {self.total_belanja:,.0f}")
        self.teks_keranjang.configure(state="disabled")

    def perbarui_dropdown_menu_kelola(self):
        menu_keys = list(self.menu_data.keys())
        self.opsi_menu_kelola.configure(values=menu_keys if menu_keys else ["Tidak ada menu"])
        if not menu_keys: self.opsi_menu_kelola.set("Tidak ada menu")
        else: self.opsi_menu_kelola.set("Pilih Menu...")

    # =====================================================================
    #  FUNGSI AKSI (COMMANDS TOMBOL)
    # =====================================================================

    def tambah_ke_keranjang(self, nama, harga, entry_jumlah):
        try:
            jumlah_str = self._bersihkan_input_angka(entry_jumlah.get())
            jumlah = int(jumlah_str)
            if jumlah <= 0: raise ValueError
        except (ValueError, TypeError):
            messagebox.showwarning("Input Salah", "Jumlah harus berupa angka positif.")
            return

        if nama in self.keranjang: self.keranjang[nama]["jumlah"] += jumlah
        else: self.keranjang[nama] = {"jumlah": jumlah, "harga": harga}
        
        entry_jumlah.delete(0, "end")
        self.perbarui_tampilan_keranjang()
        self.reset_pembayaran()

    def proses_pembayaran(self):
        try:
            uang_bayar_str = self._bersihkan_input_angka(self.entry_bayar.get())
            uang_bayar = float(uang_bayar_str)

            if uang_bayar < self.total_belanja:
                messagebox.showerror("Pembayaran Kurang", "Uang yang dibayarkan kurang dari total belanja.")
                return
            
            kembalian = uang_bayar - self.total_belanja
            self.label_kembalian.configure(text=f"Rp {kembalian:,.0f}")
            self.tombol_cetak.configure(state="normal")
            
        except (ValueError, TypeError):
            messagebox.showerror("Input Salah", "Masukkan jumlah uang bayar yang valid.")

    def cetak_nota(self):
        if self.total_belanja == 0:
            messagebox.showinfo("Info", "Tidak ada item di keranjang untuk dicetak.")
            return
        
        timestamp = datetime.now()
        nama_file = f"nota_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
        
        teks_nota = f"===== NOTA ANGKRIANGAN MODERN =====\n\nWaktu: {timestamp.strftime('%d-%m-%Y %H:%M:%S')}\n" + "-"*35 + "\n"
        
        for nama, detail in self.keranjang.items():
            teks_nota += f"{nama:<20} {detail['jumlah']} x {detail['harga']:,.0f}\n"
        
        teks_nota += "-"*35 + "\n"
        teks_nota += f"{'Total Belanja:':<20} Rp {self.total_belanja:,.0f}\n"
        
        try:
            uang_bayar_str = self._bersihkan_input_angka(self.entry_bayar.get())
            uang_bayar = float(uang_bayar_str)
            kembalian = uang_bayar - self.total_belanja
            teks_nota += f"{'Uang Bayar:':<20} Rp {uang_bayar:,.0f}\n"
            teks_nota += f"{'Kembalian:':<20} Rp {kembalian:,.0f}\n"
        except (ValueError, TypeError): pass

        teks_nota += "\nTerima kasih telah berkunjung! 🙏\n"
        
        ToplevelNota(self, teks_nota)
        
        try:
            with open(nama_file, 'w') as f: f.write(teks_nota)
            messagebox.showinfo("Sukses", f"Nota berhasil disimpan sebagai '{nama_file}'")
        except Exception as e:
            messagebox.showerror("Gagal Menyimpan", f"Gagal menyimpan nota: {e}")
        
        self.reset_transaksi()

    def reset_transaksi(self):
        self.keranjang = {}
        self.perbarui_tampilan_keranjang()
        self.reset_pembayaran()

    def reset_pembayaran(self):
        self.entry_bayar.delete(0, "end")
        self.label_kembalian.configure(text="Rp 0")
        self.tombol_cetak.configure(state="disabled")

    def tambah_menu(self):
        nama = self.entry_nama_menu.get().strip()
        harga_str = self._bersihkan_input_angka(self.entry_harga_menu.get())
        
        if not nama or not harga_str or int(harga_str) == 0:
            messagebox.showwarning("Input Kosong", "Nama dan harga menu tidak boleh kosong.")
            return
        if nama in self.menu_data:
            messagebox.showwarning("Menu Sudah Ada", f"Menu '{nama}' sudah ada dalam daftar.")
            return
        try:
            harga = float(harga_str)
            if harga < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Input Salah", "Harga harus berupa angka positif.")
            return
            
        self.menu_data[nama] = harga
        self.simpan_menu()
        messagebox.showinfo("Sukses", f"Menu '{nama}' berhasil ditambahkan.")
        
        self.perbarui_tampilan_menu_pesanan()
        self.perbarui_dropdown_menu_kelola()
        self.entry_nama_menu.delete(0, "end")
        self.entry_harga_menu.delete(0, "end")

    def pilih_menu_untuk_diedit(self, nama_menu_terpilih):
        if nama_menu_terpilih and nama_menu_terpilih != "Pilih Menu...":
            harga = self.menu_data.get(nama_menu_terpilih)
            self.entry_nama_menu.delete(0, "end")
            self.entry_nama_menu.insert(0, nama_menu_terpilih)
            self.entry_harga_menu.delete(0, "end")
            self.entry_harga_menu.insert(0, str(int(harga)))

    def simpan_perubahan_menu(self):
        nama_baru = self.entry_nama_menu.get().strip()
        nama_lama = self.opsi_menu_kelola.get()
        harga_str = self._bersihkan_input_angka(self.entry_harga_menu.get())

        if nama_lama == "Pilih Menu..." or nama_lama == "Tidak ada menu":
            messagebox.showwarning("Pilihan Kosong", "Pilih menu yang ingin diubah.")
            return
        if not nama_baru or not harga_str or int(harga_str) == 0:
            messagebox.showwarning("Input Kosong", "Nama dan harga tidak boleh kosong.")
            return
        try:
            harga_baru = float(harga_str)
            if harga_baru < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Input Salah", "Harga harus berupa angka positif.")
            return

        del self.menu_data[nama_lama]
        self.menu_data[nama_baru] = harga_baru
        self.simpan_menu()
        messagebox.showinfo("Sukses", f"Menu '{nama_lama}' berhasil diperbarui.")
        self.perbarui_tampilan_menu_pesanan()
        self.perbarui_dropdown_menu_kelola()
        self.entry_nama_menu.delete(0, "end")
        self.entry_harga_menu.delete(0, "end")

    def hapus_menu(self):
        nama_menu_dihapus = self.opsi_menu_kelola.get()
        if nama_menu_dihapus == "Pilih Menu..." or nama_menu_dihapus == "Tidak ada menu":
            messagebox.showwarning("Pilihan Kosong", "Pilih menu yang ingin dihapus.")
            return

        if messagebox.askyesno("Konfirmasi Hapus", f"Anda yakin ingin menghapus menu '{nama_menu_dihapus}'?"):
            del self.menu_data[nama_menu_dihapus]
            self.simpan_menu()
            messagebox.showinfo("Sukses", f"Menu '{nama_menu_dihapus}' telah dihapus.")
            self.perbarui_tampilan_menu_pesanan()
            self.perbarui_dropdown_menu_kelola()
            self.entry_nama_menu.delete(0, "end")
            self.entry_harga_menu.delete(0, "end")

class ToplevelNota(ctk.CTkToplevel):
    def __init__(self, master, teks_nota):
        super().__init__(master)
        self.title("Nota Pembayaran")
        self.geometry("350x450")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        textbox = ctk.CTkTextbox(self, font=("Consolas", 12))
        textbox.pack(expand=True, fill="both", padx=10, pady=10)
        textbox.insert("1.0", teks_nota)
        textbox.configure(state="disabled")

        tombol_tutup = ctk.CTkButton(self, text="Tutup", command=self.destroy)
        tombol_tutup.pack(pady=10, padx=10)

# =====================================================================
#  JALANKAN APLIKASI
# =====================================================================
if __name__ == "__main__":
    app = KasirAngkringanApp()
    app.mainloop()