import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Menu
import urllib.request
import urllib.parse
import json
import threading
import time

SERVER_URL = "http://localhost:8080"

class C2Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("C2 RED // TEAMSERVER [CLASSIFIED]")
        self.root.geometry("900x600")
        self.root.configure(bg="#050505")
        
        # Cyberpunk Styles
        style = ttk.Style()
        style.theme_use("clam")
        
        # Treeview Colors
        style.configure("Treeview", 
                        background="#111", 
                        foreground="#00ff00", 
                        fieldbackground="#111", 
                        font=("Consolas", 10))
        style.configure("Treeview.Heading", 
                        background="#222", 
                        foreground="#00ff00", 
                        font=("Consolas", 10, "bold"))
        style.map("Treeview", background=[("selected", "#004400")])
        
        self.setup_ui()
        
        # Start Poller
        self.running = True
        self.poller_thread = threading.Thread(target=self.poll_server)
        self.poller_thread.daemon = True
        self.poller_thread.start()

    def setup_ui(self):
        # 1. Header with "Matrix" vibe
        header = tk.Label(self.root, text="::: C2 RED COMMAND CENTER :::", 
                         bg="#050505", fg="#00cc00", font=("Consolas", 14, "bold"))
        header.pack(pady=5)

        # 2. Split Pane
        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#050505", sashwidth=4, sashrelief=tk.RAISED)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 3. Sidebar (Agents)
        sidebar = tk.Frame(paned, bg="#111")
        paned.add(sidebar, minsize=250)
        
        tk.Label(sidebar, text="[ ACTIVE AGENTS ]", fg="#00aa00", bg="#111", font=("Consolas", 10)).pack(fill=tk.X, pady=2)
        
        columns = ("id", "ip", "status")
        self.tree = ttk.Treeview(sidebar, columns=columns, show="headings", height=20)
        self.tree.heading("id", text="ID")
        self.tree.heading("ip", text="IP Address")
        self.tree.heading("status", text="State")
        
        self.tree.column("id", width=50)
        self.tree.column("ip", width=100)
        self.tree.column("status", width=60)
        
        # Row Colors
        self.tree.tag_configure("online", foreground="#00ff00")
        self.tree.tag_configure("offline", foreground="#555555")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Context Menu
        self.context_menu = Menu(self.root, tearoff=0, bg="#222", fg="#00ff00")
        self.context_menu.add_command(label="Interact (Select)", command=self.interact_agent)
        self.context_menu.add_command(label="Whoami", command=lambda: self.quick_cmd("whoami"))
        self.context_menu.add_command(label="Kill Agent", command=lambda: self.quick_cmd("exit"), foreground="red")
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # 4. Main Area (Console)
        main_area = tk.Frame(paned, bg="#050505")
        paned.add(main_area, minsize=500)
        
        tk.Label(main_area, text="[ TERMINAL LOG ]", fg="#00aa00", bg="#050505", font=("Consolas", 10)).pack(fill=tk.X, pady=2)
        
        self.log_area = scrolledtext.ScrolledText(main_area, bg="#080808", fg="#00dd00", 
                                                  font=("Consolas", 10), insertbackground="#00ff00",
                                                  borderwidth=0, state='normal')
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.insert(tk.END, "[*] SYSTEM ONLINE. LISTENING ON :8080...\n")
        
        # Input
        input_frame = tk.Frame(main_area, bg="#222")
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text=" C2> ", bg="#222", fg="#00ff00", font=("Consolas", 10, "bold")).pack(side=tk.LEFT)
        
        self.cmd_entry = tk.Entry(input_frame, bg="#111", fg="#00ff00", font=("Consolas", 11), 
                                  insertbackground="#00ff00", relief=tk.FLAT)
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.cmd_entry.bind("<Return>", self.send_command)
        
        btn = tk.Button(input_frame, text="EXECUTE", command=self.send_command, 
                        bg="#004400", fg="white", font=("Consolas", 10, "bold"), relief=tk.FLAT)
        btn.pack(side=tk.RIGHT, padx=5)
        
        # Current Target
        self.selected_agent = None

    def log(self, msg):
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.selected_agent = self.tree.item(item)["values"][1] # IP
            self.context_menu.post(event.x_root, event.y_root)

    def interact_agent(self):
        if self.selected_agent:
            self.log(f"[*] Target Selected: {self.selected_agent}")
            self.cmd_entry.focus()

    def quick_cmd(self, cmd):
        # In a real C2, we'd prefix with Agent ID.
        # Here we just queue it globally.
        self.send_payload(cmd)

    def send_command(self, event=None):
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        self.send_payload(cmd)
        self.cmd_entry.delete(0, tk.END)

    def send_payload(self, cmd):
        try:
            data = cmd.encode("utf-8")
            req = urllib.request.Request(f"{SERVER_URL}/api/queue", data=data, method="POST")
            with urllib.request.urlopen(req) as f:
                self.log(f"root@c2:~$ {cmd}")
        except Exception as e:
            self.log(f"[!] Error: {e}")

    def poll_server(self):
        while self.running:
            try:
                with urllib.request.urlopen(f"{SERVER_URL}/api/agents") as f:
                    agents = json.load(f)
                    self.update_agent_list(agents)
            except Exception:
                pass
            time.sleep(2)

    def update_agent_list(self, agents):
        # Clear current list
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add new
        for agent in agents:
            status = agent.get("status", "Offline")
            # Tag row based on status
            tag = "online" if status == "Online" else "offline"
            
            # Use ASCII icon
            icon = "●" if status == "Online" else "○"
            
            self.tree.insert("", tk.END, values=(agent.get("id"), agent.get("ip"), f"{icon} {status}"), tags=(tag,))

    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = C2Dashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
