// UNEXECUTED source. See ../internal/health/health.go: no Go
// toolchain on this VM, so this command was never built or run
// here. It shows the native entry point shape: a module command
// that derives a timeout context, runs the pool, and routes.
package main

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/JesunAhmadUshno/systems-languages-lab/level-2-build/go/internal/health"
)

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	eps := []health.Endpoint{
		{Name: "alpha-chat", Model: "chat", LatencyMs: 40, ProbeOK: true, Note: "200 ok"},
		{Name: "delta-chat", Model: "chat", LatencyMs: 20, ProbeOK: true, Note: "200 ok"},
		{Name: "gamma-chat", Model: "chat", LatencyMs: 25, ProbeOK: false, Note: "503 unavailable", ErrorKind: "http_error"},
	}
	records, err := health.ProbeAll(ctx, eps, 3)
	if err != nil {
		fmt.Fprintln(os.Stderr, "healthsvc:", err)
		os.Exit(1)
	}
	for _, model := range []string{"chat", "vision"} {
		target, err := health.Route(model, records)
		if err != nil {
			fmt.Println(model, "unrouted:", err)
			continue
		}
		fmt.Println(model, "routes to", target)
	}
}
