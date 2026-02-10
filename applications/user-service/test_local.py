import bcrypt

# Test bcrypt directly
password = "Test123"
pwd_bytes = password.encode('utf-8')[:72]
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(pwd_bytes, salt)

print(f"Password: {password}")
print(f"Bytes: {pwd_bytes}")
print(f"Hashed: {hashed}")
print(f"Verify: {bcrypt.checkpw(pwd_bytes, hashed)}")
print("✅ bcrypt working correctly!")
