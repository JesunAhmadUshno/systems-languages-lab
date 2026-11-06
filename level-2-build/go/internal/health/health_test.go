// UNEXECUTED source. See health.go: no Go toolchain on this VM, so
// these tests were never run here. They show the native tooling
// shape the SPEC Build scope asks for: table driven tests in the
// package, run with go test ./... on a node with the toolchain.
package health

import (
	"context"
	"errors"
	"testing"
	"time"
)

var fixtures = []Endpoint{
	{Name: "alpha-chat", Model: "chat", LatencyMs: 40, ProbeOK: true, Note: "200 ok"},
	{Name: "beta-chat", Model: "chat", LatencyMs: 25, ProbeOK: true, Note: "200 ok"},
	{Name: "gamma-chat", Model: "chat", LatencyMs: 25, ProbeOK: false, Note: "503 unavailable", ErrorKind: "http_error"},
	{Name: "delta-chat", Model: "chat", LatencyMs: 20, ProbeOK: true, Note: "200 ok"},
	{Name: "eta-code", Model: "code", LatencyMs: 18, ProbeOK: true, Note: "200 ok"},
	{Name: "zeta-code", Model: "code", LatencyMs: 18, ProbeOK: true, Note: "200 ok"},
}

func TestProbeAllCounts(t *testing.T) {
	records, err := ProbeAll(context.Background(), fixtures, 3)
	if err != nil {
		t.Fatalf("ProbeAll: %v", err)
	}
	healthy := 0
	for _, r := range records {
		if r.Healthy {
			healthy++
		}
	}
	if healthy != 5 {
		t.Fatalf("healthy = %d, want 5", healthy)
	}
}

func TestRouteTable(t *testing.T) {
	records, err := ProbeAll(context.Background(), fixtures, 3)
	if err != nil {
		t.Fatalf("ProbeAll: %v", err)
	}
	cases := []struct {
		model string
		want  string
	}{
		{"chat", "delta-chat"},
		{"code", "eta-code"},
	}
	for _, c := range cases {
		got, err := Route(c.model, records)
		if err != nil {
			t.Fatalf("Route(%s): %v", c.model, err)
		}
		if got != c.want {
			t.Errorf("Route(%s) = %s, want %s", c.model, got, c.want)
		}
	}
	if _, err := Route("vision", records); !errors.Is(err, ErrNoHealthy) {
		t.Errorf("Route(vision) error = %v, want ErrNoHealthy", err)
	}
}

func TestProbeAllCancelledContext(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	_, err := ProbeAll(ctx, fixtures, 3)
	if !errors.Is(err, context.Canceled) {
		t.Fatalf("cancelled ProbeAll error = %v, want context.Canceled", err)
	}
}

func TestProbeOneWrappedError(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	bad := Endpoint{Name: "gamma-chat", Model: "chat", ProbeOK: false, Note: "503 unavailable"}
	_, err := ProbeOne(ctx, bad)
	if !errors.Is(err, ErrProbeFailed) {
		t.Fatalf("ProbeOne error = %v, want ErrProbeFailed in chain", err)
	}
}
