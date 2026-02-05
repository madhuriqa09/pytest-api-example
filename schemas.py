pet = {
    "type": "object",
    "required": ["name", "type"],
    "properties": {
        "id": {
            "type": "integer"
        },
        "name": {
            "type": "string"
        },
        "type": {
            "type": "string",
            "enum": ["cat", "dog", "fish"]
        },
        "status": {
            "type": "string",
            "enum": ["available", "sold", "pending"]
        },
    }
}


# Response schema for POST /store/order
order = {
    "type": "object",
    "required": ["id", "pet_id"],
    "properties": {
        "id": {"type": "string"},
        "pet_id": {"type": "integer"},
        # status is added internally when orders are patched, but is not returned on create
        "status": {"type": "string", "enum": ["available", "sold", "pending"]},
    },
}


# Response schema for PATCH /store/order/{order_id}
order_patch_response = {
    "type": "object",
    "required": ["message"],
    "properties": {
        "message": {"type": "string"},
    },
}
