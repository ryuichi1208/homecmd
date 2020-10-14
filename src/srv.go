func main() {
    http.Handle("/", http.HandlerFunc(func(res http.ResponseWriter, req *http.Request) {
        httpReq, _ := http.NewRequest("GET", "http://srv+service.service.consul/backend", nil)
        httpRes, err := HTTPClient.Do(httpReq)
        if err != nil {
            log.Println(err)
            res.WriteHeader(500)
            return
        }
        defer httpRes.Body.Close()
        io.Copy(res, httpRes.Body)
    }))

    http.Handle("/backend", http.HandlerFunc(func(res http.ResponseWriter, req *http.Request) {
        res.WriteHeader(200)
        res.Write([]byte("ok"))
    }))
    http.ListenAndServe(":8080", nil)
}
