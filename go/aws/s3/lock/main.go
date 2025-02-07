package main

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

func main() {
	bucketName := "your-bucket-name" // オブジェクトロックが有効なバケット
	objectKey := "locked-object.txt"
	region := "us-west-2" // バケットのリージョン

	// AWS SDK の設定
	cfg, err := config.LoadDefaultConfig(context.TODO(), config.WithRegion(region))
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	s3Client := s3.NewFromConfig(cfg)

	// オブジェクトをアップロードしてロックを設定
	expiration := time.Now().Add(24 * time.Hour) // 24時間ロック

	_, err = s3Client.PutObject(context.TODO(), &s3.PutObjectInput{
		Bucket:                    aws.String(bucketName),
		Key:                       aws.String(objectKey),
		Body:                      aws.ReadSeekCloser(strings.NewReader("This is a locked object.")),
		ObjectLockMode:            "GOVERNANCE", // Governanceモード
		ObjectLockRetainUntilDate: aws.Time(expiration),
	})

	if err != nil {
		log.Fatalf("Failed to upload and lock object: %v", err)
	}

	fmt.Printf("Successfully uploaded and locked object '%s' in bucket '%s' until %s\n", objectKey, bucketName, expiration.Format(time.RFC3339))

	// ロック状態を確認
	headOutput, err := s3Client.HeadObject(context.TODO(), &s3.HeadObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(objectKey),
	})

	if err != nil {
		log.Fatalf("Failed to get object metadata: %v", err)
	}

	fmt.Printf("Object Lock Mode: %s\n", *headOutput.ObjectLockMode)
	fmt.Printf("Retention Until: %s\n", headOutput.ObjectLockRetainUntilDate.Format(time.RFC3339))
}
