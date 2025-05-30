package main

import (
	"bufio"
	"flag"
	"fmt"
	"io"
	"os"
	"sort"
	"strconv"
	"strings"
)

var version = "0.0.1"

type options struct {
	file    string
	pValues []int
	rValue  bool
	version bool
}

// CLI is the command line interface object
type CLI struct {
	InStream  io.Reader
	OutStream io.Writer
	ErrStream io.Writer
}

// Run executes the CLI
func (c *CLI) Run() error {
	opt, err := parseFlag()
	if err != nil {
		return fmt.Errorf("failed parse flag: %w", err)
	}

	if opt.version {
		_, _ = fmt.Fprintf(c.OutStream, "percentile version %s\n", version)
		return nil
	}

	f, err := openFile(opt.file)
	if err != nil {
		return fmt.Errorf("failed open file: %w", err)
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	var numbers []float64
	for scanner.Scan() {
		line := scanner.Text()
		num, err := strconv.ParseFloat(line, 64)
		if err != nil {
			return fmt.Errorf("failed parse float: %w", err)
		}
		numbers = append(numbers, num)
	}
	if err := scanner.Err(); err != nil {
		return fmt.Errorf("failed scan file: %w", err)
	}

	if len(numbers) == 0 {
		return nil
	}

	sort.Float64s(numbers)

	for _, v := range opt.pValues {
		p := Calculate(numbers, v)
		if opt.rValue {
			_, _ = fmt.Fprintf(c.OutStream, "p%d: %.1f \n", v, p)
		} else {
			_, _ = fmt.Fprintf(c.OutStream, "p%d: %d \n", v, int(p))
		}
	}

	return nil
}

func parseFlag() (*options, error) {
	pOption := flag.String("p", "25,50,75,90,95,99", "Specify percentiles (comma-separated list of integers)")
	rOption := flag.Bool("r", false, "Don't Round percentile values")
	version := flag.Bool("v", false, "Show version")
	flag.Parse()

	file := "-"
	if len(flag.Args()) > 0 {
		file = flag.Args()[0]
	}

	// -p オプションをパースする
	var pValues []int
	for _, v := range strings.Split(*pOption, ",") {
		p, err := strconv.Atoi(v)
		if err != nil {
			return nil, fmt.Errorf("percentile must only contain integers: %w", err)
		}
		if p < 0 || p > 100 {
			return nil, fmt.Errorf("percentile must be between 0 and 100: %w", err)
		}
		pValues = append(pValues, p)
	}

	opt := &options{
		file:    file,
		pValues: pValues,
		rValue:  *rOption,
		version: *version,
	}
	return opt, nil
}

func openFile(file string) (io.ReadCloser, error) {
	if file == "-" {
		return io.NopCloser(os.Stdin), nil
	}
	return os.Open(file)
}

func Calculate(numbers []float64, percent int) float64 {
	if percent == 0 {
		return numbers[0]
	}

	l := len(numbers)
	if percent == 100 {
		return numbers[l-1]
	}

	index := float64(l*percent) / 100
	return (numbers[int(index)] + numbers[int(index)-1]) / 2
}

func main() {
	cli := CLI{
		InStream:  os.Stdin,
		OutStream: os.Stdout,
		ErrStream: os.Stderr,
	}
	if err := cli.Run(); err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%s\n", err.Error())
		os.Exit(1)
	}
}
