from cryptography.fernet import Fernet
fernet_key = b"w9UOBC7V2y1cbn2mYd3O7wSHP2vKwvLzKqj_YpC6ZCk="
cipher = Fernet(fernet_key)

def get_token(question_id,email):
    data = f"{question_id},{email}".encode()
    token = cipher.encrypt(data).decode()
    print('encryption sucessfull')
    return token

def decrpyt_token(token):
    decrpyted_token = cipher.decrypt(token.encode()).decode()
    question_id, email = decrpyted_token.split(',')
    print('decrpytion sucessfull')
    return {
        'question_id':question_id,
        'email':email
    }



