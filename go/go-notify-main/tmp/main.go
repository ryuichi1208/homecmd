package main

import (
	"fmt"
	"time"
)

type Human struct {
	name string
	age  int
}

func (h *Human) _name(n string) {
	h.name = n
}

func change_named(h *Human) {
	h.name = "aaa"
}

func f(v string) {
	for i := 0; i < 3; i++ {
		fmt.Println(v)
		time.Sleep(time.Second)
	}
}

func gd() {
	msg := make(chan string, 2)
	go func() {
		msg <- "hello1"
		// msg <- "hello2"
	}()
	// time.Sleep(time.Second * 2)
	msg <- "hello3"
	m := <-msg
	fmt.Println(m)
	m = <-msg
	fmt.Println(m)
}

func main() {
	fmt.Println("vim-go")

	var h Human
	h._name("bbb")
	fmt.Println(h.name)
	change_named(&h)
	fmt.Println(h.name)

	maps := make(map[string]string, 2)
	maps["a"] = "b"
	maps["c"] = "e"

	for k, _ := range maps {
		fmt.Println(maps[k])
	}

	gd()

	// go f("e goroutine")
	// f("not e gortoutine")
	// fmt.Println("done")
}
