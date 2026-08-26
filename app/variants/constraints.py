from dataclasses import dataclass


@dataclass(frozen=True)
class ConstraintProfile:
    max_length: int
    max_hashtags: int
    max_emojis: int
    max_exclamations: int | None = None
    reject_excessive_caps: bool = False
    forbidden_terms: tuple[str, ...] = ()


PLATFORM_CONSTRAINTS = {
    "discord": ConstraintProfile(
        max_length=1000,
        max_hashtags=3,
        max_emojis=2,
        reject_excessive_caps=True,
    ),
    "x": ConstraintProfile(
        max_length=280,
        max_hashtags=2,
        max_emojis=1,
        max_exclamations=1,
    ),
    "linkedin": ConstraintProfile(
        max_length=1300,
        max_hashtags=3,
        max_emojis=0,
        max_exclamations=1,
        forbidden_terms=("lol", "omg", "bro"),
    ),
}