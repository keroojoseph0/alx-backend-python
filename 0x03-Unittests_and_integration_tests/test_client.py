#!/usr/bin/env python3
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient

class TestGithubOrgClient(unittest.TestCase):
    """Test GithubOrgClient.org method."""

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that org returns correct value and get_json is called once."""
        mock_get_json.return_value = {"mocked": True}

        client = GithubOrgClient(org_name)
        result = client.org  # access property without parentheses

        self.assertEqual(result, {"mocked": True})
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the repos_url from org property."""
        payload = {"repos_url": "https://api.github.com/orgs/test/repos"}
        client = GithubOrgClient("test_org")

        with patch("client.GithubOrgClient.org", new_callable=PropertyMock) as mock_org:
            mock_org.return_value = payload
            result = client._public_repos_url
            self.assertEqual(result, payload["repos_url"])
