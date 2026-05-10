package mathutils

import "testing"

func TestMax(t *testing.T) {
	if Max([]int{}) != 0 {
		t.Error("Max([]) should be 0")
	}
	if Max([]int{3, 1, 4, 1, 5}) != 5 {
		t.Error("Max([3,1,4,1,5]) should be 5")
	}
	if Max([]int{-3, -1, -4}) != -1 {
		t.Error("Max([-3,-1,-4]) should be -1")
	}
}

func TestMin(t *testing.T) {
	if Min([]int{}) != 0 {
		t.Error("Min([]) should be 0")
	}
	if Min([]int{3, 1, 4, 1, 5}) != 1 {
		t.Error("Min([3,1,4,1,5]) should be 1")
	}
	if Min([]int{-3, -1, -4}) != -4 {
		t.Error("Min([-3,-1,-4]) should be -4")
	}
}

func TestSum(t *testing.T) {
	if Sum([]int{}) != 0 {
		t.Error("Sum([]) should be 0")
	}
	if Sum([]int{1, 2, 3, 4, 5}) != 15 {
		t.Error("Sum([1,2,3,4,5]) should be 15")
	}
	if Sum([]int{-1, 1}) != 0 {
		t.Error("Sum([-1,1]) should be 0")
	}
}
