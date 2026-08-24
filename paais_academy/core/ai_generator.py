import json
import logging
import time
from typing import List, Optional

from django.conf import settings
from rest_framework import serializers

ValidationError = serializers.ValidationError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config — override LESSON_AI_MODEL in settings.py if needed
# ---------------------------------------------------------------------------

AI_MODEL = getattr(settings, "LESSON_AI_MODEL", "claude-3-5-sonnet")
AI_MAX_TOKENS = getattr(settings, "LESSON_AI_MAX_TOKENS", 4000)


class AIGenerationError(Exception):
    """Raised when the API call, or validation of its output, fails."""


# ---------------------------------------------------------------------------
# Output schema — mirrors the Lesson model's content fields
# ---------------------------------------------------------------------------

class QuizQuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
    options = serializers.ListField(child=serializers.CharField(), min_length=2, max_length=6)
    correct_answer_index = serializers.IntegerField(min_value=0)
    explanation = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        if data['correct_answer_index'] >= len(data['options']):
            raise serializers.ValidationError({'correct_answer_index': 'Must point to an option.'})
        return data


class LessonContentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    level = serializers.ChoiceField(choices=('starter', 'practitioner', 'champion'))
    duration_minutes = serializers.IntegerField(min_value=5, max_value=180)
    content_html = serializers.CharField()
    objectives = serializers.ListField(child=serializers.CharField(), min_length=1)
    sample_prompt = serializers.CharField(required=False, allow_blank=True, default='')
    ai_tools_covered = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    quiz_questions = QuizQuestionSerializer(many=True, required=False, default=list)

    def validate_content_html(self, value):
        lowered = value.lower()
        if any(token in lowered for token in ('<script', 'javascript:', ' onerror=', ' onclick=')):
            raise serializers.ValidationError('content_html contains unsafe HTML.')
        return value


class LessonContentSchema:
    def __init__(self, values):
        self.__dict__.update(values)
        self.generation_log_id = None

    @classmethod
    def model_validate(cls, value):
        serializer = LessonContentSerializer(data=value)
        serializer.is_valid(raise_exception=True)
        return cls(serializer.validated_data)

    def to_lesson_fields(self):
        return {
            'title': self.title,
            'description': self.description,
            'level': self.level,
            'duration_minutes': self.duration_minutes,
            'content_html': self.content_html,
            'objectives': self.objectives,
            'sample_prompt': self.sample_prompt,
            'ai_tools_covered': self.ai_tools_covered,
            'quiz_questions': self.quiz_questions,
        }


# Forcing a tool call (rather than parsing free text + json.loads) is the
# most reliable way to get valid JSON back from the model — malformed
# text output is the #1 cause of silent generation failures.
LESSON_TOOL_SCHEMA = {
    "name": "submit_lesson",
    "description": "Submit one structured lesson for the PAAIS Academy platform.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "level": {"type": "string", "enum": ["starter", "practitioner", "champion"]},
            "duration_minutes": {"type": "integer"},
            "content_html": {
                "type": "string",
                "description": "Full lesson body as clean semantic HTML (headings, paragraphs, lists). No <script> tags.",
            },
            "objectives": {"type": "array", "items": {"type": "string"}},
            "sample_prompt": {
                "type": "string",
                "description": "One example AI prompt a learner could reuse for this lesson.",
            },
            "ai_tools_covered": {"type": "array", "items": {"type": "string"}},
            "quiz_questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 2,
                            "maxItems": 6,
                        },
                        "correct_answer_index": {"type": "integer"},
                        "explanation": {"type": "string"},
                    },
                    "required": ["question", "options", "correct_answer_index"],
                },
            },
        },
        "required": ["title", "description", "level", "duration_minutes", "content_html", "objectives"],
    },
}


SYSTEM_PROMPT = (
    "You are a curriculum writer for PAAIS Academy, a platform that teaches "
    "business professionals (marketing, sales, finance, HR, operations, customer "
    "service, founders) how to use everyday AI tools like ChatGPT, Claude, and "
    "Perplexity in their work. Write practical, example-driven lessons with realistic "
    "business context (Europe, America, Asia, Middle East, and or Ghanaian / African examples where it fits "
    "naturally). Never invent statistics, tool features, or pricing you are not "
    "certain of. Call the submit_lesson tool exactly once with the complete lesson — "
    "do not respond with plain text."
)


def _build_user_prompt(topic: str, track_name: str, level: str, duration_minutes: Optional[int]) -> str:
    duration_hint = f"around {duration_minutes} minutes" if duration_minutes else "15-25 minutes"
    return (
        f"Track: {track_name}\n"
        f"Topic: {topic}\n"
        f"Target level: {level}\n"
        f"Target duration: {duration_hint}\n\n"
        "Generate one complete lesson: a clear title, a 1-2 sentence description, "
        "3-5 learning objectives, lesson content as HTML (intro, concept explanation, "
        "a worked example, a short practice task), one sample AI prompt the learner "
        "can reuse, the AI tools it covers, and 3-5 multiple choice quiz questions "
        "each with a correct_answer_index and a one-line explanation."
    )


def generate_lesson(
    track,
    topic: str,
    level: str = "starter",
    duration_minutes: Optional[int] = None,
    triggered_by=None,
) -> LessonContentSchema:
    """
    Call the Anthropic API to draft one lesson's content.

    Args:
        track: a Track instance — used for prompt context and logging.
        topic: what the lesson should cover.
        level: 'starter' | 'practitioner' | 'champion'.
        duration_minutes: optional target length.
        triggered_by: the User who requested generation (for logging/notifications).

    Returns:
        LessonContentSchema — validated, ready for .to_lesson_fields().

    Raises:
        AIGenerationError on API failure or schema validation failure.
    """
    api_key = getattr(settings, "ANTHROPIC_API_KEY", None)
    if not api_key:
        raise AIGenerationError("ANTHROPIC_API_KEY is not configured in settings.")

    try:
        import anthropic
    except ImportError as exc:
        raise AIGenerationError(
            "The Anthropic SDK is not installed. Install the project's AI dependencies first."
        ) from exc

    client = anthropic.Anthropic(api_key=api_key)
    user_prompt = _build_user_prompt(topic, track.name, level, duration_minutes)

    start = time.monotonic()
    try:
        response = client.messages.create(
            model=AI_MODEL,
            max_tokens=AI_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=[LESSON_TOOL_SCHEMA],
            tool_choice={"type": "tool", "name": "submit_lesson"},
            messages=[{"role": "user", "content": user_prompt}],
        )
    except anthropic.APIError as exc:
        logger.exception("Anthropic API call failed for topic=%r", topic)
        _log_generation(track, topic, level, triggered_by, ok=False, error=str(exc))
        raise AIGenerationError(f"AI request failed: {exc}") from exc

    elapsed = time.monotonic() - start

    tool_use_block = next(
        (b for b in response.content if b.type == "tool_use" and b.name == "submit_lesson"),
        None,
    )
    if tool_use_block is None:
        _log_generation(
            track, topic, level, triggered_by, ok=False,
            error="No tool_use block returned", response=response, elapsed=elapsed,
        )
        raise AIGenerationError("Model did not return structured lesson data.")

    try:
        lesson_data = LessonContentSchema.model_validate(tool_use_block.input)
    except ValidationError as exc:
        logger.error("Lesson schema validation failed: %s", exc)
        _log_generation(
            track, topic, level, triggered_by, ok=False,
            error=str(exc), response=response, elapsed=elapsed,
        )
        raise AIGenerationError(f"AI output failed validation: {exc}") from exc

    generation_log = _log_generation(
        track, topic, level, triggered_by, ok=True,
        response=response, elapsed=elapsed, prompt=user_prompt,
    )
    lesson_data.generation_log_id = generation_log.pk if generation_log else None
    return lesson_data


def _log_generation(track, topic, level, triggered_by, ok, response=None, error="", elapsed=None, prompt=""):
    """Persist a record of the generation call so spend and failures are auditable."""
    from .models import AIGenerationLog  # local import avoids a circular import at app load

    usage = getattr(response, "usage", None)
    try:
        response_json = {}
        if response:
            for block in getattr(response, "content", []):
                if getattr(block, "type", None) == "tool_use":
                    response_json = getattr(block, "input", {}) or {}
                    break
        return AIGenerationLog.objects.create(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            success=ok,
            error_message=(error or "")[:2000],
            prompt_text=prompt,
            response_json=response_json,
            model=AI_MODEL,
            input_tokens=getattr(usage, "input_tokens", 0) or 0,
            output_tokens=getattr(usage, "output_tokens", 0) or 0,
            duration_seconds=elapsed or 0,
        )
    except Exception:
        # A logging failure must never take down generation itself.
        logger.exception("Failed to write AIGenerationLog")