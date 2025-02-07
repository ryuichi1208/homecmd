package main

import (
    "log"
    "sync"
    "time"

    "golang.org/x/sync/singleflight"
)

var group singleflight.Group

func callAPI(name string) {
    v, err, shared := group.Do(name, func() (interface{}, error) {
        // 具体的に実行したい処理を書く
        <-time.After(3 * time.Millisecond)
        return time.Now(), nil
    })
    if err != nil {
        log.Fatal(err)
    }
    log.Println("結果:", v, ", 重複が発生したか:", shared)
}

func main() {
    log.SetFlags(0)

    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            callAPI("work")
        }()
        <-time.After(time.Millisecond)
    }
    wg.Wait()
}
