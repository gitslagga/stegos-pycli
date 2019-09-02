package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"io"
)

func encrypt_origin() {
	encKey := "3cYdoIdwr3b49eyuH92oPw=="
	cipherText := "+Ywz8IlmUhVrfklYNJFuom+dLZ2kpEWgTgvyvf5/JVGC2mPY2uYPSpxQk7bCrjInQ5yV3XQfjMUf35aMNJqt"

	encKeyDecoded, err := base64.StdEncoding.DecodeString(encKey)
	if err != nil {
		panic(err)
	}

	cipherTextDecoded, err := base64.StdEncoding.DecodeString(cipherText)
	if err != nil {
		panic(err)
	}

	block, err := aes.NewCipher([]byte(encKeyDecoded))
	if err != nil {
		panic(err)
	}

	iv := cipherTextDecoded[:aes.BlockSize]
	cipherTextBytes := []byte(cipherTextDecoded)

	plaintext := make([]byte, len(cipherTextBytes)-aes.BlockSize)
	stream := cipher.NewCTR(block, iv)
	stream.XORKeyStream(plaintext, cipherTextBytes[aes.BlockSize:])

	fmt.Println(string(plaintext))
}

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

func decrypt(api_token []byte, ciphertext []byte) string {
	if len(ciphertext) < aes.BlockSize {
		panic("invalid ciphertext")
	}

	block, err := aes.NewCipher(api_token)
	if err != nil {
		panic(err)
	}

	iv := ciphertext[:aes.BlockSize]
	plaintext := make([]byte, len(ciphertext)-aes.BlockSize)
	stream := cipher.NewCTR(block, iv)
	stream.XORKeyStream(plaintext, ciphertext[aes.BlockSize:])
	return string(plaintext[:])
}

func main() {
	api_token_base64 := "3cYdoIdwr3b49eyuH92oPw=="
	api_token, _ := base64.StdEncoding.DecodeString(api_token_base64)

	plaintext := "{'type': 'balance_info', 'account_id': '1', 'id': 1}"
	fmt.Printf("Text: %s\n", plaintext)
	ciphertext := encrypt(api_token, plaintext)
	fmt.Printf("Encoded Text: %s\n", hex.EncodeToString(ciphertext))

	cipherText, err := base64.StdEncoding.DecodeString("Sr7ulOn//xciIdQuRf5nqpgu7x79CCFVU2JLYzaDcFMRgE1FW3Mun3oJEHCO+32X/HU0tM9IiYNkDk5em/CSZYVG87dnSXzbwyWp6NODXVag3o+/GaWP")
	if err != nil {
		panic("base64 decode error")
	}
	plaintext2 := decrypt(api_token, cipherText)
	fmt.Printf("Decoded Text: %s\n", plaintext2)
}

//Text: {'type': 'balance_info', 'account_id': '1', 'id': 1}
//Encoded Text: 2caa05bcfc8a9e1092bae389bc230bbfa1de3bdf72b51a11c6483eb66802ee2d404fbb36284769cf571195784392a470d2a995989c7cf3fabe654d81ea594130afef432c
//Decoded Text: {"type":"rollback_micro_block","epoch":14020,"offset":59,"statuses":{}}
