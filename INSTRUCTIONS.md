# C2 Framework Usage Guide

## Components
1.  **TeamServer (Go)**: Listens on port 8080.
2.  **Implant (C++)**: Connects to the server, retrieves commands, executes them, and prints output locally.

## Running the Lab (Dashboard Mode)

To use the new **Hacker Dashboard (GUI)**:

### 1. Start the TeamServer
```bash
go run server.go
```
The server now spawns an API on port 8080.

### 2. Start the Dashboard
Open a new terminal:
```bash
python c2_gui.py
```
A window will open. You will see an empty **AGENTS** list on the left.

### 3. Start the Implant
Open a third terminal (or run on a different VM):
```bash
./implant
```

### 4. Pwn!
*   **Watch**: The Implant IP appears in the GUI Sidebar as **Online**.
*   **Interact**: Type commands (e.g., `whoami`, `ls`) in the bottom bar of the GUI.
*   **Results**: The command is queued, picked up by the implant, and you see the log in the console.

## How it Works
1.  **Implant** POSTs to `/api/beacon`.
2.  **Server** checks if it has a queued command.
    *   **Yes**: Sends command string.
    *   **No**: Sends "sleep".
3.  **Implant** reads response.
    *   If "sleep": Waits 5s.
    *   If command: Runs `popen(cmd)`, prints output, then waits 5s.
