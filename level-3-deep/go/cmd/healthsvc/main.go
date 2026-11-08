// UNEXECUTED source. See ../../internal/profile/profile.go: no Go
// toolchain on this VM, so this command was never built or run
// here. It shows the pprof wiring the study design needs: the
// net/http/pprof handlers registered by import side effect on a
// diagnostics only listener, kept off the service listener, plus
// a printed copy of the study steps so a runner on a Go machine
// follows the same plan REPORT.md publishes.
package main

import (
	"fmt"
	"log"
	"net/http"
	_ "net/http/pprof"
	"time"

	"github.com/JesunAhmadUshno/systems-languages-lab/level-3-deep/go/internal/profile"
)

func main() {
	// Diagnostics listener: pprof only, localhost by convention.
	go func() {
		server := &http.Server{
			Addr:              "127.0.0.1:6060",
			ReadHeaderTimeout: 5 * time.Second,
		}
		log.Println("pprof diagnostics on http://127.0.0.1:6060/debug/pprof/")
		log.Fatal(server.ListenAndServe())
	}()
	fmt.Println("pprof study plan (UNEXECUTED on the authoring VM):")
	for _, step := range profile.StudySteps {
		fmt.Println(step)
	}
	select {}
}
