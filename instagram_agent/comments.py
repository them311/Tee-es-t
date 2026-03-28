"""Comment template system with dynamic placeholders."""

import random
import re
from datetime import datetime


class CommentGenerator:
    """Generates comments from templates with dynamic placeholders.

    Supported placeholders:
        {username}  - Target post author's username
        {city}      - City from the targeting rule location
        {name}      - Name from the targeting rule
        {hashtag}   - Hashtag that matched
        {day}       - Current day of the week
        {emoji}     - Random relevant emoji
    """

    EMOJIS = ["🔥", "💪", "👏", "✨", "🙌", "💯", "❤️", "👍", "🎯", "⭐"]

    GREETINGS = [
        "Salut", "Hey", "Bonjour", "Coucou", "Hello",
    ]

    def __init__(self, templates: list[str] | None = None):
        self.templates = templates or self._default_templates()

    def generate(self, username: str = "", city: str = "", name: str = "",
                 hashtag: str = "") -> str:
        """Generate a comment from a random template."""
        template = random.choice(self.templates)
        return self._fill_template(template, username, city, name, hashtag)

    def _fill_template(self, template: str, username: str, city: str,
                       name: str, hashtag: str) -> str:
        now = datetime.now()
        replacements = {
            "username": f"@{username}" if username else "",
            "city": city,
            "name": name,
            "hashtag": f"#{hashtag}" if hashtag else "",
            "day": now.strftime("%A"),
            "emoji": random.choice(self.EMOJIS),
            "greeting": random.choice(self.GREETINGS),
        }

        result = template
        for key, value in replacements.items():
            result = result.replace(f"{{{key}}}", value)

        # Clean up double spaces from empty placeholders
        result = re.sub(r"\s{2,}", " ", result).strip()
        return result

    @staticmethod
    def _default_templates() -> list[str]:
        return [
            "{greeting} {username} ! Super post {emoji}",
            "{emoji} Trop bien ! {city} c'est magnifique",
            "{greeting} ! J'adore ce contenu {emoji} {hashtag}",
            "Wow {username}, incroyable {emoji}",
            "{emoji} Super contenu de {city} ! Continue comme ça {username}",
            "{greeting} {name} ! Quel post génial {emoji}",
            "J'adore {emoji} {hashtag}",
            "{greeting} ! Superbe photo {username} {emoji}",
            "Magnifique {emoji} {city} est tellement beau",
            "{greeting} {username} ! Top ce {day} {emoji}",
        ]
