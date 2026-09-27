# AGY CLI Round-Robin Multi-Akun (Dynamic Manager)

Sistem ini memungkinkan Anda mengelola **Antigravity CLI (`agy`)** secara **sepenuhnya dinamis** dengan banyak akun Google (Gemini Pro / Advanced) secara bergantian (**Round-Robin**).

Tidak ada batasan jumlah akun: Anda bisa menggunakan **2 akun, 3 akun, 5 akun, 10 akun, atau lebih!**

---

## ➕ Cara Menambah Akun Baru Kapan Saja

Jika ke depannya Anda ingin menambah Akun #3, #4, #5, dst., Anda **tidak perlu mengedit kode sama sekali**. Cukup jalankan:

```bash
agy-rr add
```

Sistem akan otomatis:
1. Mendeteksi nomor akun berikutnya.
2. Membuka browser untuk login akun Google baru Anda.
3. Mengambil dan menyimpan kredensialnya ke profil baru.
4. Memasukkannya langsung ke antrean round-robin!

---

## ➖ Cara Menghapus Akun Tertentu

Jika ada akun yang masa langganannya habis atau ingin dikeluarkan:

```bash
agy-rr remove <nomor>
```
*Contoh*: `agy-rr remove 3`  
Nomor akun sisanya akan otomatis dirapikan kembali secara berurutan.

---

## 📊 Cara Cek Kuota (/usage) Semua Akun Sekaligus

```bash
agy-rr usage
```
Akan menampilkan sisa kuota (`Weekly Limit Remaining`, `Five Hour Limit Remaining`) untuk semua akun yang sedang aktif.

---

## 💡 Cara Penggunaan Sehari-hari

### 1. Buka Sesi CLI (Round-Robin Otomatis)
```bash
agy-rr
```
Setiap kali dijalankan, sistem akan memutar giliran akun secara adil:
$$\text{Akun 1} \longrightarrow \text{Akun 2} \longrightarrow \text{Akun 3} \dots \longrightarrow \text{Akun N}$$

### 2. Prompt Singkat / Non-Interaktif (`-p`)
```bash
agy-rr -p "Buat endpoint API login menggunakan Express.js"
```

### 3. Memilih Akun Tertentu Secara Langsung
```bash
# Langsung memakai Akun #2:
agy-rr --acc 2

# Langsung memakai Akun #3 untuk prompt tertentu:
agy-rr --acc 3 -p "Jelaskan konsep Dependency Injection"
```

### 4. Cek Status Akun dan Antrean Giliran
```bash
agy-rr status
```

---

## 🛠️ Ringkasan Perintah

| Perintah | Deskripsi |
|---|---|
| `agy-rr` | Jalankan agy dengan akun giliran berikutnya |
| `agy-rr add` | **Tambah akun baru (dinamis tanpa batas)** |
| `agy-rr remove <nomor>` | **Hapus akun tertentu dan rapikan antrean** |
| `agy-rr usage` | **Cek sisa kuota semua akun sekaligus** |
| `agy-rr usage <nomor>` | Cek sisa kuota akun tertentu saja |
| `agy-rr status` | Lihat daftar akun aktif dan antrean saat ini |
| `agy-rr --acc <nomor>` | Jalankan agy langsung dengan akun tertentu |
| `agy-rr login <nomor>` | Login ulang jika token akun tertentu kedaluwarsa |
