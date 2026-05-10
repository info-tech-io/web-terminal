package main

import "testing"

func TestReverse(t *testing.T) {
	cases := []struct {
		in, want string
	}{
		{"hello", "olleh"},
		{"", ""},
		{"a", "a"},
		{"abcd", "dcba"},
		{"racecar", "racecar"},
	}
	for _, c := range cases {
		got := Reverse(c.in)
		if got != c.want {
			t.Errorf("Reverse(%q) = %q, want %q", c.in, got, c.want)
		}
	}
}
