"""
Tests for static file serving and root endpoint redirection.

Tests verify that the root endpoint properly redirects to the static files
and that static files are accessible.
"""

import pytest


class TestRootRedirect:
    """Tests for the GET / endpoint."""
    
    def test_root_redirects_to_static_index(self, client, reset_activities):
        """
        Arrange: A request to the root endpoint
        Act: Make GET request to /
        Assert: Response redirects to /static/index.html
        """
        # Arrange & Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code in (301, 302, 307, 308)  # Redirect status codes
        assert "/static/index.html" in response.headers["location"]
    
    def test_root_with_follow_redirects_returns_200(self, client, reset_activities):
        """
        Arrange: A request to the root with follow_redirects enabled
        Act: Make follow-redirect GET request to /
        Assert: Final response is 200
        """
        # Arrange & Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        assert response.status_code == 200


class TestStaticFiles:
    """Tests for static file serving."""
    
    def test_static_index_html_returns_200(self, client, reset_activities):
        """
        Arrange: A request to the index.html file
        Act: Make GET request to /static/index.html
        Assert: Response status is 200 and content is HTML
        """
        # Arrange & Act
        response = client.get("/static/index.html")
        
        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "<!DOCTYPE html>" in response.text or "<html" in response.text
    
    def test_static_index_html_contains_title(self, client, reset_activities):
        """
        Arrange: Request the index.html file
        Act: Get the HTML content
        Assert: Content contains expected title
        """
        # Arrange & Act
        response = client.get("/static/index.html")
        
        # Assert
        assert "Mergington High School Activities" in response.text
    
    def test_static_styles_css_returns_200(self, client, reset_activities):
        """
        Arrange: A request to the CSS file
        Act: Make GET request to /static/styles.css
        Assert: Response status is 200
        """
        # Arrange & Act
        response = client.get("/static/styles.css")
        
        # Assert
        assert response.status_code == 200
    
    def test_static_app_js_returns_200(self, client, reset_activities):
        """
        Arrange: A request to the JavaScript file
        Act: Make GET request to /static/app.js
        Assert: Response status is 200
        """
        # Arrange & Act
        response = client.get("/static/app.js")
        
        # Assert
        assert response.status_code == 200
