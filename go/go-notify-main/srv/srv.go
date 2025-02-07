package main

import (
	"sync"
	"log"
	"time"
	// "github.com/gin-gonic/gin"
)

func _sleep(n time.Duration, cb chan J) {
	time.Sleep(n * time.Second)
	log.Println("block")
	log.Println("go", <-cb)
}

type J struct {
	name string
}

func main() {
	wg := sync.WaitGroup{}
	// r := gin.Default()
	// r.GET("/ping", func(c *gin.Context) {
	// 	c.JSON(200, gin.H{
	// 		"message": "pong",
	// 	})
	// })
	// r.Run()

	js := make([]J, 2)
	js[0] = J{name: "test"}
	js[1] = J{name: "test"}

	log.Println(js[0].name)

	log.Print("Start")
	cb := make(chan J, 2)
	j := J{"aaa"}

	for i := 0; i < 3; i++ {
		go _sleep(2, cb)
	}

	cb<-j
	cb<-j
	wg.Wait()

	// time.Sleep(5 * time.Second)
	cb<-j
	log.Print("End")

	b := true

	switch b {
	case true:
		log.Println("true")
		fallthrough
	case false:
		log.Println("false")
	}
}
