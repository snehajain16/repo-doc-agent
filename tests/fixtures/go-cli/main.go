package main

import (
    "fmt"
    "os"
)

func main() {
    if len(os.Args) < 2 {
        fmt.Fprintln(os.Stderr, "Usage: greet <name>")
        os.Exit(1)
    }
    fmt.Printf("Hello, %s!\n", os.Args[1])
}
