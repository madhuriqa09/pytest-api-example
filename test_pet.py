from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_
import uuid

'''
TODO: Finish this test by...
1) Troubleshooting and fixing the test failure
The purpose of this test is to validate the response matches the expected schema defined in schemas.py
'''
def test_pet_schema():
    test_endpoint = "/pets/1"

    response = api_helpers.get_api_data(test_endpoint)

    assert response.status_code == 200

    # Validate the response schema against the defined schema in schemas.py
    validate(instance=response.json(), schema=schemas.pet)

'''
TODO: Finish this test by...
1) Extending the parameterization to include all available statuses
2) Validate the appropriate response code
3) Validate the 'status' property in the response is equal to the expected status
4) Validate the schema for each object in the response
'''
@pytest.mark.parametrize("status", ["available", "pending", "sold"])
def test_find_by_status_200(status):
    test_endpoint = "/pets/findByStatus"
    params = {
        "status": status
    }

    # Create a known pet for this status so the test has something to assert on
    # (the seeded dataset doesn't include every status).
    created = None
    for _ in range(5):
        unique_id = int(uuid.uuid4().int % 1_000_000) + 10_000
        pet_payload = {
            "id": unique_id,
            "name": f"status-{status}-{unique_id}",
            "type": "dog",
            "status": status,
        }
        created = api_helpers.post_api_data("/pets/", pet_payload)
        if created.status_code in (200, 201):
            break
        if created.status_code != 409:
            break

    response = api_helpers.get_api_data(test_endpoint, params)

    assert response.status_code == 200

    pets = response.json()
    assert isinstance(pets, list)

    # Ensure at least one pet is returned for that status.
    assert any(p.get("status") == status for p in pets)

    for pet in pets:
        assert_that(pet.get("status"), is_(status))
        validate(instance=pet, schema=schemas.pet)

'''
TODO: Finish this test by...
1) Testing and validating the appropriate 404 response for /pets/{pet_id}
2) Parameterizing the test for any edge cases
'''
def test_get_by_id_404():
    # IDs are seeded as 0, 1, 2. Use very large values to avoid collisions
    # even if other tests create pets.
    test_ids = [999_999, 9_999_999, -1]

    for pet_id in test_ids:
        response = api_helpers.get_api_data(f"/pets/{pet_id}")
        assert response.status_code == 404

        # When the route matches (positive integers), Flask-RESTX returns JSON.
        # For negative integers, Flask's route converter may not match and you'll get
        # the default HTML 404 page.
        try:
            body = response.json()
            assert_that(str(body.get("message", "")), contains_string("not found"))
        except Exception:
            assert "Not Found" in response.text
