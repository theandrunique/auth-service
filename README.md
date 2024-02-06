# Refresh token

How it should works in my opinion? Let's write an example:

We have to have two endpoints:

- "/login/"

```python
@app.get("/login/")
async def login(login: str, password: str):
    # validation of login and password

    # creating refresh token
    refresh_token = create_refresh_token()
    return refresh_token
```

- "/refresh/"

```python
@app.get("/refresh/")
async def refresh(refresh_token: str)
    # validation that it's a real refresh token

    # creating access token
    access_token = create_access_token()
    return access_token
```

### Refresh token payload
```python
payload = {
    "sub": {
        "user_id": 795,
        # other field...
    }
    "mode": "refresh_token",
    "exp": 1707250352, # if necessary
}
```

### Access token payload
```python
payload = {
    "sub": {
        "user_id": 795,
        # other field...
    }
    "mode": "access_token",
    "exp": 1707250352, # if necessary
}
```