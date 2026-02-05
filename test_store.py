from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_
import uuid

'''
TODO: Finish this test by...
1) Creating a function to test the PATCH request /store/order/{order_id}
2) *Optional* Consider using @pytest.fixture to create unique test data for each run
2) *Optional* Consider creating an 'Order' model in schemas.py and validating it in the test
3) Validate the response codes and values
4) Validate the response message "Order and pet status updated successfully"
'''
def test_patch_order_by_id():
    # 1) Create a unique pet that's available
    pets_resp = api_helpers.get_api_data("/pets/")
    assert pets_resp.status_code == 200
    existing_ids = [p.get("id") for p in pets_resp.json() if "id" in p]
    next_id = (max(existing_ids) + 1) if existing_ids else 100

    pet_payload = {
        "id": next_id,
        "name": f"order-pet-{uuid.uuid4().hex[:8]}",
        "type": "dog",
        "status": "available",
    }
    create_pet = api_helpers.post_api_data("/pets/", pet_payload)
    assert create_pet.status_code in (200, 201)

    # 2) Place an order for that pet
    order_create = api_helpers.post_api_data("/store/order", {"pet_id": next_id})
    assert order_create.status_code == 201
    order_json = order_create.json()
    validate(instance=order_json, schema=schemas.order)
    order_id = order_json["id"]
    assert_that(order_json["pet_id"], is_(next_id))

    # 3) Patch the order status
    patch_status = "sold"
    patched = api_helpers.patch_api_data(f"/store/order/{order_id}", {"status": patch_status})
    assert patched.status_code == 200
    patched_json = patched.json()
    validate(instance=patched_json, schema=schemas.order_patch_response)
    assert_that(patched_json.get("message"), is_("Order and pet status updated successfully"))

    # 4) Confirm the pet status was updated as well
    pet_get = api_helpers.get_api_data(f"/pets/{next_id}")
    assert pet_get.status_code == 200
    pet_json = pet_get.json()
    validate(instance=pet_json, schema=schemas.pet)
    assert_that(pet_json.get("status"), is_(patch_status))


def test_patch_order_by_id_400_invalid_status():
    """Edge case: invalid status should return a 400."""

    pets_resp = api_helpers.get_api_data("/pets/")
    assert pets_resp.status_code == 200
    existing_ids = [p.get("id") for p in pets_resp.json() if "id" in p]
    next_id = (max(existing_ids) + 1) if existing_ids else 100

    pet_payload = {
        "id": next_id,
        "name": f"order-pet-{uuid.uuid4().hex[:8]}",
        "type": "cat",
        "status": "available",
    }
    create_pet = api_helpers.post_api_data("/pets/", pet_payload)
    assert create_pet.status_code in (200, 201)

    order_create = api_helpers.post_api_data("/store/order", {"pet_id": next_id})
    assert order_create.status_code == 201
    order_id = order_create.json()["id"]

    patched = api_helpers.patch_api_data(f"/store/order/{order_id}", {"status": "nope"})
    assert patched.status_code == 400
    try:
        body = patched.json()
        assert_that(str(body.get("message", "")), contains_string("Invalid status"))
    except Exception:
        assert "Invalid status" in patched.text
