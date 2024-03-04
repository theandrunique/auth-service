import secrets
import string

import pyotp

secret = pyotp.random_base32()

totp = pyotp.TOTP(secret)

otp = totp.now()

print("Сгенерированный OTP:", otp)

if totp.verify(otp):
    print("OTP верен")
else:
    print("OTP неверен")

def gen_otp() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(6))

print(gen_otp())
