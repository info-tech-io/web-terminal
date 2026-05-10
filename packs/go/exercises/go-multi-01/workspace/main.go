package main

import (
	"exercise/mathutils"
	"fmt"
)

func main() {
	nums := []int{3, 1, 4, 1, 5, 9}
	fmt.Println("Max:", mathutils.Max(nums))
	fmt.Println("Min:", mathutils.Min(nums))
	fmt.Println("Sum:", mathutils.Sum(nums))
}
