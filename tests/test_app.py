import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Set up test client
        Act: Call GET /activities
        Assert: Verify response contains all activities
        """
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert all(activity in activities for activity in expected_activities)
        assert activities["Chess Club"]["max_participants"] == 12


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """
        Arrange: Prepare a valid activity and email
        Act: Sign up a new student
        Assert: Verify student is added to participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email in participants
    
    def test_signup_duplicate_fails(self, client):
        """
        Arrange: User already registered for activity
        Act: Attempt to sign up same user again
        Assert: Verify duplicate signup is rejected
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_activity_not_found(self, client):
        """
        Arrange: Reference a non-existent activity
        Act: Attempt to sign up for invalid activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """
        Arrange: User is registered for an activity
        Act: Unregister from activity
        Assert: Verify participant is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        assert email not in participants
    
    def test_unregister_not_registered(self, client):
        """
        Arrange: User is not registered for activity
        Act: Attempt to unregister non-existent participant
        Assert: Verify 400 error is returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_activity_not_found(self, client):
        """
        Arrange: Reference a non-existent activity
        Act: Attempt to unregister from invalid activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestActivityWorkflow:
    """Integration tests for multi-step workflows"""
    
    def test_signup_then_unregister_workflow(self, client):
        """
        Arrange: Fresh activity state
        Act: Sign up a student, then unregister them
        Assert: Verify final state matches expectations
        """
        # Arrange
        activity_name = "Programming Class"
        email = "workflow@mergington.edu"
        original_count = len(client.get("/activities").json()[activity_name]["participants"])
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Assert - Verify signup worked
        after_signup_count = len(client.get("/activities").json()[activity_name]["participants"])
        assert after_signup_count == original_count + 1
        
        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Assert - Verify unregister worked
        final_count = len(client.get("/activities").json()[activity_name]["participants"])
        assert final_count == original_count
