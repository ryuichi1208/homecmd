package process

import (
	"context"
	"encoding/json"
	"errors"
	"runtime"
	"sort"
	"time"

	"github.com/shirou/gopsutil/cpu"
	"github.com/shirou/gopsutil/internal/common"
	"github.com/shirou/gopsutil/mem"
)

var (
	invoke                 common.Invoker = common.Invoke{}
	ErrorNoChildren                       = errors.New("process does not have children")
	ErrorProcessNotRunning                = errors.New("process does not exist")
)

type Process struct {
	Pid            int32 `json:"pid"`
	name           string
	status         string
	parent         int32
	numCtxSwitches *NumCtxSwitchesStat
	uids           []int32
	gids           []int32
	numThreads     int32
	memInfo        *MemoryInfoStat
	sigInfo        *SignalInfoStat
	createTime     int64
	lastCPUTimes   *cpu.TimesStat
	lastCPUTime    time.Time
	tgid           int32
}

func (r RlimitStat) String() string {
	s, _ := json.Marshal(r)
	return string(s)
}

func (i IOCountersStat) String() string {
	s, _ := json.Marshal(i)
	return string(s)
}

func (p NumCtxSwitchesStat) String() string {
	s, _ := json.Marshal(p)
	return string(s)
}

func Pids() ([]int32, error) {
	return PidsWithContext(context.Background())
}
func PidsWithContext(ctx context.Context) ([]int32, error) {
	pids, err := pidsWithContext(ctx)
	sort.Slice(pids, func(i, j int) bool { return pids[i] < pids[j] })
	return pids, err
}

func NewProcess(pid int32) (*Process, error) {
	p := &Process{Pid: pid}
	exists, err := PidExists(pid)
	if err != nil {
		return p, err
	}
	if !exists {
		return p, ErrorProcessNotRunning
	}
	p.CreateTime()
	return p, nil
}

func PidExists(pid int32) (bool, error) {
	return PidExistsWithContext(context.Background(), pid)
}

func (p *Process) Background() (bool, error) {
	return p.BackgroundWithContext(context.Background())
}
func (p *Process) BackgroundWithContext(ctx context.Context) (bool, error) {
	fg, err := p.ForegroundWithContext(ctx)
	if err != nil {
		return false, err
	}
	return !fg, err
}

func (p *Process) PercentWithContext(ctx context.Context, interval time.Duration) (float64, error) {
	cpuTimes, err := p.Times()
	if err != nil {
		return 0, err
	}
	now := time.Now()
	if interval > 0 {
		p.lastCPUTimes = cpuTimes
		p.lastCPUTime = now
		time.Sleep(interval)
		cpuTimes, err = p.Times()
		now = time.Now()
		if err != nil {
			return 0, err
		}
	} else {
		if p.lastCPUTimes == nil {
			// invoked first time
			p.lastCPUTimes = cpuTimes
			p.lastCPUTime = now
			return 0, nil
		}
	}
	numcpu := runtime.NumCPU()
	delta := (now.Sub(p.lastCPUTime).Seconds()) * float64(numcpu)
	ret := calculatePercent(p.lastCPUTimes, cpuTimes, delta, numcpu)
	p.lastCPUTimes = cpuTimes
	p.lastCPUTime = now
	return ret, nil
}

func (p *Process) IsRunning() (bool, error) {
	return p.IsRunningWithContext(context.Background())
}

func (p *Process) IsRunningWithContext(ctx context.Context) (bool, error) {
	createTime, err := p.CreateTimeWithContext(ctx)
	if err != nil {
		return false, err
	}
	p2, err := NewProcess(p.Pid)
	if err == ErrorProcessNotRunning {
		return false, nil
	}
	createTime2, err := p2.CreateTimeWithContext(ctx)
	if err != nil {
		return false, err
	}
	return createTime == createTime2, nil
}

func (p *Process) MemoryPercentWithContext(ctx context.Context) (float32, error) {
	machineMemory, err := mem.VirtualMemory()
	if err != nil {
		return 0, err
	}
	total := machineMemory.Total
	processMemory, err := p.MemoryInfo()
	if err != nil {
		return 0, err
	}
	used := processMemory.RSS
	return (100 * float32(used) / float32(total)), nil
}

func (p *Process) CPUPercent() (float64, error) {
	return p.CPUPercentWithContext(context.Background())
}

func (p *Process) CPUPercentWithContext(ctx context.Context) (float64, error) {
	crt_time, err := p.CreateTime()
	if err != nil {
		return 0, err
	}
	cput, err := p.Times()
	if err != nil {
		return 0, err
	}
	created := time.Unix(0, crt_time*int64(time.Millisecond))
	totalTime := time.Since(created).Seconds()
	if totalTime <= 0 {
		return 0, nil
	}
	return 100 * cput.Total() / totalTime, nil
}
