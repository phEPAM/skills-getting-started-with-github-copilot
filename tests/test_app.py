import copy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
_original_activities = copy.deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


def test_get_activities_returns_all():
    # Arrange
    expected_activity_names = set(_original_activities.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == expected_activity_names
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    new_email = "nina@mergington.edu"
    assert new_email not in activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_existing_student_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_success():
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"
    assert email_to_remove in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email_to_remove}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email_to_remove} from {activity_name}"}
    assert email_to_remove not in activities[activity_name]["participants"]


def test_remove_participant_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
