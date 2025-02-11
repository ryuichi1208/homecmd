package main

import (
	"context"
	"fmt"
	"log"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
)

const (
	tableName = "Orders"
	gsiName   = "ProductCategoryIndex"
)

func main() {
	// AWS設定の読み込み
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Fatalf("unable to load SDK config, %v", err)
	}

	// DynamoDBクライアントの作成
	svc := dynamodb.NewFromConfig(cfg)

	// テーブル作成（存在しない場合のみ）
	createTable(svc)

	// データの挿入
	putItem(svc, "001", "CUST001", "2023-02-01", 150, "Electronics")
	putItem(svc, "002", "CUST002", "2023-02-02", 200, "Books")
	putItem(svc, "003", "CUST003", "2023-02-03", 100, "Electronics")

	// GSIを使ったクエリ
	queryByProductCategory(svc, "Electronics")
}

func createTable(svc *dynamodb.Client) {
	_, err := svc.DescribeTable(context.TODO(), &dynamodb.DescribeTableInput{
		TableName: &tableName,
	})

	if err == nil {
		fmt.Println("Table already exists!")
		return
	}

	fmt.Println("Creating table...")

	_, err = svc.CreateTable(context.TODO(), &dynamodb.CreateTableInput{
		TableName: &tableName,
		AttributeDefinitions: []types.AttributeDefinition{
			{AttributeName: awsString("OrderID"), AttributeType: types.ScalarAttributeTypeS},
			{AttributeName: awsString("ProductCategory"), AttributeType: types.ScalarAttributeTypeS},
		},
		KeySchema: []types.KeySchemaElement{
			{AttributeName: awsString("OrderID"), KeyType: types.KeyTypeHash},
		},
		GlobalSecondaryIndexes: []types.GlobalSecondaryIndex{
			{
				IndexName: awsString(gsiName),
				KeySchema: []types.KeySchemaElement{
					{AttributeName: awsString("ProductCategory"), KeyType: types.KeyTypeHash},
				},
				Projection: &types.Projection{
					ProjectionType: types.ProjectionTypeAll,
				},
				ProvisionedThroughput: &types.ProvisionedThroughput{
					ReadCapacityUnits:  awsInt64(5),
					WriteCapacityUnits: awsInt64(5),
				},
			},
		},
		ProvisionedThroughput: &types.ProvisionedThroughput{
			ReadCapacityUnits:  awsInt64(5),
			WriteCapacityUnits: awsInt64(5),
		},
	})

	if err != nil {
		log.Fatalf("Failed to create table: %v", err)
	}

	fmt.Println("Table created successfully!")
}

func putItem(svc *dynamodb.Client, orderID, customerID, orderDate string, orderAmount int, productCategory string) {
	_, err := svc.PutItem(context.TODO(), &dynamodb.PutItemInput{
		TableName: &tableName,
		Item: map[string]types.AttributeValue{
			"OrderID":         &types.AttributeValueMemberS{Value: orderID},
			"CustomerID":      &types.AttributeValueMemberS{Value: customerID},
			"OrderDate":       &types.AttributeValueMemberS{Value: orderDate},
			"OrderAmount":     &types.AttributeValueMemberN{Value: fmt.Sprintf("%d", orderAmount)},
			"ProductCategory": &types.AttributeValueMemberS{Value: productCategory},
		},
	})

	if err != nil {
		log.Fatalf("Failed to put item: %v", err)
	}

	fmt.Printf("Inserted item: OrderID=%s, ProductCategory=%s\n", orderID, productCategory)
}

func queryByProductCategory(svc *dynamodb.Client, category string) {
	fmt.Printf("Querying items in category: %s\n", category)

	result, err := svc.Query(context.TODO(), &dynamodb.QueryInput{
		TableName:              &tableName,
		IndexName:              &gsiName,
		KeyConditionExpression: awsString("ProductCategory = :category"),
		ExpressionAttributeValues: map[string]types.AttributeValue{
			":category": &types.AttributeValueMemberS{Value: category},
		},
	})

	if err != nil {
		log.Fatalf("Failed to query items: %v", err)
	}

	for _, item := range result.Items {
		fmt.Printf("OrderID: %s, ProductCategory: %s\n",
			item["OrderID"].(*types.AttributeValueMemberS).Value,
			item["ProductCategory"].(*types.AttributeValueMemberS).Value,
		)
	}
}

func awsString(value string) *string {
	return &value
}

func awsInt64(value int64) *int64 {
	return &value
}
