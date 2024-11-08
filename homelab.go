package main

import (
	"crypto/tls"
	"log"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"time"
)

// ProxyHandler handles the HTTP proxy requests
func ProxyHandler(remoteAddr, host string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		remote, err := url.Parse(remoteAddr)
		if err != nil {
			http.Error(w, "Invalid remote address", http.StatusInternalServerError)
			return
		}

		// Create a reverse proxy
		proxy := httputil.NewSingleHostReverseProxy(remote)

		// Modify the transport to skip TLS verification and use custom dialer
		proxy.Transport = &http.Transport{
			TLSClientConfig: &tls.Config{
				InsecureSkipVerify: true,
				ServerName:         host,
			},
			DialContext: (&net.Dialer{
				Timeout:   30 * time.Second,
				KeepAlive: 30 * time.Second,
			}).DialContext,
		}

		// Set the Host header to the target hostname
		r.Host = host
		proxy.ServeHTTP(w, r)
	})
}

func main() {
	localAddr := "127.0.0.1:8080"          // Local address to listen on
	remoteAddr := "https://192.168.51.100" // Remote address to forward traffic to
	host := "cd.homelab.internal"          // Hostname to preserve in the request

	log.Printf("Listening on %s and forwarding to %s with Host header %s", localAddr, remoteAddr, host)

	// Create an HTTP server
	server := &http.Server{
		Addr:    localAddr,
		Handler: ProxyHandler(remoteAddr, host),
	}

	// Start the HTTP server
	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("Server failed: %s", err)
	}
}
