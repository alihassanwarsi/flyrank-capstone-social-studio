import pytest

import app.services.variant_service as variant_service_module
from app.services.variant_service import VariantService
from app.variants.validator import VariantValidationError


def test_generate_for_post_uses_stored_content_and_saves_three_variants(
    monkeypatch,
):
    stored_post = {
        "id": 10,
        "content": "Stored article content from PostgreSQL.",
    }

    monkeypatch.setattr(
        variant_service_module.SourcePostRepository,
        "get_by_id",
        lambda post_id: stored_post,
    )

    monkeypatch.setattr(
        variant_service_module.VariantRepository,
        "get_by_source_post",
        lambda post_id: [],
    )

    generated_calls = []

    def fake_generate_variant(*, platform, source_content):
        generated_calls.append(
            (platform, source_content)
        )

        return {
            "discord": "Discord version",
            "x": "Short X version #AI",
            "linkedin": "Professional LinkedIn version",
        }[platform]

    monkeypatch.setattr(
        variant_service_module,
        "generate_variant",
        fake_generate_variant,
    )

    saved_variants = []

    def fake_create(*, source_post_id, platform, content):
        row = {
            "id": len(saved_variants) + 1,
            "source_post_id": source_post_id,
            "platform": platform,
            "content": content,
        }

        saved_variants.append(row)
        return row

    monkeypatch.setattr(
        variant_service_module.VariantRepository,
        "create",
        fake_create,
    )

    result = VariantService.generate_for_post(10)

    assert len(result) == 3

    assert [item["platform"] for item in result] == [
        "discord",
        "x",
        "linkedin",
    ]

    assert all(
        source_content == stored_post["content"]
        for _, source_content in generated_calls
    )

    assert len(saved_variants) == 3


def test_invalid_variant_is_blocked_before_database_save(
    monkeypatch,
):
    stored_post = {
        "id": 20,
        "content": "Stored article.",
    }

    monkeypatch.setattr(
        variant_service_module.SourcePostRepository,
        "get_by_id",
        lambda post_id: stored_post,
    )

    monkeypatch.setattr(
        variant_service_module.VariantRepository,
        "get_by_source_post",
        lambda post_id: [],
    )

    def fake_generate_variant(*, platform, source_content):
        if platform == "x":
            return "A" * 300

        return "Valid platform content"

    monkeypatch.setattr(
        variant_service_module,
        "generate_variant",
        fake_generate_variant,
    )

    save_calls = []

    def fake_create(**kwargs):
        save_calls.append(kwargs)

    monkeypatch.setattr(
        variant_service_module.VariantRepository,
        "create",
        fake_create,
    )

    with pytest.raises(VariantValidationError):
        VariantService.generate_for_post(20)

    assert save_calls == []