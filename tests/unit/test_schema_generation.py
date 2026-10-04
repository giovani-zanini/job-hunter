"""Generated contracts describe the public modules without identity DTOs."""

import json

from scripts.generate_json_schemas import generated_files


def test_generated_schemas_have_no_identity_contracts():
    files = generated_files()
    assert files
    for content in files.values():
        schema = json.loads(content)
        assert "AuthenticatedUser" not in schema.get("x-models", {}).get("shared", {})
        assert "ProfileUser" not in schema.get("x-models", {}).get("shared", {})
    user_schema = next(
        json.loads(content)
        for path, content in files.items()
        if path.as_posix().endswith("profile/features/user/schema.json")
    )
    assert "external_id" not in json.dumps(user_schema)
    assert "is_anonymous" in json.dumps(user_schema)
