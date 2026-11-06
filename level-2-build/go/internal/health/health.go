// UNEXECUTED source. This VM has no Go toolchain (go not found,
// rechecked 2026-11-05), so this package was never compiled or run
// here. It is the Build grade Go shape of the executed Python
// reference in ../../service_build.py: a module package with wrapped
// errors, context cancellation, and a worker pool over channels,
// written as a native Go developer would write it. Read it beside
// the Python file. No result in this level comes from this code.
package health

import (
	"context"
	"errors"
	"fmt"
	"sort"
	"sync"
)

// ErrProbeFailed marks a probe transport failure. Callers test it
// with errors.Is through any number of wrapping layers.
var ErrProbeFailed = errors.New("probe failed")

// ErrNoHealthy marks a routing miss for a model.
var ErrNoHealthy = errors.New("no healthy endpoint")

type Endpoint struct {
	Name      string
	Model     string
	LatencyMs int
	ProbeOK   bool
	Note      string
	ErrorKind string
}

type Record struct {
	Name      string
	Model     string
	Healthy   bool
	LatencyMs int
	Note      string
	ErrorKind string
}

// ProbeOne probes one endpoint. A failure is returned as a wrapped
// error: the transport cause stays reachable with errors.Is and
// errors.As, and each layer adds its own context, the Go way.
func ProbeOne(ctx context.Context, ep Endpoint) (Record, error) {
	if err := ctx.Err(); err != nil {
		return Record{}, fmt.Errorf("probe %s: %w", ep.Name, err)
	}
	if !ep.ProbeOK {
		cause := fmt.Errorf("%w: %s", ErrProbeFailed, ep.Note)
		return Record{}, fmt.Errorf("probe %s: %w", ep.Name, cause)
	}
	return Record{Name: ep.Name, Model: ep.Model, Healthy: true, LatencyMs: ep.LatencyMs, Note: ep.Note}, nil
}

// ProbeAll probes every endpoint with a worker pool over channels.
// The pool stops early when ctx is cancelled: workers select on
// ctx.Done() beside the jobs channel, and the returned error wraps
// context.Canceled or context.DeadlineExceeded. Records come back
// sorted by name, so the result does not depend on worker count.
func ProbeAll(ctx context.Context, eps []Endpoint, workers int) ([]Record, error) {
	if workers < 1 {
		return nil, fmt.Errorf("probe all: workers must be at least 1, got %d", workers)
	}
	type outcome struct {
		rec Record
		ep  Endpoint
		err error
	}
	jobs := make(chan Endpoint)
	outcomes := make(chan outcome)
	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				select {
				case <-ctx.Done():
					return
				case ep, ok := <-jobs:
					if !ok {
						return
					}
					rec, err := ProbeOne(ctx, ep)
					select {
					case outcomes <- outcome{rec: rec, ep: ep, err: err}:
					case <-ctx.Done():
						return
					}
				}
			}
		}()
	}
	go func() {
		for _, ep := range eps {
			select {
			case jobs <- ep:
			case <-ctx.Done():
				break
			}
		}
		close(jobs)
	}()
	go func() {
		wg.Wait()
		close(outcomes)
	}()
	out := []Record{}
	for oc := range outcomes {
		if oc.err != nil {
			if errors.Is(oc.err, context.Canceled) || errors.Is(oc.err, context.DeadlineExceeded) {
				continue
			}
			out = append(out, Record{Name: oc.ep.Name, Model: oc.ep.Model, Healthy: false, LatencyMs: oc.ep.LatencyMs, Note: oc.ep.Note, ErrorKind: oc.ep.ErrorKind})
			continue
		}
		out = append(out, oc.rec)
	}
	if err := ctx.Err(); err != nil {
		return out, fmt.Errorf("probe all: %w", err)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].Name < out[j].Name })
	return out, nil
}

// Route picks the endpoint for one model: healthy only, lowest
// latency first, name ascending as the tie break. A miss is a
// wrapped ErrNoHealthy, not a silent empty string.
func Route(model string, records []Record) (string, error) {
	best := ""
	bestLatency := 0
	for _, r := range records {
		if r.Model != model || !r.Healthy {
			continue
		}
		if best == "" || r.LatencyMs < bestLatency || (r.LatencyMs == bestLatency && r.Name < best) {
			best = r.Name
			bestLatency = r.LatencyMs
		}
	}
	if best == "" {
		return "", fmt.Errorf("route %s: %w", model, ErrNoHealthy)
	}
	return best, nil
}
