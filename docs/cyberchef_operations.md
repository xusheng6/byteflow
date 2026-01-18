# CyberChef Operations Reference

This document lists all 463 operations from CyberChef, organized by category. Use this as a reference for implementing new nodes in ByteFlow.

## Summary

| Category | Count |
|----------|-------|
| Default | 200 |
| Crypto | 57 |
| Ciphers | 54 |
| Image | 28 |
| Code | 23 |
| Compression | 19 |
| Encodings | 14 |
| Regex | 13 |
| PublicKey | 11 |
| Hashing | 8 |
| Bletchley | 7 |
| Serialise | 6 |
| PGP | 6 |
| Charts | 5 |
| URL | 3 |
| Protobuf | 2 |
| Others | 8 |

---

## Default (200 operations)

ADD, Add line numbers, Alternating Caps, AND, Bacon Cipher Decode, Bacon Cipher Encode, Bit shift left, Bit shift right, Caret/M-decode, Cartesian Product, Change IP format, Chi Square, Comment, Conditional Jump, Convert area, Convert data units, Convert distance, Convert Leet Speak, Convert mass, Convert speed, Convert to NATO alphabet, Count occurrences, CRC Checksum, CSV to JSON, DateTime Delta, Dechunk HTTP response, Decode NetBIOS Name, Defang IP Addresses, Defang URL, Detect File Type, Divide, DNS over HTTPS, Drop bytes, Drop nth bytes, ELF Info, Encode NetBIOS Name, Escape string, Escape Unicode Characters, Expand alphabet range, Extract Files, Extract ID3, Fang URL, Fernet Decrypt, Fernet Encrypt, File Tree, Fork, Format MAC addresses, Frequency distribution, From Base, From Base32, From Base45, From Base58, From Base62, From Base64, From Base85, From Base92, From BCD, From Binary, From Braille, From Case Insensitive Regex, From Charcode, From Decimal, From Float, From Hex, From Hex Content, From Hexdump, From Modhex, From Morse Code, From Octal, From Quoted Printable, From UNIX Timestamp, Fuzzy Match, Generate De Bruijn Sequence, Generate HOTP, Generate Lorem Ipsum, Generate TOTP, Get All Casings, Get Time, Group IP addresses, Hamming Distance, Haversine distance, Head, HTML To Text, HTTP request, Index of Coincidence, IPv6 Transition Addresses, JSON to CSV, JSON to YAML, Jump, Label, Levenshtein Distance, Luhn Checksum, Magic, Mean, Median, Merge, Microsoft Script Decoder, MIME Decoding, Multiply, NOT, Numberwang, Offset checker, OR, P-list Viewer, Pad lines, Parse colour code, Parse DateTime, Parse IP range, Parse IPv4 header, Parse IPv6 address, Parse SSH Host Key, Parse TCP, Parse TLS record, Parse TLV, Parse UDP, Parse UNIX file permissions, PEM to Hex, PHP Deserialize, PHP Serialize, Play Media, Power Set, RAKE, Remove Diacritics, Remove line numbers, Remove null bytes, Remove whitespace, Return, Reverse, ROT13, ROT13 Brute Force, ROT47, ROT47 Brute Force, ROT8000, Rotate left, Rotate right, Scan for Embedded Files, Set Difference, Set Intersection, Set Union, Show Base64 offsets, Shuffle, Sleep, Sort, Split, Standard Deviation, Strip HTML tags, Strip HTTP headers, Strip IPv4 header, Strip TCP header, Strip UDP header, SUB, Subsection, Substitute, Subtract, Sum, Swap case, Swap endianness, Symmetric Difference, Tail, Take bytes, Take nth bytes, To Base, To Base32, To Base45, To Base58, To Base62, To Base64, To Base85, To Base92, To BCD, To Binary, To Braille, To Case Insensitive Regex, To Charcode, To Decimal, To Float, To Hex, To Hex Content, To Hexdump, To Lower case, To Modhex, To Morse Code, To Octal, To Quoted Printable, To Table, To UNIX Timestamp, To Upper case, Translate DateTime Format, Unescape string, Unescape Unicode Characters, Unicode Text Format, Unique, UNIX Timestamp to Windows Filetime, VarInt Decode, VarInt Encode, Windows Filetime to UNIX Timestamp, XKCD Random Number, XOR, XOR Brute Force, YAML to JSON

## Crypto (57 operations)

Adler-32 Checksum, Analyse hash, Analyse UUID, Argon2, Argon2 compare, Bcrypt, Bcrypt compare, Bcrypt parse, CipherSaber2 Decrypt, CipherSaber2 Encrypt, CMAC, Compare CTPH hashes, Compare SSDEEP hashes, CTPH, Derive HKDF key, Fletcher-16 Checksum, Fletcher-32 Checksum, Fletcher-64 Checksum, Fletcher-8 Checksum, Generate all checksums, Generate all hashes, Generate UUID, HAS-160, HASSH Client Fingerprint, HASSH Server Fingerprint, HMAC, JA3 Fingerprint, JA3S Fingerprint, JA4 Fingerprint, JA4Server Fingerprint, JWT Decode, JWT Sign, JWT Verify, Keccak, LM Hash, LS47 Decrypt, LS47 Encrypt, MD2, MD4, MD5, MD6, NT Hash, RIPEMD, Scrypt, SHA0, SHA1, SHA2, SHA3, Shake, SM2 Decrypt, SM2 Encrypt, SM3, Snefru, SSDEEP, TCP/IP Checksum, Whirlpool, XOR Checksum

## Ciphers (54 operations)

A1Z26 Cipher Decode, A1Z26 Cipher Encode, AES Decrypt, AES Encrypt, AES Key Unwrap, AES Key Wrap, Affine Cipher Decode, Affine Cipher Encode, Atbash Cipher, Bifid Cipher Decode, Bifid Cipher Encode, Blowfish Decrypt, Blowfish Encrypt, Caesar Box Cipher, Cetacean Cipher Decode, Cetacean Cipher Encode, ChaCha, Derive EVP key, Derive PBKDF2 key, DES Decrypt, DES Encrypt, ECDSA Sign, ECDSA Signature Conversion, ECDSA Verify, Generate ECDSA Key Pair, Generate RSA Key Pair, GOST Decrypt, GOST Encrypt, GOST Key Unwrap, GOST Key Wrap, GOST Sign, GOST Verify, Pseudo-Random Number Generator, Rabbit, Rail Fence Cipher Decode, Rail Fence Cipher Encode, RC2 Decrypt, RC2 Encrypt, RC4, RC4 Drop, RSA Decrypt, RSA Encrypt, RSA Sign, RSA Verify, Salsa20, SM4 Decrypt, SM4 Encrypt, Triple DES Decrypt, Triple DES Encrypt, Vigenère Decode, Vigenère Encode, XSalsa20, XXTEA Decrypt, XXTEA Encrypt

## Image (28 operations)

Add Text To Image, Blur Image, Contain Image, Convert Image Format, Cover Image, Crop Image, Dither Image, Extract EXIF, Extract LSB, Extract RGBA, Flip Image, Generate Image, Generate QR Code, Image Brightness / Contrast, Image Filter, Image Hue/Saturation/Lightness, Image Opacity, Invert Image, Normalise Image, Parse QR Code, Randomize Colour Palette, Remove EXIF, Render Image, Resize Image, Rotate Image, Sharpen Image, Split Colour Channels, View Bit Plane

## Code (23 operations)

CSS Beautify, CSS Minify, CSS selector, From MessagePack, Generic Code Beautify, JavaScript Beautify, JavaScript Minify, JavaScript Parser, JPath expression, JSON Beautify, JSON Minify, Jsonata Query, Render Markdown, SQL Beautify, SQL Minify, Syntax highlighter, To Camel case, To Kebab case, To MessagePack, To Snake case, XML Beautify, XML Minify, XPath expression

## Compression (19 operations)

Bzip2 Compress, Bzip2 Decompress, Gunzip, Gzip, LZ4 Compress, LZ4 Decompress, LZMA Compress, LZMA Decompress, LZNT1 Decompress, LZString Compress, LZString Decompress, Raw Deflate, Raw Inflate, Tar, Untar, Unzip, Zip, Zlib Deflate, Zlib Inflate

## Encodings (14 operations)

AMF Decode, AMF Encode, Citrix CTX1 Decode, Citrix CTX1 Encode, Decode text, Encode text, From HTML Entity, From Punycode, Normalise Unicode, Rison Decode, Rison Encode, Text Encoding Brute Force, To HTML Entity, To Punycode

## Regex (13 operations)

Extract dates, Extract domains, Extract email addresses, Extract file paths, Extract hashes, Extract IP addresses, Extract MAC addresses, Extract URLs, Filter, Find / Replace, Register, Regular expression, Strings

## PublicKey (11 operations)

Hex to Object Identifier, Hex to PEM, JWK to PEM, Object Identifier to Hex, Parse ASN.1 hex string, Parse CSR, Parse X.509 certificate, Parse X.509 CRL, PEM to JWK, Public Key from Certificate, Public Key from Private Key

## Hashing (8 operations)

BLAKE2b, BLAKE2s, BLAKE3, Convert co-ordinate format, GOST Hash, MurmurHash3, Show on map, Streebog

## Bletchley (7 operations)

Bombe, Colossus, Enigma, Lorenz, Multiple Bombe, SIGABA, Typex

## Serialise (6 operations)

Avro to JSON, BSON deserialise, BSON serialise, CBOR Decode, CBOR Encode, Parse ObjectID timestamp

## PGP (6 operations)

Generate PGP Key Pair, PGP Decrypt, PGP Decrypt and Verify, PGP Encrypt, PGP Encrypt and Sign, PGP Verify

## Charts (5 operations)

Entropy, Heatmap chart, Hex Density chart, Scatter chart, Series chart

## URL (3 operations)

Parse URI, URL Decode, URL Encode

## Protobuf (2 operations)

Protobuf Decode, Protobuf Encode

## Other Categories (1 operation each)

- **Diff**: Diff
- **Handlebars**: Template
- **Jq**: Jq
- **OCR**: Optical Character Recognition
- **Shellcode**: Disassemble x86
- **UserAgent**: Parse User Agent
- **Yara**: YARA Rules

---

## ByteFlow Implementation Status

### Implemented ✅
- XOR, RC4, AES, Base64 (Crypto)
- MD5, SHA1, SHA256 (Hash)
- URL Encode/Decode, Hex Encode/Decode, ROT, Atbash (Encoding)
- Reverse, Zlib, Gzip, Substring, Repeat (Utility)
- Hex Input, Text Input, File Input, Output (I/O)

### High Priority for Implementation 🔴
- Vigenère Cipher
- DES / Triple DES
- Blowfish
- From/To Binary
- From/To Base32
- Extract IPs/URLs/emails (Regex)
- JSON Beautify/Minify
- Find/Replace (Regex)
- Magic (auto-detect)
- HMAC
- CRC Checksum

### Medium Priority 🟡
- ChaCha / Salsa20
- Rail Fence Cipher
- Affine Cipher
- BLAKE2/3
- Entropy visualization
- Bit shift operations
- Swap endianness
- From/To Charcode
