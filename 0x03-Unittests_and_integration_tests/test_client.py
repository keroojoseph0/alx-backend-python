#!/usr/bin/env python3
"""
Unit tests for the GithubOrgClient class.

Tests include:
- org property
- _public_repos_url property
- public_repos method
"""
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

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the correct list of repo names."""
        # Mocked data returned by get_json
        repos_payload = [{"name": "repo1"}, {"name": "repo2"}]
        mock_get_json.return_value = repos_payload

        client = GithubOrgClient("test_org")

        # Mock the _public_repos_url property
        with patch.object(GithubOrgClient, "_public_repos_url", new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "https://fake.url/repos"

            result = client.public_repos()

            # Check that public_repos returns expected repo names
            self.assertEqual(result, ["repo1", "repo2"])

            # Check that _public_repos_url was called once
            mock_url.assert_called_once()

            # Check that get_json was called once with the mocked URL
            mock_get_json.assert_called_once_with("https://fake.url/repos")