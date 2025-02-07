// mapとmutexをstructのプロパティに持たせる
type SafeCounter struct {
    v   map[string]int
    mux sync.RWMutex
}

// Inc 指定したkeyのvalueをインクリメントする
func (c *SafeCounter) Inc(key string) {
    // 排他ロックをかけて値更新
    c.mux.Lock()
    defer c.mux.Unlock()
    c.v[key]++
}

// GetValue ゲッター
func (c *SafeCounter) GetValue(key string) int {
    // 共有ロックをかけて値取得
    c.mux.RLock()
    defer c.mux.RUnlock()
    return c.v[key]
}

func main() {
    c := SafeCounter{v: make(map[string]int)}
    for i := 0; i < 1000; i++ {
        go c.Inc("somekey")
    }

    time.Sleep(time.Second)
    fmt.Println(c.GetValue("somekey"))
}package main
