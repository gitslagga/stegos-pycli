package main

import (
    "io"
    "fmt"
    "encoding/base64"
    "crypto/aes"
    "crypto/cipher" 
    "crypto/rand"
    "encoding/hex"
)

func encrypt(api_token []byte, payload string) []byte {  
    block, err := aes.NewCipher(api_token)
    if err != nil {
        panic(err)
    }
    // The IV needs to be unique, but not secure. Therefore it's common to
    // include it at the beginning of the ciphertext.
    ciphertext := make([]byte, aes.BlockSize+len(payload))
    iv := ciphertext[:aes.BlockSize]
    if _, err := io.ReadFull(rand.Reader, iv); err != nil {
        panic(err.Error())
    }
    stream := cipher.NewCTR(block, iv)
    stream.XORKeyStream(ciphertext[aes.BlockSize:], []byte(payload))
    return ciphertext
}

func decrypt(api_token []byte, ciphertext [] byte) string {  
    if len(ciphertext) < aes.BlockSize {  
        panic("invalid ciphertext")  
    }

    block, err := aes.NewCipher(api_token)
    if err != nil {
        panic(err)
    }

    iv := ciphertext[:aes.BlockSize]
    plaintext := make([]byte, len(ciphertext) - aes.BlockSize)
    stream  := cipher.NewCTR(block, iv)
    stream.XORKeyStream(plaintext, ciphertext[aes.BlockSize:])
    return string(plaintext[:])  
}

func main() {
    // API Token
    api_token_base64 := "ZgV+1oFFh0D8zL78bDU8jA=="
    api_token, err := base64.StdEncoding.DecodeString(api_token_base64)
    if err != nil {
        fmt.Println("Invalid API_TOKEN:", err)
        return
    }

    plaintext := "some text"
    fmt.Printf("Text: %s\n", plaintext)
    ciphertext := encrypt(api_token, plaintext)
    fmt.Printf("Encoded Text: %s\n", hex.EncodeToString(ciphertext))
    plaintext2 := decrypt(api_token, ciphertext)
    fmt.Printf("Decoded Text: %s\n", plaintext2)
}