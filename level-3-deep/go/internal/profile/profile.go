// UNEXECUTED source. This VM has no Go toolchain (go not found,
// rechecked 2026-11-05), so this package was never compiled or run
// here. It carries the Deep pprof study design in code shape: the
// capture helpers and the exact before and after study steps that
// WOULD run on a machine with Go, against the Build health service
// in ../../level-2-build/go. No profile was captured on this VM
// and no Go timing is claimed anywhere in this level.
package profile

import (
	"fmt"
	"os"
	"runtime"
	"runtime/pprof"
)

// StudySteps is the exact study plan, in order. Step 4 is the fix
// whose Python form was measured in this level (an index built
// once per fixed health record set, replacing a per request filter
// and sort); the Go form would precompute the best endpoint per
// model in a map at probe time.
var StudySteps = []string{
	"1. serve: run the Build health service with the diagnostics listener on (cmd/healthsvc) and confirm /debug/pprof/ answers",
	"2. load: replay the deterministic workload (200 endpoints, 20000 routing requests, same generation as profile_deep.py)",
	"3. capture before: CaptureCPU for the load duration into cpu-before.prof; read it with go tool pprof -top and record the top functions",
	"4. fix: replace per request filter and sort in Route with a per model best endpoint index built once after probing",
	"5. capture after: CaptureCPU into cpu-after.prof under the identical load; record the top functions and the total samples",
	"6. compare: publish both -top tables and the wall time medians (perf style pooled repetitions) beside the Python numbers, labelled Go measured on that machine",
	"7. heap: CaptureHeap before and after as a secondary check that the index does not grow memory per request",
}

// CaptureCPU runs a CPU profile for the duration of fn and writes
// it to path. It is the runtime/pprof half of the study; the
// net/http/pprof listener in cmd/healthsvc is the live half.
func CaptureCPU(path string, fn func()) error {
	f, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("capture cpu: create %s: %w", path, err)
	}
	defer f.Close()
	if err := pprof.StartCPUProfile(f); err != nil {
		return fmt.Errorf("capture cpu: start: %w", err)
	}
	fn()
	pprof.StopCPUProfile()
	return nil
}

// CaptureHeap writes a heap profile to path after a GC, so the
// snapshot reflects live allocations, not pending collections.
func CaptureHeap(path string) error {
	f, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("capture heap: create %s: %w", path, err)
	}
	defer f.Close()
	runtime.GC()
	if err := pprof.WriteHeapProfile(f); err != nil {
		return fmt.Errorf("capture heap: write: %w", err)
	}
	return nil
}
