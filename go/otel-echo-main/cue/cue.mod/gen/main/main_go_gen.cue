// Code generated by cue get go. DO NOT EDIT.

//cue:generate cue get go main

package main

// Person はGoの構造体で、CUEスキーマに準拠する必要があります。
#Person: {
	Name: string
	Age:  int & <120
}
