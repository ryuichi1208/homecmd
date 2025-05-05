package main

import (
	"fmt"
)

func main() {
	// Define a slice of integers
	numbers := []int{1, 2, 3, 4, 5}

	// Use a for loop to iterate over the slice
	for i := 0; i < len(numbers); i++ {
		fmt.Println(numbers[i])
	}

	// Use a for range loop to iterate over the slice
	for _, number := range numbers {
		fmt.Println(number)
	}
}
