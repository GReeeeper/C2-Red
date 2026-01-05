# C2 RED // Advanced Adversary Emulation Framework

![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-red)
![Language](https://img.shields.io/badge/go-server-blue)
![Language](https://img.shields.io/badge/cpp-implant-orange)
![Language](https://img.shields.io/badge/python-gui-yellow)

**C2 RED** is a lightweight, modular Command & Control (C2) framework designed for Red Team engagements and educational cybersecurity research. It features a high-performance Go-based TeamServer, a stealthy C++ implant with dynamic configuration capabilities, and a "Cyberpunk" style Python Dashboard for operator control.

> **Disclaimer**: This software is for educational purposes and authorized security testing only. Usage for malicious intent is strictly prohibited.

---

## 🚀 Features

### 1. TeamServer (Golang)
*   **High Performance**: Built with Go for concurrency and speed.
*   **REST API**: Exposes agent management and tasking via standard HTTP/JSON endpoints.
*   **Agent Tracking**: In-memory tracking of active sessions, health status, and last-seen timestamps.

### 2. Stealth Implant (C++)
*   **Lightweight**: Native C++ implementation with minimal dependencies (libcurl).
*   **Poll-Based Beaconing**: Uses HTTP POST heartbeats to fetch tasks.
*   **Dynamic Configuration**: 
    *   Change sleep intervals on-the-fly (`config sleep <seconds>`).
    *   Remote termination (`exit`).
*   **Shell Execution**: Executes system commands via `popen` and returns output.

### 3. Operator Dashboard (Python)
*   **Visual Interface**: A "Hacker-style" dark GUI built with Tkinter.
*   **Real-Time Monitoring**: Auto-refreshing agent table with status indicators.
*   **Context Menus**: Right-click to interact, kill, or query agents.
*   **Integrated Console**: Command input and chronological event logging.

---

## 🛠️ Architecture

```mermaid
graph LR
    A[Operator] -->|GUI (Python)| B(TeamServer :8080)
    C[Implant (C++)] -->|HTTP Beacon| B
    B -->|Task Queue| C
    C -->|Cmd Output| B
```

---

## 📦 Installation & Usage

### Prerequisites
*   **Go** (1.19+)
*   **C++ Compiler** (g++ or clang) with `libcurl`
*   **Python 3** with `tkinter`

### 1. Start the TeamServer
The brain of the operation. It listens on port `8080`.
```bash
go run server.go
```

### 2. Launch the Dashboard
The visual console for the operator.
```bash
python c2_gui.py
```

### 3. Compile & Run the Implant
The agent running on the target machine.
```bash
# Compile (Linux)
g++ implant.cpp -o implant -lcurl

# Run
./implant
```

---

## 🎮 Command Reference

| Command | Description | Example |
| :--- | :--- | :--- |
| `whoami` | Run shell command on target | `whoami` |
| `ls -la` | List files on target | `ls -la` |
| `config sleep <N>` | Change beacon interval to N seconds | `config sleep 2` |
| `exit` | Kill the implant remotely | `exit` |

---

## 📸 Screenshots
*(Add screenshots of your Dashboard here)*

---

## ⚠️ Legal & Ethics
This project interacts with operating system commands and network interfaces. It is designed to simulate adversary tactics for the purpose of testing detection and response capabilities.
*   **Do not** deploy on systems you do not own or have explicit permission to test.
*   The author is not responsible for misuse of this tool.
