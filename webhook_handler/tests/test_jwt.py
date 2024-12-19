import jwt
import pytest

def test_encode_decode():
    my_dict = {"name": "Alice", "age": 25, "city": "New York"}
    encoded_jwt = jwt.encode(my_dict, "secret", algorithm="HS256")
    print("encoded_jwt:"+encoded_jwt)
    
    decoded_dict = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
    print("decoded_dict:"+ str(decoded_dict))
    assert decoded_dict == my_dict