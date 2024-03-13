from copy import deepcopy

import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)


@pytest.fixture
def mock_initial_domain_pools():
    return {
        'pool1': {'domain-a.xyz': 2, 'domain-b.xyz': 1},
        'pool2': {'domain-c.xyz': 3, 'domain-d.xyz': 1, 'domain-e.xyz': 2}
    }


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_pool_id():
    response = client.get("/path?pool_id=invalid_pool")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid pool ID"}


def test_redirect_with_mocked_domain_pools(mock_initial_domain_pools):
    with patch('app.main.initial_domain_pools', mock_initial_domain_pools):
        with patch('app.main.domain_pools', deepcopy(mock_initial_domain_pools)):
            response = client.get("/path?pool_id=pool1", allow_redirects=False)
            assert response.status_code == 302
            assert response.headers["location"].startswith("http://")
            assert response.headers["location"].endswith("/path")

            response = client.get("/path?pool_id=pool1&param1=value1&param2=value2", allow_redirects=False)
            assert response.status_code == 302
            assert "param1=value1" in response.headers["location"]
            assert "param2=value2" in response.headers["location"]

            response = client.get("/path", allow_redirects=False)
            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid pool ID"}


def test_redirect_multiple_times(mock_initial_domain_pools):
    with patch('app.main.initial_domain_pools', mock_initial_domain_pools):
        with patch('app.main.domain_pools', deepcopy(mock_initial_domain_pools)):
            domain_counts = {domain: weight for domain, weight in mock_initial_domain_pools['pool1'].items()}
            for _ in range(100):
                response = client.get("/path?pool_id=pool1", allow_redirects=False)
                assert response.status_code == 302
                chosen_domain = response.headers["location"].split("//")[1].split("/")[0]
                assert chosen_domain in domain_counts
                domain_counts[chosen_domain] -= 1
            assert abs(domain_counts['domain-a.xyz']) > abs(domain_counts['domain-b.xyz'])


def test_reset_pool_after_empty(mock_initial_domain_pools):
    with patch('app.main.initial_domain_pools', mock_initial_domain_pools):
        with patch('app.main.domain_pools', deepcopy(mock_initial_domain_pools)):
            for _ in range(3):
                response = client.get("/path?pool_id=pool1", allow_redirects=False)
                assert response.status_code == 302
            response = client.get("/path?pool_id=pool1", allow_redirects=False)
            assert response.status_code == 302
            assert response.headers["location"].split("//")[1].split("/")[0] in ['domain-a.xyz',
                                                                                 'domain-b.xyz']


def test_reset_pool_after_empty_domains():
    with patch('app.main.initial_domain_pools', {'pool1': {}}):
        with patch('app.main.domain_pools', deepcopy({'pool1': {}})):
            response = client.get("/path?pool_id=pool1", allow_redirects=False)
            assert response.status_code == 400
