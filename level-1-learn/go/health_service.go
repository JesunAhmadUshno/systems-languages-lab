// Teaching source, NOT compiled or run in this Learn level.
// This VM has no Go toolchain (go not found, checked 2026-11-05), so this
// file was never built here. It shows the same health and routing logic
// as the executed Python reference (../health_service.py) in the Go
// shape the SPEC asks for: goroutines fed by a jobs channel, results
// returned on a results channel. Read it beside the Python file. The
// Build level compiles and tests this track with a real toolchain.
package main

import (
	"fmt"
	"sort"
	"sync"
)

type Endpoint struct {
	Name      string
	Model     string
	LatencyMs int
	ProbeOK   bool
}

type Health struct {
	Name      string
	Model     string
	Healthy   bool
	LatencyMs int
}

var endpoints = []Endpoint{
	{"alpha-chat", "chat", 40, true},
	{"beta-chat", "chat", 25, true},
	{"gamma-chat", "chat", 25, false},
	{"alpha-embed", "embed", 15, true},
	{"beta-embed", "embed", 30, true},
	{"gamma-vision", "vision", 50, false},
}

func probeAll(eps []Endpoint, workers int) []Health {
	jobs := make(chan Endpoint)
	results := make(chan Health)
	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for ep := range jobs {
				results <- Health{ep.Name, ep.Model, ep.ProbeOK, ep.LatencyMs}
			}
		}()
	}
	go func() {
		for _, ep := range eps {
			jobs <- ep
		}
		close(jobs)
	}()
	go func() {
		wg.Wait()
		close(results)
	}()
	out := []Health{}
	for h := range results {
		out = append(out, h)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].Name < out[j].Name })
	return out
}

func route(model string, health []Health) string {
	best := ""
	bestLatency := 0
	for _, h := range health {
		if h.Model != model || !h.Healthy {
			continue
		}
		if best == "" || h.LatencyMs < bestLatency || (h.LatencyMs == bestLatency && h.Name < best) {
			best = h.Name
			bestLatency = h.LatencyMs
		}
	}
	return best
}

func main() {
	health := probeAll(endpoints, 3)
	for _, model := range []string{"chat", "embed", "vision"} {
		fmt.Println(model, "routes to", route(model, health))
	}
}
