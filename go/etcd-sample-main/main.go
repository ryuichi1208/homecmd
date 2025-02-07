package main

import (
	"context"
	"log"
	"time"

	clientv3 "go.etcd.io/etcd/client/v3"
)

func main() {
	// etcd クライアントの設定
	cli, err := clientv3.New(clientv3.Config{
		Endpoints:   []string{"localhost:2379"}, // etcd サーバーのアドレスを指定
		DialTimeout: 5 * time.Second,
	})
	if err != nil {
		log.Fatalf("Failed to connect to etcd: %v", err)
	}
	defer cli.Close()

	// キーと値を etcd に書き込む
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	_, err = cli.Put(ctx, "mykey", "myvalue")
	cancel()
	if err != nil {
		log.Fatalf("Failed to write to etcd: %v", err)
	}

	// etcd からキーの値を取得
	ctx, cancel = context.WithTimeout(context.Background(), time.Second)
	resp, err := cli.Get(ctx, "mykey")
	cancel()
	if err != nil {
		log.Fatalf("Failed to read from etcd: %v", err)
	}

	// 取得した値を表示
	for _, ev := range resp.Kvs {
		log.Printf("%s : %s\n", ev.Key, ev.Value)
	}
}
