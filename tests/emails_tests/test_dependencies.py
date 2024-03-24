import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.emails.dependencies import check_token
from src.emails.exceptions import InvalidToken
from src.emails.schemas import EmailTokenPayload
from src.emails.token_utils import gen_email_token


async def test_check_token_valid_token():
    jti = uuid4()
    token = gen_email_token(
        payload=EmailTokenPayload(
            sub="valid_sub",
            typ="email",
            jti=jti,
            exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=60),
        )
    )
    with patch("src.emails.dependencies.redis_client") as mock_redis_client:
        mock_redis_client.get = AsyncMock(return_value=jti.bytes)
        result = await check_token(token, 'key_prefix')

    assert result == 'valid_sub'



async def test_check_token_invalid_token():
    jti = uuid4()
    token = gen_email_token(
        payload=EmailTokenPayload(
            sub="valid_sub",
            typ="email",
            jti=uuid4(),
            exp=datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=60),
        )
    )
    with patch("src.emails.dependencies.redis_client") as mock_redis_client:
        with pytest.raises(InvalidToken):
            mock_redis_client.get = AsyncMock(return_value=jti.bytes)
            await check_token(token, 'key_prefix')
