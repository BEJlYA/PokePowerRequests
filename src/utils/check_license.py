import hashlib
import hmac
import time

SECRET_SALT = "lestnica"

def verify_license_key(user_email: str, license_key: str) -> bool:
    try:
        clean = license_key.replace("-", "")

        if len(clean) < 10:
            return False

        expires_str = clean[-10:]
        expires = int(expires_str)

        if expires < time.time():
            return False

        signature_part = clean[:-10]

        payload = f"{user_email}|{expires}"
        expected = hmac.new(
            key=SECRET_SALT.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()[:20]

        if signature_part == expected:
            return True
        else:
            return False

    except Exception as e:
        return False