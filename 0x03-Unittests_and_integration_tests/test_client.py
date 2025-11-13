#!/usr/bin/env python3
import unittest
from unittest.mock import patch
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

