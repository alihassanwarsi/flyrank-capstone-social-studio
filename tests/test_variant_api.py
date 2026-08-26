from fastapi.testclient import TestClient

import app.api.variants as variants_api
from app.main import app
from app.services.variant_service import VariantServiceError


client = TestClient(app)


def test_generate_variants_endpoint(monkeypatch):
    fake_variants = [
        {
    "id": 1,
    "source_post_id": 10,
    "platform": "discord",
    "content": "Discord version",
    "status": "draft",
    "created_at": "2026-08-26T18:00:00Z",
    "updated_at": "2026-08-26T18:00:00Z",
},
        {
    "id": 2,
    "source_post_id": 10,
    "platform": "x",
    "content": "X version",
    "status": "draft",
    "created_at": "2026-08-26T18:00:00Z",
    "updated_at": "2026-08-26T18:00:00Z",
},
        {
    "id": 3,
    "source_post_id": 10,
    "platform": "linkedin",
    "content": "LinkedIn version",
    "status": "draft",
    "created_at": "2026-08-26T18:00:00Z",
    "updated_at": "2026-08-26T18:00:00Z",
}
    ]

    monkeypatch.setattr(
        variants_api.VariantService,
        "generate_for_post",
        lambda post_id: fake_variants,
    )

    response = client.post("/posts/10/variants")

    assert response.status_code == 201
    assert len(response.json()) == 3


def test_generate_variants_for_missing_post_returns_404(monkeypatch):
    def fake_generate(post_id):
        raise VariantServiceError("Source post not found.")

    monkeypatch.setattr(
        variants_api.VariantService,
        "generate_for_post",
        fake_generate,
    )

    response = client.post("/posts/999/variants")

    assert response.status_code == 404


def test_duplicate_generation_returns_409(monkeypatch):
    def fake_generate(post_id):
        raise VariantServiceError(
            "Variants already exist for this source post."
        )

    monkeypatch.setattr(
        variants_api.VariantService,
        "generate_for_post",
        fake_generate,
    )

    response = client.post("/posts/10/variants")

    assert response.status_code == 409