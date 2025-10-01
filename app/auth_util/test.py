from access_tokens import create_access_token, verify_access_token

user_id = "1230ubaeubvk"
role = "user"

# data = {"user_id": user_id}
token = {
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoicHJhcmFiZGhhIiwicm9sZSI6InVzZXIiLCJleHAiOjE3NTkyNjkzNTJ9.wxjJtQp2sJCf8_GDqBV3MA2NIoIer6pI569cKXWFBPE",
  "token_type": "bearer"
}
# token = create_access_token(data)
# print(token)
print(verify_access_token(token["access_token"]))
payload = verify_access_token(token["access_token"])
user_id: str = payload.get("user_id")
print(user_id)