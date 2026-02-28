"""
Tests for the Activities API endpoints.

Tests cover the main functionality: retrieving activities, signing up for activities,
and withdrawing from activities. Uses the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_all_activities_returns_200(self, client, reset_activities):
        """
        Arrange: Request the activities endpoint
        Act: Make GET request to /activities
        Assert: Response status is 200 and contains all activities
        """
        # Arrange & Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """
        Arrange: Request activities endpoint
        Act: Get activities and check structure
        Assert: Each activity has required fields
        """
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_info in data.items():
            assert "description" in activity_info
            assert "schedule" in activity_info
            assert "max_participants" in activity_info
            assert "participants" in activity_info
            assert isinstance(activity_info["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_student_returns_200(self, client, reset_activities):
        """
        Arrange: A new student email not in Chess Club
        Act: POST signup for Chess Club
        Assert: Status is 200 and student is added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
    
    def test_signup_adds_student_to_participants(self, client, reset_activities):
        """
        Arrange: A new student and the Chess Club activity
        Act: Sign up the student
        Assert: Student appears in participants list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert email in participants
    
    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """
        Arrange: A student already signed up for Chess Club
        Act: Try to sign up the same student again
        Assert: Status is 400 (conflict) with appropriate message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: A non-existent activity name
        Act: Try to sign up for that activity
        Assert: Status is 404 (not found)
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestWithdrawFromActivity:
    """Tests for the POST /activities/{activity_name}/withdraw endpoint."""
    
    def test_withdraw_signed_up_student_returns_200(self, client, reset_activities):
        """
        Arrange: A student signed up for Chess Club
        Act: POST withdraw request
        Assert: Status is 200 and student is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/withdraw",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
    
    def test_withdraw_removes_student_from_participants(self, client, reset_activities):
        """
        Arrange: A student in Chess Club
        Act: Withdraw the student
        Assert: Student is no longer in participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/withdraw",
            params={"email": email}
        )
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert email not in participants
    
    def test_withdraw_not_signed_up_student_returns_404(self, client, reset_activities):
        """
        Arrange: A student NOT signed up for Drama Club
        Act: Try to withdraw the student
        Assert: Status is 404 (not found)
        """
        # Arrange
        activity_name = "Drama Club"
        email = "student@mergington.edu"  # Not in Drama Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/withdraw",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Student not registered" in response.json()["detail"]
    
    def test_withdraw_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: A non-existent activity name
        Act: Try to withdraw from that activity
        Assert: Status is 404 (not found)
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/withdraw",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestActivityParticipationFlow:
    """Integration tests for signup and withdrawal workflows."""
    
    def test_signup_then_withdraw_flow(self, client, reset_activities):
        """
        Arrange: A new student
        Act: Sign up, verify participation, then withdraw
        Assert: Student is added, then removed correctly
        """
        # Arrange
        activity_name = "Programming Class"
        email = "integration@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Assert - Verify signup
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email in participants
        
        # Act - Withdraw
        withdraw_response = client.post(
            f"/activities/{activity_name}/withdraw",
            params={"email": email}
        )
        assert withdraw_response.status_code == 200
        
        # Assert - Verify withdrawal
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email not in participants
