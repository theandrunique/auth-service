from unittest.mock import AsyncMock


async def mock_redis_client(mocker):
    mock = AsyncMock()
    mocker.patch("src.auth.views.redis_client", mock)
    return mock
