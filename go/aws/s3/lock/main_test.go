package main

import (
	"context"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/aws/aws-sdk-go-v2/service/s3/types"
	"github.com/stretchr/testify/assert"
)

// MockS3Client は S3 クライアントのモック
type MockS3Client struct {
	s3.Client
	PutObjectFunc  func(ctx context.Context, params *s3.PutObjectInput, optFns ...func(*s3.Options)) (*s3.PutObjectOutput, error)
	HeadObjectFunc func(ctx context.Context, params *s3.HeadObjectInput, optFns ...func(*s3.Options)) (*s3.HeadObjectOutput, error)
}

func (m *MockS3Client) PutObject(ctx context.Context, params *s3.PutObjectInput, optFns ...func(*s3.Options)) (*s3.PutObjectOutput, error) {
	return m.PutObjectFunc(ctx, params, optFns...)
}

func (m *MockS3Client) HeadObject(ctx context.Context, params *s3.HeadObjectInput, optFns ...func(*s3.Options)) (*s3.HeadObjectOutput, error) {
	return m.HeadObjectFunc(ctx, params, optFns...)
}

func TestUploadAndLockObject(t *testing.T) {
	mockClient := &MockS3Client{
		PutObjectFunc: func(ctx context.Context, params *s3.PutObjectInput, optFns ...func(*s3.Options)) (*s3.PutObjectOutput, error) {
			assert.Equal(t, "your-bucket-name", *params.Bucket)
			assert.Equal(t, "locked-object.txt", *params.Key)
			assert.Equal(t, "GOVERNANCE", string(params.ObjectLockMode))
			return &s3.PutObjectOutput{}, nil
		},
	}

	err := uploadAndLockObject(mockClient, "your-bucket-name", "locked-object.txt", time.Now().Add(24*time.Hour))
	assert.NoError(t, err)
}

func TestGetObjectLockInfo(t *testing.T) {
	expiration := time.Now().Add(24 * time.Hour)

	mockClient := &MockS3Client{
		HeadObjectFunc: func(ctx context.Context, params *s3.HeadObjectInput, optFns ...func(*s3.Options)) (*s3.HeadObjectOutput, error) {
			assert.Equal(t, "your-bucket-name", *params.Bucket)
			assert.Equal(t, "locked-object.txt", *params.Key)
			return &s3.HeadObjectOutput{
				ObjectLockMode:            types.ObjectLockModeGovernance,
				ObjectLockRetainUntilDate: &expiration,
			}, nil
		},
	}

	output, err := getObjectLockInfo(mockClient, "your-bucket-name", "locked-object.txt")
	assert.NoError(t, err)
	assert.Equal(t, types.ObjectLockModeGovernance, *output.ObjectLockMode)
	assert.Equal(t, expiration, *output.ObjectLockRetainUntilDate)
}
