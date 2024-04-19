from src.emails.utils import render_email_template


async def test_template_verification_email():
    html_body = await render_email_template(
        template_name="confirm_email.html",
        context={
            "username": "test_username",
            "confirm_url": "test_confirm_url",
        },
    )
    assert "test_username" in html_body
    assert "test_confirm_url" in html_body


async def test_template_otp_email():
    html_body = await render_email_template(
        template_name="otp.html",
        context={"username": "test_username", "otp": "12345"},
    )
    assert "test_username" in html_body
    assert "12345" in html_body


async def test_template_reset_password_email():
    html_body = await render_email_template(
        template_name="reset_password.html",
        context={"token": "test_token"},
    )
    assert "test_token" in html_body
