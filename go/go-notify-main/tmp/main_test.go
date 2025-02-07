package main

import (
	"fmt"
	// "time"
	"os"
	"sync"
)

func main() {
	wg := sync.WaitGroup{}
	// ch := make(chan bool)
	ch := make(chan map[string]string)
	go func() {
		for {
			select {
			case v := <-ch:
				fmt.Println(v)
			default:
				fmt.Println("no value")
				os.Exit(0)
			}
		}
	}()
	// t := true
	t := make(map[string]string)
	t["aaa"] = "bbb"
	ch <- t
	wg.Wait()
	fmt.Println("End")
}
