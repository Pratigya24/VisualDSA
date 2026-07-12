import time

import pytest

from app.core.security import (
    InvalidTokenError,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        assert hash_password("correct horse battery staple") != "correct horse battery staple"

    def test_verify_succeeds_for_correct_password(self):
        hashed = hash_password("s3cr3t-P@ssw0rd")
        assert verify_password("s3cr3t-P@ssw0rd", hashed) is True

    def test_verify_fails_for_incorrect_password(self):
        hashed = hash_password("s3cr3t-P@ssw0rd")
        assert verify_password("wrong-password", hashed) is False

    def test_same_password_produces_different_hashes(self):
        # bcrypt salts every hash — this guards against a regression to an
        # unsalted scheme, which would make hashes comparable/rainbow-tableable.
        assert hash_password("identical") != hash_password("identical")


class TestAccessToken:
    def test_round_trip(self):
        token = create_access_token(user_id="user-123")
        payload = decode_token(token, expected_type=TokenType.ACCESS)
        assert payload.sub == "user-123"
        assert payload.type == TokenType.ACCESS

    def test_rejects_wrong_token_type(self):
        token = create_access_token(user_id="user-123")
        with pytest.raises(InvalidTokenError):
            decode_token(token, expected_type=TokenType.REFRESH)

    def test_rejects_tampered_token(self):
        token = create_access_token(user_id="user-123")
        tampered = token[:-2] + ("aa" if not token.endswith("aa") else "bb")
        with pytest.raises(InvalidTokenError):
            decode_token(tampered, expected_type=TokenType.ACCESS)


class TestRefreshToken:
    def test_round_trip_and_jti_present(self):
        token, jti = create_refresh_token(user_id="user-123")
        payload = decode_token(token, expected_type=TokenType.REFRESH)
        assert payload.sub == "user-123"
        assert payload.jti == jti

    def test_each_refresh_token_has_unique_jti(self):
        _, jti_a = create_refresh_token(user_id="user-123")
        _, jti_b = create_refresh_token(user_id="user-123")
        assert jti_a != jti_b
