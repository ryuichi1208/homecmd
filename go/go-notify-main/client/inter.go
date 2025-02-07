package main

import (
	"fmt"
	"reflect"
	"sync"
	"time"
)

type inpA interface {
	A(i int64) (n int, s string)
}

type Target struct {
	Value string
}

func (t *Target) A(i int64) (n int, s string) {
	return 1, "a"
}

type f func(w string)

func w(w string) {
	fmt.Println("aaa" + w)
}

func main() {
	fmt.Println("aaa")
	fprint("aaa")
	fprint(10)
	var n int64
	fprint(n)

	var fn f
	fn = w
	fn("bbb")

	go func() {
		fmt.Println("ddd")
	}()

	var mu sync.Mutex
	c := 0
	for i := 0; i < 1000; i++ {
		go func() {
			mu.Lock()         // 排他ロック取得
			defer mu.Unlock() // 関数終了時に排他ロック解除
			c++
		}()
	}
	time.Sleep(time.Second)
	fmt.Println(c)
}

func fprint(f interface{}) {
	fmt.Println(f, reflect.TypeOf(f))
}
