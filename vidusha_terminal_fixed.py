import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os, sqlite3, hashlib, secrets, socket, platform
import subprocess, threading, datetime, urllib.parse, urllib.request, webbrowser, sys

APP_NAME = "VIDUSHA | SUPER RED CYBER TERMINAL"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "vidusha.db")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
BG, PANEL, RED, WHITE, MUTED = "#080808", "#151515", "#ff3030", "#f2f2f2", "#aaaaaa"

def stamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def db():
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, salt BLOB NOT NULL, password_hash BLOB NOT NULL, created_at TEXT NOT NULL)")
    con.commit()
    return con

def password_hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 240000)

def create_user(username, password):
    username = username.strip()
    if len(username) < 3 or len(username) > 24:
        raise ValueError("Username must be 3–24 characters.")
    if not username.replace("_", "").isalnum():
        raise ValueError("Use only letters, numbers and underscore in username.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    salt = secrets.token_bytes(16)
    con = db()
    try:
        con.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, salt, password_hash(password, salt), stamp()))
        con.commit()
    except sqlite3.IntegrityError:
        raise ValueError("That username already exists. Choose another one.")
    finally:
        con.close()

def check_login(username, password):
    con = db()
    row = con.execute("SELECT salt, password_hash FROM users WHERE username=?", (username.strip(),)).fetchone()
    con.close()
    return bool(row and secrets.compare_digest(password_hash(password, row[0]), row[1]))

class VidushaApp:
    def __init__(self, root, username):
        self.root, self.username = root, username
        self.root.title(APP_NAME)
        self.root.geometry("1120x760")
        self.root.minsize(920, 640)
        self.root.configure(bg=BG)
        os.makedirs(REPORT_DIR, exist_ok=True)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background="#252525", foreground=WHITE, padding=(13, 9), font=("Consolas", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#761414")], foreground=[("selected", "white")])
        self.output = {}
        self.build_ui()
        self.log(f"User {username} signed in.")

    def log(self, message):
        with open(os.path.join(REPORT_DIR, "activity.log"), "a", encoding="utf-8") as f:
            f.write(f"[{stamp()}] {message}\n")

    def save_report(self, name, content):
        safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in name)
        path = os.path.join(REPORT_DIR, datetime.datetime.now().strftime("%Y%m%d_%H%M%S_") + safe + ".txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{APP_NAME}\n{name}\nCreated: {stamp()}\n\n{content}\n")
        return path

    def make_output(self, parent, key, height=15):
        box = tk.Text(parent, height=height, bg="#030303", fg="#dddddd", insertbackground=RED,
                      font=("Consolas", 10), wrap="word", relief="flat", padx=10, pady=10)
        box.pack(fill="both", expand=True, padx=12, pady=10)
        self.output[key] = box
        return box

    def write(self, key, value):
        w = self.output.get(key)
        if w:
            w.delete("1.0", "end")
            w.insert("end", str(value))

    def run_task(self, fn):
        self.status.config(text="● WORKING", fg="#ffd166")
        def worker():
            try:
                fn()
            except Exception as exc:
                self.root.after(0, lambda err=str(exc): messagebox.showerror("Tool error", err))
            finally:
                self.root.after(0, lambda: self.status.config(text=f"● SYSTEM READY     USER: {self.username}", fg="#59e391"))
        threading.Thread(target=worker, daemon=True).start()

    def heading(self, frame, text):
        tk.Label(frame, text=text, bg=BG, fg=RED, font=("Consolas", 15, "bold")).pack(anchor="w", padx=15, pady=12)

    def button(self, parent, text, command):
        tk.Button(parent, text=text, command=command, bg="#741111", fg="white", activebackground=RED,
                  activeforeground="white", relief="flat", font=("Consolas", 10, "bold"), padx=13, pady=8).pack(anchor="w", padx=15, pady=8)

    def build_ui(self):
        header = tk.Frame(self.root, bg="#1a0505", height=90)
        header.pack(fill="x"); header.pack_propagate(False)
        tk.Label(header, text="▰  VIDUSHA", bg="#1a0505", fg=RED, font=("Consolas", 25, "bold")).pack(anchor="w", padx=22, pady=(10, 0))
        tk.Label(header, text="SUPER RED CYBER TERMINAL V∞  |  DEFENSIVE TOOLS  |  NO AI", bg="#1a0505", fg=WHITE, font=("Consolas", 9)).pack(anchor="w", padx=25)
        self.status = tk.Label(self.root, text=f"● SYSTEM READY     USER: {self.username}", bg=BG, fg="#59e391", font=("Consolas", 10, "bold"), anchor="w")
        self.status.pack(fill="x", padx=22, pady=8)
        self.tabs = ttk.Notebook(self.root); self.tabs.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        pages = [("Dashboard", self.dashboard_tab), ("Network", self.network_tab), ("Local Ports", self.ports_tab),
                 ("Wi-Fi / IP", self.wifi_tab), ("DNS", self.dns_tab), ("Website", self.website_tab),
                 ("Password", self.password_tab), ("File Hash", self.file_tab), ("Processes", self.process_tab),
                 ("Web Browser", self.browser_tab), ("3D Game", self.game_tab), ("Reports", self.reports_tab)]
        for name, builder in pages:
            frame = tk.Frame(self.tabs, bg=BG); self.tabs.add(frame, text=name); builder(frame)
        tk.Label(self.root, text="Only use security tools on devices, networks and websites you own or have permission to test.",
                 bg=BG, fg=MUTED, font=("Consolas", 8)).pack(fill="x", padx=18, pady=(0, 8))

    def local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("192.0.2.1", 80)); return s.getsockname()[0]
        except OSError:
            return "Unavailable"
        finally:
            s.close()

    def dashboard_tab(self, frame):
        self.heading(frame, "VIDUSHA SYSTEM DASHBOARD")
        details = (f"Welcome, {self.username}!\n\nComputer: {socket.gethostname()}\nOperating system: {platform.platform()}\n"
                   f"Python: {platform.python_version()}\nLocal IP: {self.local_ip()}\nAccount database: vidusha.db\n"
                   f"Reports folder: {REPORT_DIR}\n\nModules: local network information, localhost port check, DNS lookup, "
                   "HTTPS header check, sample password checker, SHA-256 file checker, process viewer, web browser and optional 3D game.")
        tk.Label(frame, text=details, bg=BG, fg=WHITE, justify="left", font=("Consolas", 12)).pack(anchor="w", padx=22, pady=10)
        self.button(frame, "REFRESH DASHBOARD", lambda: messagebox.showinfo("Dashboard", f"Computer: {socket.gethostname()}\nLocal IP: {self.local_ip()}"))

    def network_tab(self, frame):
        self.heading(frame, "LOCAL NETWORK ARP TABLE")
        tk.Label(frame, text="Shows entries already known to Windows; it does not scan outside your local network.", bg=BG, fg=MUTED).pack(anchor="w", padx=15)
        self.button(frame, "VIEW ARP TABLE", self.arp_scan); self.make_output(frame, "network")

    def arp_scan(self):
        def task():
            p = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=10)
            result = p.stdout or p.stderr or "No ARP entries."
            self.root.after(0, lambda: self.write("network", result)); self.save_report("arp_table", result); self.log("Viewed ARP table")
        self.run_task(task)

    def ports_tab(self, frame):
        self.heading(frame, "LOCALHOST PORT CHECKER")
        tk.Label(frame, text="Checks common TCP ports on this computer only (127.0.0.1).", bg=BG, fg=MUTED).pack(anchor="w", padx=15)
        self.button(frame, "CHECK THIS PC", self.local_ports); self.make_output(frame, "ports")

    def local_ports(self):
        def task():
            lines = ["Target: 127.0.0.1", ""]
            for port in [21,22,23,25,53,80,110,135,139,143,443,445,3306,3389,5000,8000,8080]:
                with socket.socket() as s:
                    s.settimeout(.2); state = "OPEN" if s.connect_ex(("127.0.0.1", port)) == 0 else "closed"
                lines.append(f"{port:5}  {state}")
            result = "\n".join(lines); self.root.after(0, lambda: self.write("ports", result))
            self.save_report("localhost_ports", result); self.log("Checked localhost ports")
        self.run_task(task)

    def wifi_tab(self, frame):
        self.heading(frame, "WI-FI / IP INFORMATION")
        self.button(frame, "GET NETWORK DETAILS", self.wifi_info); self.make_output(frame, "wifi")

    def wifi_info(self):
        def task():
            chunks = [f"Hostname: {socket.gethostname()}", f"Local IP: {self.local_ip()}"]
            if os.name == "nt":
                for cmd in [["ipconfig"], ["netsh", "wlan", "show", "interfaces"]]:
                    p = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
                    chunks.append("\n$ " + " ".join(cmd) + "\n" + (p.stdout or p.stderr))
            result = "\n".join(chunks); self.root.after(0, lambda: self.write("wifi", result))
            self.save_report("wifi_details", result); self.log("Viewed Wi-Fi/IP details")
        self.run_task(task)

    def dns_tab(self, frame):
        self.heading(frame, "DNS LOOKUP")
        row = tk.Frame(frame, bg=BG); row.pack(fill="x", padx=15)
        self.dns_entry = tk.Entry(row, bg=PANEL, fg=WHITE, insertbackground=RED, font=("Consolas", 11))
        self.dns_entry.pack(side="left", fill="x", expand=True, ipady=7); self.dns_entry.insert(0, "example.com")
        tk.Button(row, text="LOOK UP", command=self.dns_lookup, bg="#741111", fg="white", relief="flat", padx=12).pack(side="left", padx=8)
        self.make_output(frame, "dns")

    def dns_lookup(self):
        host = self.dns_entry.get().strip()
        if not host or "/" in host or " " in host:
            messagebox.showwarning("DNS", "Enter a domain such as example.com"); return
        def task():
            result = f"DNS results for {host}\n\n" + "\n".join(sorted({r[4][0] for r in socket.getaddrinfo(host, None)}))
            self.root.after(0, lambda: self.write("dns", result)); self.save_report("dns_lookup", result); self.log(f"DNS lookup {host}")
        self.run_task(task)

    def website_tab(self, frame):
        self.heading(frame, "HTTPS SECURITY HEADER INSPECTOR")
        tk.Label(frame, text="Checks response headers only. Use websites you own or are allowed to assess.", bg=BG, fg=MUTED).pack(anchor="w", padx=15)
        row = tk.Frame(frame, bg=BG); row.pack(fill="x", padx=15, pady=8)
        self.site_entry = tk.Entry(row, bg=PANEL, fg=WHITE, insertbackground=RED, font=("Consolas", 11))
        self.site_entry.pack(side="left", fill="x", expand=True, ipady=7); self.site_entry.insert(0, "https://example.com")
        tk.Button(row, text="INSPECT", command=self.inspect_site, bg="#741111", fg="white", relief="flat", padx=12).pack(side="left", padx=8)
        self.make_output(frame, "website")

    def inspect_site(self):
        raw = self.site_entry.get().strip(); parsed = urllib.parse.urlparse(raw)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            messagebox.showwarning("Website", "Enter a valid HTTPS address, e.g. https://example.com"); return
        def task():
            req = urllib.request.Request(raw, headers={"User-Agent": "VIDUSHA-Security-Inspector/1.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                names = ["Strict-Transport-Security","Content-Security-Policy","X-Content-Type-Options","X-Frame-Options","Referrer-Policy","Permissions-Policy"]
                lines = [f"URL: {raw}", f"HTTP status: {response.status}", "", "Security headers:"]
                lines += [f"{n}: {response.headers.get(n) or 'NOT PRESENT'}" for n in names]
            result = "\n".join(lines); self.root.after(0, lambda: self.write("website", result))
            self.save_report("website_headers", result); self.log(f"Inspected HTTPS headers for {parsed.hostname}")
        self.run_task(task)

    def password_tab(self, frame):
        self.heading(frame, "PASSWORD STRENGTH CHECKER")
        tk.Label(frame, text="Use a sample password, not your real password. It is not saved or sent.", bg=BG, fg=MUTED).pack(anchor="w", padx=15)
        row = tk.Frame(frame, bg=BG); row.pack(fill="x", padx=15, pady=10)
        self.pass_entry = tk.Entry(row, show="*", bg=PANEL, fg=WHITE, insertbackground=RED)
        self.pass_entry.pack(side="left", fill="x", expand=True, ipady=7)
        tk.Button(row, text="ANALYZE", command=self.audit_password, bg="#741111", fg="white", relief="flat", padx=12).pack(side="left", padx=8)
        self.make_output(frame, "password", 10)

    def audit_password(self):
        p = self.pass_entry.get()
        if not p:
            messagebox.showwarning("Password", "Enter a sample password."); return
        checks = [("At least 12 characters", len(p)>=12), ("Lowercase letter", any(c.islower() for c in p)),
                  ("Uppercase letter", any(c.isupper() for c in p)), ("Number", any(c.isdigit() for c in p)),
                  ("Symbol", any(not c.isalnum() for c in p))]
        score = sum(ok for _,ok in checks)
        result = f"Strength: {['Very weak','Weak','Fair','Fair','Strong','Very strong'][score]} ({score}/5)\n\n"
        result += "\n".join(("PASS  " if ok else "MISS  ")+label for label,ok in checks)
        self.write("password", result); self.save_report("password_strength", result); self.log("Ran sample password check")
        self.pass_entry.delete(0, "end")

    def file_tab(self, frame):
        self.heading(frame, "FILE INTEGRITY – SHA-256")
        self.button(frame, "SELECT FILE AND HASH", self.hash_file); self.make_output(frame, "file", 12)

    def hash_file(self):
        path = filedialog.askopenfilename()
        if not path: return
        def task():
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1024*1024), b""): h.update(chunk)
            result = f"File: {path}\nSHA-256: {h.hexdigest()}"
            self.root.after(0, lambda: self.write("file", result)); self.save_report("file_sha256", result); self.log("Calculated file SHA-256")
        self.run_task(task)

    def process_tab(self, frame):
        self.heading(frame, "RUNNING PROCESSES (READ ONLY)")
        self.button(frame, "VIEW PROCESSES", self.processes); self.make_output(frame, "processes")

    def processes(self):
        def task():
            p = subprocess.run(["tasklist"] if os.name=="nt" else ["ps","-A"], capture_output=True, text=True, timeout=15)
            result = p.stdout or p.stderr or "No process data."
            self.root.after(0, lambda: self.write("processes", result)); self.save_report("processes", result); self.log("Viewed process list")
        self.run_task(task)

    def browser_tab(self, frame):
        self.heading(frame, "VIDUSHA WEB BROWSER")
        tk.Label(frame, text="Enter a website and open it in your default Windows browser.", bg=BG, fg=MUTED).pack(anchor="w", padx=15)
        row = tk.Frame(frame, bg=BG); row.pack(fill="x", padx=15, pady=10)
        self.browser_entry = tk.Entry(row, bg=PANEL, fg=WHITE, insertbackground=RED, font=("Consolas", 11))
        self.browser_entry.pack(side="left", fill="x", expand=True, ipady=8); self.browser_entry.insert(0, "https://www.google.com")
        tk.Button(row, text="OPEN WEBSITE", command=self.open_browser, bg="#741111", fg="white", relief="flat", padx=12, pady=8).pack(side="left", padx=8)
        tk.Label(frame, text="Uses the browser installed on Windows. This app does not collect browsing history.", bg=BG, fg=MUTED).pack(anchor="w", padx=15, pady=8)

    def open_browser(self):
        value = self.browser_entry.get().strip()
        if not value: return
        if "://" not in value: value = "https://" + value
        parsed = urllib.parse.urlparse(value)
        if parsed.scheme not in ("http","https") or not parsed.hostname:
            messagebox.showwarning("Browser", "Enter a valid http or https website."); return
        webbrowser.open(value); self.log(f"Opened browser URL: {parsed.hostname}")

    def game_tab(self, frame):
        self.heading(frame, "VIDUSHA 3D CYBER DODGE")
        tk.Label(frame, text="Optional 3D mini-game powered by Ursina. It opens in a separate game window.\n"
                 "Move with W A S D or arrow keys. Avoid the red blocks. Press ESC to quit.",
                 bg=BG, fg=WHITE, justify="left", font=("Consolas", 11)).pack(anchor="w", padx=18, pady=10)
        self.button(frame, "START 3D GAME", self.start_game)
        tk.Label(frame, text="Install the 3D engine using:\npython -m pip install ursina",
                 bg=BG, fg=MUTED, justify="left", font=("Consolas", 10)).pack(anchor="w", padx=18, pady=8)

    def start_game(self):
        try:
            import ursina  # noqa: F401
        except ImportError:
            messagebox.showinfo(
                "3D Game",
                "Install the game engine first:\n\npy -3.13 -m pip install ursina\n\nThen restart VIDUSHA and press START 3D GAME."
            )
            return

        # Ursina/Panda3D must run on the main thread. Start it in a separate
        # process so the Tkinter app can remain responsive.
        game_path = os.path.join(BASE_DIR, "VIDUSHA_3D_GAME.py")
        game_code = """from ursina import *
import random

app = Ursina()
window.title = 'VIDUSHA 3D CYBER DODGE'
window.color = color.rgb(8, 8, 8)

player = Entity(model='cube', color=color.azure, scale=(1, 1, 1),
                position=(0, .6, 0))
Entity(model='plane', color=color.rgb(30, 30, 30), scale=20, collider='box')
camera.position = (0, 12, -18)
camera.rotation_x = 28

score = 0
score_text = Text(text='SCORE: 0', position=(-.85, .45),
                  scale=1.5, color=color.red)
ended = False
blocks = [
    Entity(model='cube', color=color.red, scale=1,
           position=(random.randint(-7, 7), .6, random.randint(5, 24)),
           collider='box')
    for _ in range(9)
]

def update():
    global score, ended
    if ended:
        return

    dx = held_keys['d'] - held_keys['a'] + held_keys['right'] - held_keys['left']
    dz = held_keys['w'] - held_keys['s'] + held_keys['up'] - held_keys['down']
    player.x = clamp(player.x + dx * time.dt * 8, -8, 8)
    player.z = clamp(player.z + dz * time.dt * 8, -8, 8)

    for block in blocks:
        block.z -= time.dt * 7
        if block.z < -10:
            block.position = (random.randint(-7, 7), .6, random.randint(15, 30))
            score += 1
            score_text.text = 'SCORE: ' + str(score)
        if player.intersects(block).hit:
            ended = True
            Text(text='GAME OVER - CLOSE THIS WINDOW',
                 origin=(0, 0), scale=1.5, color=color.red)

app.run()
"""
        try:
            with open(game_path, "w", encoding="utf-8") as game_file:
                game_file.write(game_code)

            running = getattr(self, "game_process", None)
            if running is not None and running.poll() is None:
                messagebox.showinfo("3D Game", "The 3D game is already running.")
                return

            self.game_process = subprocess.Popen(
                [sys.executable, game_path],
                cwd=BASE_DIR
            )
            self.log("Started 3D game in a separate process")
        except Exception as exc:
            messagebox.showerror("3D Game Error", str(exc))

    def reports_tab(self, frame):
        self.heading(frame, "REPORTS AND ACTIVITY LOG")
        tk.Label(frame, text=f"Reports are saved locally in:\n{REPORT_DIR}", bg=BG, fg=WHITE, justify="left").pack(anchor="w", padx=15)
        self.button(frame, "OPEN REPORT FOLDER", lambda: os.startfile(REPORT_DIR) if os.name=="nt" else webbrowser.open(REPORT_DIR))
        self.make_output(frame, "reports", 8)
        self.write("reports", "Generated reports and activity.log are stored locally.")

class LoginWindow:
    def __init__(self, root):
        self.root = root
        root.title("VIDUSHA | LOGIN"); root.geometry("470x440"); root.resizable(False,False); root.configure(bg=BG)
        db().close()
        tk.Label(root, text="VIDUSHA", bg=BG, fg=RED, font=("Consolas",28,"bold")).pack(pady=(28,4))
        tk.Label(root, text="SUPER RED CYBER TERMINAL V∞", bg=BG, fg=WHITE, font=("Consolas",10)).pack(pady=(0,22))
        form = tk.Frame(root,bg=BG); form.pack(fill="x",padx=55)
        tk.Label(form,text="USERNAME",bg=BG,fg=RED,font=("Consolas",10,"bold")).pack(anchor="w")
        self.username = tk.Entry(form,bg=PANEL,fg=WHITE,insertbackground=RED,font=("Consolas",12))
        self.username.pack(fill="x",ipady=7,pady=(4,14))
        tk.Label(form,text="PASSWORD",bg=BG,fg=RED,font=("Consolas",10,"bold")).pack(anchor="w")
        self.password = tk.Entry(form,show="*",bg=PANEL,fg=WHITE,insertbackground=RED,font=("Consolas",12))
        self.password.pack(fill="x",ipady=7,pady=(4,18))
        tk.Button(form,text="LOGIN",command=self.login,bg="#8b1111",fg="white",activebackground=RED,relief="flat",font=("Consolas",11,"bold"),pady=9).pack(fill="x",pady=4)
        tk.Button(form,text="CREATE NEW ACCOUNT",command=self.create_account,bg="#292929",fg=WHITE,relief="flat",font=("Consolas",10,"bold"),pady=9).pack(fill="x",pady=4)
        tk.Label(root,text="Accounts are stored locally in vidusha.db.",bg=BG,fg=MUTED,font=("Consolas",8)).pack(pady=16)

    def login(self):
        u,p = self.username.get(),self.password.get()
        if check_login(u,p):
            self.root.destroy()
            main = tk.Tk(); VidushaApp(main,u); main.mainloop()
        else:
            messagebox.showerror("Login failed","Incorrect username or password.")

    def create_account(self):
        try:
            create_user(self.username.get(),self.password.get())
            messagebox.showinfo("Account created","Account created! You can now press LOGIN.")
            self.password.delete(0,"end")
        except ValueError as exc:
            messagebox.showwarning("Create account",str(exc))

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
