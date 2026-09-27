"""
AGY CLI Round-Robin Manager (Dynamic Multi-Account)
Mengelola multi-akun Gemini Pro untuk Antigravity CLI (agy) secara Dinamis & Round-Robin di Windows.
Mendukung penambahan, penghapusan, dan rotasi tanpa batas jumlah akun (2, 3, 5, 10+ akun).
"""

import sys
import os
import json
import base64
import subprocess
import ctypes
import shutil
import datetime
from ctypes import wintypes
from pathlib import Path

PROFILES_BASE_DIR = Path.home() / ".agy-profiles"
STATE_FILE = PROFILES_BASE_DIR / "state.json"
CREDENTIAL_TARGET = "gemini:antigravity"


# Windows Credential Manager API definitions
class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


advapi32 = ctypes.WinDLL("Advapi32.dll")


def cred_read(target=CREDENTIAL_TARGET):
    """Membaca data kredensial dari Windows Credential Manager."""
    pcred = ctypes.POINTER(CREDENTIAL)()
    if advapi32.CredReadW(target, 1, 0, ctypes.byref(pcred)):
        cred = pcred.contents
        raw = bytes(cred.CredentialBlob[:cred.CredentialBlobSize])
        user = cred.UserName
        advapi32.CredFree(pcred)
        try:
            return json.loads(raw.decode("utf-8")), user
        except Exception:
            return None, user
    return None, None


def cred_write(data_dict, user="antigravity", target=CREDENTIAL_TARGET) -> bool:
    """Menulis data kredensial ke Windows Credential Manager."""
    data_bytes = json.dumps(data_dict).encode("utf-8")
    blob_type = ctypes.c_byte * len(data_bytes)
    blob = blob_type.from_buffer_copy(data_bytes)

    cred = CREDENTIAL()
    cred.Flags = 0
    cred.Type = 1  # CRED_TYPE_GENERIC
    cred.TargetName = target
    cred.Comment = None
    cred.CredentialBlobSize = len(data_bytes)
    cred.CredentialBlob = ctypes.cast(blob, ctypes.POINTER(ctypes.c_byte))
    cred.Persist = 2  # CRED_PERSIST_LOCAL_MACHINE
    cred.AttributeCount = 0
    cred.Attributes = None
    cred.TargetAlias = None
    cred.UserName = user

    return bool(advapi32.CredWriteW(ctypes.byref(cred), 0))


def cred_delete(target=CREDENTIAL_TARGET) -> bool:
    """Menghapus data kredensial dari Windows Credential Manager."""
    return bool(advapi32.CredDeleteW(target, 1, 0))


def get_email_from_cred(cred_data: dict) -> str:
    """Mendapatkan alamat email dari JWT id_token di dalam kredensial."""
    if not cred_data:
        return "Belum login"
    id_token = cred_data.get("id_token", "")
    if id_token and "." in id_token:
        try:
            parts = id_token.split(".")
            if len(parts) >= 2:
                payload = parts[1] + "=" * (-len(parts[1]) % 4)
                info = json.loads(base64.urlsafe_b64decode(payload))
                return info.get("email", "Terkoneksi (Email tidak terbaca)")
        except Exception:
            pass
    return "Terkoneksi"


def ensure_base_dir():
    PROFILES_BASE_DIR.mkdir(parents=True, exist_ok=True)


def get_profile_dir(acc_num: int) -> Path:
    return PROFILES_BASE_DIR / f"account_{acc_num}"


def get_profile_cred_path(acc_num: int) -> Path:
    return get_profile_dir(acc_num) / "credential.json"


def load_account_cred(acc_num: int) -> dict:
    fpath = get_profile_cred_path(acc_num)
    if fpath.exists():
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def save_account_cred(acc_num: int, cred_data: dict):
    p_dir = get_profile_dir(acc_num)
    p_dir.mkdir(parents=True, exist_ok=True)
    fpath = get_profile_cred_path(acc_num)
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(cred_data, f, indent=2)


def get_active_account_numbers() -> list:
    """Mendeteksi semua profil akun yang ada di folder secara otomatis dan berurutan."""
    ensure_base_dir()
    nums = []
    for item in PROFILES_BASE_DIR.iterdir():
        if item.is_dir() and item.name.startswith("account_"):
            num_part = item.name.replace("account_", "")
            if num_part.isdigit():
                nums.append(int(num_part))
    return sorted(nums)


def load_state() -> dict:
    ensure_base_dir()
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_account": 0}


def save_state(state: dict):
    ensure_base_dir()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def pre_populate_onboarding(acc_num: int):
    """Bypass disclaimer onboarding pada profil akun."""
    p_dir = get_profile_dir(acc_num)
    cache_dir = p_dir / ".gemini" / "antigravity-cli" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    with open(cache_dir / "onboarding.json", "w") as f:
        json.dump(
            {
                "consumerOnboardingComplete": True,
                "enterpriseOnboardingComplete": True,
                "onboardingComplete": True,
            },
            f,
        )


def run_login(acc_num: int):
    """Membuka sesi agy untuk login pada nomor akun tertentu."""
    ensure_base_dir()
    p_dir = get_profile_dir(acc_num)
    p_dir.mkdir(parents=True, exist_ok=True)

    pre_populate_onboarding(acc_num)

    env = os.environ.copy()
    env["USERPROFILE"] = str(p_dir)
    env["HOME"] = str(p_dir)

    print(f"\n=======================================================")
    print(f" Membuka sesi login untuk Akun #{acc_num}...")
    print(f" Folder profil: {p_dir}")
    print(f" Silakan login melalui browser yang terbuka.")
    print(f" Setelah selesai dan masuk ke agy, ketik /exit untuk keluar.")
    print(f"=======================================================\n")

    cred_delete()

    try:
        subprocess.run(["agy"], env=env, check=False)
        new_cred, _ = cred_read()
        if new_cred and get_email_from_cred(new_cred) != "Belum login":
            save_account_cred(acc_num, new_cred)
            email = get_email_from_cred(new_cred)
            print(f"\n[OK] Sukses! Akun #{acc_num} berhasil disimpan sebagai: {email}\n")
        else:
            print(f"\n[!] Belum terdeteksi login baru untuk Akun #{acc_num}.")
    except FileNotFoundError:
        print("[ERROR] 'agy' executable tidak ditemukan di PATH.")
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan: {e}")


def add_account():
    """Menambahkan akun baru secara dinamis."""
    active_nums = get_active_account_numbers()
    next_num = (max(active_nums) + 1) if active_nums else 1
    print(f"[+] Menyiapkan Akun baru (#{next_num})...")
    run_login(next_num)


def remove_account(target_acc: int):
    """Menghapus akun tertentu dan merapikan kembali urutan nomor akun."""
    active_nums = get_active_account_numbers()
    if target_acc not in active_nums:
        print(f"[ERROR] Akun #{target_acc} tidak ditemukan. Akun aktif saat ini: {active_nums}")
        return

    email = get_email_from_cred(load_account_cred(target_acc))
    print(f"[-] Menghapus Akun #{target_acc} ({email})...")

    # Hapus folder target
    shutil.rmtree(get_profile_dir(target_acc), ignore_errors=True)

    # Re-index sisa akun agar tetap berurutan 1, 2, 3...
    remaining_nums = [n for n in active_nums if n != target_acc]
    for new_idx, old_num in enumerate(remaining_nums, start=1):
        if old_num != new_idx:
            old_dir = get_profile_dir(old_num)
            new_dir = get_profile_dir(new_idx)
            if new_dir.exists():
                shutil.rmtree(new_dir, ignore_errors=True)
            old_dir.rename(new_dir)

    # Reset state round-robin jika perlu
    state = load_state()
    state["last_account"] = 0
    save_state(state)

    new_active = get_active_account_numbers()
    print(f"[OK] Akun berhasil dihapus. Sekarang tersisa {len(new_active)} akun aktif.")
    show_status()


def format_indo_time(iso_str: str) -> str:
    """Mengubah timestamp ISO UTC menjadi format waktu lokal Indonesia (WIB)."""
    if not iso_str:
        return ""
    try:
        clean = iso_str.strip().replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(clean)
        local_dt = dt.astimezone()
        bulan_indo = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        nama_bulan = bulan_indo[local_dt.month - 1]
        return local_dt.strftime(f"%d {nama_bulan} %Y, %H:%M WIB")
    except Exception:
        return iso_str


def check_usage(target_acc: int = None):
    """Mengecek penggunaan kuota (/usage) untuk semua akun atau akun tertentu."""
    active_nums = get_active_account_numbers()
    if not active_nums:
        print("[!] Belum ada akun yang terdaftar. Jalankan 'agy-rr add' untuk menambahkan akun.")
        return

    targets = [target_acc] if target_acc else active_nums

    print("\n======================= CEK USAGE KUOTA =======================")
    for num in targets:
        cred = load_account_cred(num)
        email = get_email_from_cred(cred) if cred else "Belum login"
        print(f"\n[Akun #{num}: {email}]")
        if not cred:
            print(f"  Status: Belum login. Jalankan 'agy-rr login {num}'")
            continue

        p_dir = get_profile_dir(num)
        env = os.environ.copy()
        env["USERPROFILE"] = str(p_dir)
        env["HOME"] = str(p_dir)
        cred_write(cred)

        try:
            res = subprocess.run(
                ["agy", "--print", "/usage"],
                env=env,
                capture_output=True,
                text=True,
                timeout=25,
            )
            out = res.stdout.strip()
            err = res.stderr.strip()
            if res.returncode == 0 and out:
                lines = out.splitlines()
                for line in lines:
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        model_grp, limit_type, remaining = parts[0], parts[1], parts[2]
                        reset_raw = parts[3] if len(parts) > 3 else ""
                        reset_formatted = f"  (Reset: {format_indo_time(reset_raw)})" if reset_raw else ""
                        print(f"  - {model_grp.ljust(22)} | {limit_type.ljust(26)} : {remaining.rjust(5)}{reset_formatted}")
                    else:
                        print(f"  {line}")
            else:
                combined = out + " " + err
                if "Authentication required" in combined or "visit the URL" in combined:
                    print(f"  [!] Token kedaluwarsa / perlu re-login. Jalankan 'agy-rr login {num}'")
                else:
                    print(f"  {out or err or 'Tidak ada data usage'}")
        except subprocess.TimeoutExpired:
            print("  Waktu pengecekan habis (timeout).")
        except Exception as e:
            print(f"  Gagal mengambil usage: {e}")
    print("\n===============================================================\n")


def show_status():
    """Tampilkan status semua akun aktif dan giliran berikutnya."""
    active_nums = get_active_account_numbers()
    if not active_nums:
        print("\n[!] Belum ada akun yang terdaftar. Ketik 'agy-rr add' untuk login akun baru.\n")
        return

    state = load_state()
    last_acc = state.get("last_account", 0)

    # Hitung next account dalam daftar active_nums
    if last_acc in active_nums:
        curr_pos = active_nums.index(last_acc)
        next_acc = active_nums[(curr_pos + 1) % len(active_nums)]
    else:
        next_acc = active_nums[0]

    print("\n================ STATUS AKUN ROUND-ROBIN ================")
    for num in active_nums:
        cred = load_account_cred(num)
        email = get_email_from_cred(cred) if cred else "Belum login"
        is_last = " <-- Terakhir digunakan" if num == last_acc else ""
        is_next = " [NEXT]" if num == next_acc else ""
        print(f" Akun #{num}: {email}{is_last}{is_next}")
    print("---------------------------------------------------------")
    print(f" Total Akun Aktif        : {len(active_nums)} akun")
    print(f" Akun giliran berikutnya : Akun #{next_acc}")
    print("=========================================================\n")


def execute_agy(acc_num: int, args: list) -> int:
    """Terapkan kredensial akun tertentu lalu jalankan agy dengan profil terisolasi."""
    cred = load_account_cred(acc_num)
    if not cred:
        print(f"[ERROR] Akun #{acc_num} belum login!", file=sys.stderr)
        print(f"Jalankan 'agy-rr login {acc_num}' terlebih dahulu.", file=sys.stderr)
        return 1

    email = get_email_from_cred(cred)
    p_dir = get_profile_dir(acc_num)
    p_dir.mkdir(parents=True, exist_ok=True)

    # Tulis kredensial akun ini ke Windows Credential Manager
    cred_write(cred)

    # Siapkan environment terisolasi untuk profil ini
    env = os.environ.copy()
    env["USERPROFILE"] = str(p_dir)
    env["HOME"] = str(p_dir)

    # Info banner jika bukan mode raw stream
    if not any(arg in ["--output-format", "stream-json"] for arg in args):
        print(f"[agy-rr] Menggunakan Akun #{acc_num} ({email})...", file=sys.stderr)

    try:
        proc = subprocess.run(["agy"] + args, env=env)
        # Perbarui file kredensial jika token di-refresh selama sesi
        updated_cred, _ = cred_read()
        if updated_cred:
            save_account_cred(acc_num, updated_cred)
        return proc.returncode
    except FileNotFoundError:
        print("[ERROR] 'agy' executable tidak ditemukan di PATH.", file=sys.stderr)
        return 1


def main():
    args = sys.argv[1:]

    if len(args) == 0:
        pass
    elif args[0] in ["--help", "-h", "help"]:
        print("""
Penggunaan Dinamis agy-rr:
  agy-rr [argumen agy...]               Jalankan agy dengan giliran Round-Robin otomatis
  agy-rr add                            Tambah akun baru (Akun #3, #4, #5, dst.)
  agy-rr remove <nomor>                 Hapus akun tertentu (contoh: agy-rr remove 2)
  agy-rr usage [nomor]                  Cek sisa kuota (/usage) semua akun atau akun tertentu
  agy-rr status                         Lihat status semua akun dan antrean giliran
  agy-rr --acc <nomor> [argumen agy...] Jalankan agy langsung dengan akun nomor tertentu
  agy-rr login <nomor>                  Re-login pada akun tertentu

Contoh:
  agy-rr add                            Tambah akun baru ke dalam sistem
  agy-rr                                Buka agy interaktif (bergantian akun otomatis)
  agy-rr usage                          Cek kuota semua akun sekaligus
  agy-rr remove 3                       Hapus Akun #3
  agy-rr --acc 2                        Pakai Akun #2 saja
        """)
        return

    elif args[0] == "add":
        add_account()
        return

    elif args[0] in ["remove", "logout", "delete"]:
        if len(args) < 2 or not args[1].isdigit():
            print("[!] Harap sertakan nomor akun yang ingin dihapus. Contoh: agy-rr remove 2")
            return
        remove_account(int(args[1]))
        return

    elif args[0] == "login":
        if len(args) < 2 or not args[1].isdigit():
            print("[!] Harap sertakan nomor akun. Contoh: agy-rr login 3")
            return
        run_login(int(args[1]))
        return

    elif args[0] == "usage":
        target = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        check_usage(target)
        return

    elif args[0] == "status":
        show_status()
        return

    elif args[0] == "--acc":
        if len(args) < 2 or not args[1].isdigit():
            print("[!] Harap tentukan nomor akun setelah --acc. Contoh: agy-rr --acc 2")
            return
        target_acc = int(args[1])
        agy_args = args[2:]
        sys.exit(execute_agy(target_acc, agy_args))

    # Mode Round-Robin Otomatis Dinamis
    active_nums = get_active_account_numbers()
    if not active_nums:
        print("[!] Belum ada akun yang terdaftar. Ketik 'agy-rr add' untuk login akun pertama.")
        return

    state = load_state()
    last_acc = state.get("last_account", 0)

    # Hitung akun giliran berikutnya dari daftar akun aktif
    if last_acc in active_nums:
        curr_pos = active_nums.index(last_acc)
        next_acc = active_nums[(curr_pos + 1) % len(active_nums)]
    else:
        next_acc = active_nums[0]

    # Simpan state akun terakhir
    state["last_account"] = next_acc
    save_state(state)

    # Jalankan perintah agy
    exit_code = execute_agy(next_acc, args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
