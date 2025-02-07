package main

import (
	"fmt"
	"net/http"
	"io/ioutil"
)

func _request1(url string) {
	resp, err := http.Get(url)
	if err != nil {
		panic("http error")
	}
	defer resp.Body.Close()
	byteArray, _ := ioutil.ReadAll(resp.Body)
	fmt.Println(string(byteArray))
}

func _request2(url string) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		panic(err)
	}
	fmt.Println(req)
}

func main() {
	url := "aaaa"
	_request2(url)
	fmt.Println("vim-go")
}
