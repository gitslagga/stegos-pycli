const crypto  = require('crypto')
const atob = require('atob')
const btoa = require('btoa')

let apiToken = "3cYdoIdwr3b49eyuH92oPw==";
const algorithm = 'aes-128-ctr'; // todo config
const tokenLength = 16; // todo config

const encrypt = (plaintext, key) => {
  const resizedIV = Buffer.allocUnsafe(tokenLength);
  const iv = crypto
    .createHash('sha256')
    .update(plaintext)
    .digest();
  iv.copy(resizedIV);
  const encryptor = crypto.createCipheriv(
    algorithm,
    Buffer.from(base64ToArrayBuffer(key)),
    resizedIV
  );
  return arrayBufferToBase64(
    Buffer.concat([resizedIV, encryptor.update(plaintext), encryptor.final()])
  );
};

const decrypt = (buffer, key) => {
  const resizedIV = Buffer.allocUnsafe(tokenLength);
  Buffer.from(buffer, 0, tokenLength).copy(resizedIV);
  const ct = Buffer.from(buffer, tokenLength);
  const decipher = crypto.createDecipheriv(
    algorithm,
    Buffer.from(key, 'base64'),
    resizedIV
  );
  const dec = Buffer.concat([decipher.update(ct), decipher.final()]);
  return dec.toString('utf8');
};

const base64ToArrayBuffer = base64 => {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i += 1) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

const arrayBufferToBase64 = buffer => {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}


const payload = {'type': 'balance_info', 'account_id': '1', 'id': 1}
encode = encrypt(JSON.stringify(payload), apiToken).toString('utf8')
console.log(encode)


const data = "QwVxuiPXH5YTUSRv1aJ+Y2ZpjwT1Q+QXcyP0q2oKrtEGrsabzcJPa+LXrLfKTHwzMV/0CNWC+Ho4yT6ec5D5STkp19s="
const decode = decrypt(base64ToArrayBuffer(data), apiToken)
console.log(decode)
console.log(JSON.parse(decode))


// +Ywz8IlmUhVrfklYNJFuom+dLZ2kpEWgTgvyvf5/JVGC2mPY2uYPSpxQk7bCrjInQ5yV3XQfjMUf35aMNJqt
// {"type": "balance_info", "account_id": "1", "id": 1}
// { type: 'balance_info', account_id: '1', id: 1 }