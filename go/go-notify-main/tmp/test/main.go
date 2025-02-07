package main

import "fmt"

type Hu struct {
	name string
	age int
	fiend string
}

func main() {
	// for i := 0; i < 10; i++ {
	// 	fmt.Println(i)
	// }

	// list := make([]int, 3)
	// list[0] = 1

	list := make([]Hu, 2)
	for i, _ := range list {
		list[i].name = fmt.Sprintf("%s%d", "aaa", i)
		fmt.Println(list[i].name)
	}
}
