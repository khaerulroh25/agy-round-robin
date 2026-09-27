# AGY CLI Round-Robin Multi-Akun (Dynamic Manager)

Sistem ini memungkinkan Anda mengelola **Antigravity CLI (`agy`)** secara **sepenuhnya dinamis** dengan banyak akun Google (Gemini Pro / Advanced) secara bergantian (**Round-Robin**).

Tidak ada batasan jumlah akun: Anda bisa menggunakan **2 akun, 3 akun, 5 akun, 10 akun, atau lebih!**

---

## 💻 Panduan Pasang di Laptop / Komputer Baru

Jika Anda ingin menggunakan sistem ini di laptop lain:

### Langkah 1: Prasyarat di Laptop Baru
1. Pastikan **Antigravity CLI (`agy`)** sudah terpasang.
2. Pastikan **Python** sudah terpasang.

### Langkah 2: Salin Folder Proyek Ini
Salin folder `agy-round-robin` ini ke laptop baru Anda (bisa lewat Flashdisk, Git repo, zip, dll.).

### Langkah 3: Jalankan Installer Otomatis
Buka folder `agy-round-robin` di laptop baru, lalu:
* Cukup **klik dua kali (*double-click*) file `install.bat`**  
  *(Atau jalankan `.\install.ps1` lewat PowerShell)*.

### Langkah 4: Login Akun Anda
Buka terminal baru di laptop baru, lalu tambahkan akun Anda satu per satu:
```bash
agy-rr add    # Untuk Akun #1
agy-rr add    # Untuk Akun #2
agy-rr add    # Untuk Akun #3 (jika ada)
```

Selesai! `agy-rr` langsung siap digunakan di laptop baru.

---

## ➕ Cara Menambah Akun Baru Kapan Saja

```bash
agy-rr add
```
Sistem akan otomatis membuka browser untuk login akun Google baru dan memasukkannya ke antrean round-robin.

---

## ➖ Cara Menghapus Akun Tertentu

```bash
agy-rr remove <nomor>
```
*Contoh:* `agy-rr remove 3` (sisa akun otomatis dirapikan kembali urutannya).

---

## 📊 Cara Cek Kuota (/usage) Semua Akun Sekaligus

```bash
agy-rr usage
```
Menampilkan sisa kuota dan jam reset waktu lokal Indonesia (WIB) untuk semua akun.

---

## 🛠️ Ringkasan Perintah

| Perintah | Deskripsi |
|---|---|
| `agy-rr` | Jalankan agy dengan akun giliran berikutnya |
| `agy-rr add` | **Tambah akun baru ke antrean** |
| `agy-rr remove <nomor>` | **Hapus akun dan rapikan antrean** |
| `agy-rr usage` | **Cek kuota seluruh akun (WIB)** |
| `agy-rr status` | Lihat daftar akun aktif dan antrean |
| `agy-rr --acc <nomor>` | Jalankan agy langsung dengan akun tertentu |
| `agy-rr login <nomor>` | Login ulang jika token akun kedaluwarsa |
