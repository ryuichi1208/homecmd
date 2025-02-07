package main

import (
	"fmt"
	"time"
	"errors"
)

type St struct {
	name string
	age int
}

func (s *St)new(name string, age int) error {
	s.name = name
	if ! (age > 0) {
		return errors.New("No age")
	}
	s.age = age
	return nil
}

func gPrint(ch chan *St) {

	c:=<-ch
	fmt.Println(c)
}

func gInt(ch chan int) {
	for {
		i := <-ch
		switch i {
		case 1:
			fmt.Println("1")
		case 2:
			fmt.Println("2")
			fallthrough
		case 3:
			fmt.Println("3")
		default:
			fmt.Println("default")
		}
	}
}

func main() {
	a := "aaa"
	b := &a
	fmt.Println(*b)

	// ch := make(chan *St, 2)

	c := &St{}
	err := c.new("aaa", -1)
	if err != nil {
		fmt.Println(err)
	}

	ich := make(chan int)
	go gInt(ich)
	ich <- 2
	ich <- 4
	ich <- 3

	// go gPrint(ch)
	// ch <-c
	time.Sleep(time.Second * 3)

}
