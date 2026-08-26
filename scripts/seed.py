from app.repositories.source_post_repository import (
    SourcePostRepository,
)


SAMPLE_TITLE = "Building Reliable AI Products"

SAMPLE_CONTENT = """
# Building Reliable AI Products

AI applications need more than good model
responses.

Reliable storage, validation, human review,
durable background processing, and clear
failure handling help turn prototypes into
dependable products.
""".strip()


def main():
    post = SourcePostRepository.create(
        source_type="markdown",
        title=SAMPLE_TITLE,
        content=SAMPLE_CONTENT,
    )

    print("Sample post created.")
    print(f"Post ID: {post['id']}")


if __name__ == "__main__":
    main()