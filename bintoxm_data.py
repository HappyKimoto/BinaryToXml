# ascii not printable
b = bytes.fromhex('000102030405060708090A0B0C0D0E0F')
b += bytes.fromhex('00000000000000000000000000000000')

# ascii printable
b += bytes.fromhex('303132333435363738393A3B3C3D3E3F')
b += bytes.fromhex('00000000000000000000000000000000')

# utf-8
b += 'あいうえおかきく'.encode('cp932')
b += bytes.fromhex('00000000000000000000000000000000')

# code page 932
b += 'あいうえお'.encode('utf-8')
b += bytes.fromhex('00')
b += bytes.fromhex('00000000000000000000000000000000')

# mixed with null terminator
b += bytes.fromhex('0000')
b += 'あい'.encode('shift-jis') 
b += bytes.fromhex('00000000')
b += 'えお'.encode('shift-jis')
b += bytes.fromhex('0000')

# system time
b += bytes.fromhex('DC0707000200030010002A001100C902')
b += bytes.fromhex('00000000000000000000000000000000')

# repeated pattern
b += bytes.fromhex('01000500')
b += bytes.fromhex('02000600')
b += bytes.fromhex('03000700')

with open('bintoxml_data.dat', 'wb') as f:
    f.write(b)
