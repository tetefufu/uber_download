from utils.creds import extract_bearer_token


def test_read_token():
    bearer_token = extract_bearer_token()
    assert len(bearer_token) > 900
