```python
"""
PAAIS Academy - AI Lesson Generator

Generates structured lessons using the Anthropic Messages API and validates
the returned lesson against Django REST Framework serializers.

Configuration is read from Django settings:

    ANTHROPIC_API_KEY
    LESSON_AI_MODEL
    LESSON_AI_MAX_TOKENS

Example settings:

    ANTHROPIC_API_KEY = config("ANTHROPIC_API_KEY", default="")
    LESSON_AI_MODEL = config("LESSON_AI_MODEL", default="")
    LESSON_AI_MAX_TOKENS = config(
        "LESSON_AI_MAX_TOKENS",
        default=4000,
        cast=int,
    )
"""

import logging
import time
from typing import Any, Dict, Optional

from django.conf import settings
from rest_framework import serializers

logger = logging.getLogger(__name__)

ValidationError = serializers.ValidationError


# ============================================================================
# CONFIGURATION
# ============================================================================

def _get_ai_model() -> str:
    """
    Return the configured Anthropic model.

    We intentionally do not provide a guessed model fallback. This prevents
    production from silently using an obsolete or invalid model ID.
    """
    model = getattr(settings, "LESSON_AI_MODEL", None)

    if not model:
        raise RuntimeError(
            "LESSON_AI_MODEL is not configured. "
            "Set LESSON_AI_MODEL in Django settings/environment variables."
        )

    return str(model).strip()


def _get_max_tokens() -> int:
    """
    Return the configured maximum output tokens.
    """
    value = getattr(settings, "LESSON_AI_MAX_TOKENS", 4000)

    try:
        value = int(value)
    except (TypeError, ValueError):
        logger.warning(
            "Invalid LESSON_AI_MAX_TOKENS=%r. Falling back to 4000.",
            value,
        )
        value = 4000

    if value < 1:
        logger.warning(
            "LESSON_AI_MAX_TOKENS must be greater than zero. "
            "Falling back to 4000."
        )
        value = 4000

    return value


# ============================================================================
# EXCEPTIONS
# ============================================================================

class AIGenerationError(Exception):
    """
    Raised when AI lesson generation fails.

    This covers:
    - Missing configuration
    - Missing Anthropic SDK
    - Anthropic API errors
    - Missing tool response
    - Invalid AI output
    - Unexpected response structures
    """


# ============================================================================
# OUTPUT SERIALIZERS
# ============================================================================

class QuizQuestionSerializer(serializers.Serializer):
    question = serializers.CharField()

    options = serializers.ListField(
        child=serializers.CharField(),
        min_length=2,
        max_length=6,
    )

    correct_answer_index = serializers.IntegerField(
        min_value=0,
    )

    explanation = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    def validate(self, data):
        correct_index = data["correct_answer_index"]
        options = data["options"]

        if correct_index >= len(options):
            raise serializers.ValidationError(
                {
                    "correct_answer_index": (
                        "Must point to a valid option."
                    )
                }
            )

        return data


class LessonContentSerializer(serializers.Serializer):
    title = serializers.CharField(
        max_length=255,
    )

    description = serializers.CharField()

    level = serializers.ChoiceField(
        choices=(
            "starter",
            "practitioner",
            "champion",
        ),
    )

    duration_minutes = serializers.IntegerField(
        min_value=5,
        max_value=180,
    )

    content_html = serializers.CharField()

    objectives = serializers.ListField(
        child=serializers.CharField(),
        min_length=1,
    )

    sample_prompt = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    ai_tools_covered = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )

    quiz_questions = QuizQuestionSerializer(
        many=True,
        required=False,
        default=list,
    )

    def validate_content_html(self, value):
        """
        Basic protection against obviously dangerous HTML.

        This is not intended to replace proper HTML sanitization when
        rendering content to users.
        """
        lowered = value.lower()

        unsafe_tokens = (
            "<script",
            "javascript:",
            " onerror=",
            " onclick=",
            " onload=",
            " onmouseover=",
        )

        if any(token in lowered for token in unsafe_tokens):
            raise serializers.ValidationError(
                "content_html contains unsafe HTML."
            )

        return value


# ============================================================================
# INTERNAL LESSON OBJECT
# ============================================================================

class LessonContentSchema:
    """
    Lightweight validated object used between AI generation and the Lesson
    model.
    """

    def __init__(self, values: Dict[str, Any]):
        self.__dict__.update(values)
        self.generation_log_id = None

    @classmethod
    def model_validate(cls, value):
        serializer = LessonContentSerializer(data=value)
        serializer.is_valid(raise_exception=True)

        return cls(serializer.validated_data)

    def to_lesson_fields(self):
        """
        Convert the generated lesson into fields suitable for the Lesson model.
        """
        return {
            "title": self.title,
            "description": self.description,
            "level": self.level,
            "duration_minutes": self.duration_minutes,
            "content_html": self.content_html,
            "objectives": self.objectives,
            "sample_prompt": self.sample_prompt,
            "ai_tools_covered": self.ai_tools_covered,
            "quiz_questions": self.quiz_questions,
        }


# ============================================================================
# ANTHROPIC TOOL SCHEMA
# ============================================================================

LESSON_TOOL_SCHEMA = {
    "name": "submit_lesson",
    "description": (
        "Submit one complete structured lesson for the PAAIS Academy "
        "platform."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Clear and practical lesson title.",
            },
            "description": {
                "type": "string",
                "description": (
                    "A concise 1-2 sentence description of the lesson."
                ),
            },
            "level": {
                "type": "string",
                "enum": [
                    "starter",
                    "practitioner",
                    "champion",
                ],
            },
            "duration_minutes": {
                "type": "integer",
                "minimum": 5,
                "maximum": 180,
            },
            "content_html": {
                "type": "string",
                "description": (
                    "Complete lesson body as clean semantic HTML. "
                    "Use headings, paragraphs, lists, tables where useful, "
                    "and other safe semantic elements. "
                    "Do not include script tags or JavaScript."
                ),
            },
            "objectives": {
                "type": "array",
                "items": {
                    "type": "string",
                },
                "minItems": 1,
                "maxItems": 10,
            },
            "sample_prompt": {
                "type": "string",
                "description": (
                    "One practical AI prompt a learner can reuse."
                ),
            },
            "ai_tools_covered": {
                "type": "array",
                "items": {
                    "type": "string",
                },
            },
            "quiz_questions": {
                "type": "array",
                "minItems": 3,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                        },
                        "options": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "minItems": 2,
                            "maxItems": 6,
                        },
                        "correct_answer_index": {
                            "type": "integer",
                            "minimum": 0,
                        },
                        "explanation": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "question",
                        "options",
                        "correct_answer_index",
                        "explanation",
                    ],
                },
            },
        },
        "required": [
            "title",
            "description",
            "level",
            "duration_minutes",
            "content_html",
            "objectives",
            "sample_prompt",
            "ai_tools_covered",
            "quiz_questions",
        ],
    },
}


# ============================================================================
# SYSTEM PROMPT
# ============================================================================

SYSTEM_PROMPT = """
You are a curriculum writer for PAAIS Academy.

PAAIS Academy teaches business professionals how to use practical AI tools
such as ChatGPT, Claude, Perplexity, and other relevant workplace AI tools.

The audience includes:

- Marketing professionals
- Sales professionals
- Finance professionals
- HR professionals
- Operations professionals
- Customer service professionals
- Business owners
- Founders
- Consultants
- Government and NGO professionals

Your lessons must be:

1. Practical
2. Example-driven
3. Easy to understand
4. Professionally written
5. Immediately applicable to real work
6. Appropriate for the learner's specified level

Use realistic business contexts from Europe, America, Asia, the Middle East,
Ghana, and other African markets when they fit naturally.

Do not invent statistics, product capabilities, pricing, regulations,
companies, or factual claims that you are uncertain about.

The lesson should explain concepts clearly before moving into examples.

Include:

- Introduction
- Concept explanation
- Practical/worked example
- Practical learner exercise
- Reusable AI prompt
- AI tools covered
- Multiple-choice quiz

The content_html must contain clean semantic HTML.

Never include:

- <script> tags
- JavaScript
- Event-handler attributes
- Unsafe HTML
- Fake statistics
- Unsupported claims

You MUST call the submit_lesson tool exactly once.

Do not respond with ordinary plain text.
""".strip()


# ============================================================================
# PROMPT BUILDER
# ============================================================================

def _build_user_prompt(
    topic: str,
    track_name: str,
    level: str,
    duration_minutes: Optional[int],
) -> str:
    """
    Build the user prompt for lesson generation.
    """

    duration_hint = (
        f"approximately {duration_minutes} minutes"
        if duration_minutes
        else "approximately 15-25 minutes"
    )

    return f"""
Track: {track_name}

Topic: {topic}

Target level: {level}

Target duration: {duration_hint}

Generate one complete lesson for this topic.

The lesson must include:

1. A clear, useful title.
2. A concise 1-2 sentence description.
3. 3-5 learning objectives.
4. A complete lesson body in semantic HTML.
5. A clear introduction.
6. A practical explanation of the main concepts.
7. At least one realistic worked business example.
8. A short practical exercise for the learner.
9. One reusable AI prompt.
10. The AI tools relevant to the lesson.
11. 3-5 multiple-choice quiz questions.
12. The correct answer index for every quiz question.
13. A short explanation for every quiz answer.

Make the lesson practical rather than theoretical.

Use examples that make sense for actual business professionals.

The learner should be able to apply something from the lesson immediately
after completing it.
""".strip()


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_lesson(
    track,
    topic: str,
    level: str = "starter",
    duration_minutes: Optional[int] = None,
    triggered_by=None,
) -> LessonContentSchema:
    """
    Generate one structured lesson using Anthropic.

    Args:
        track:
            Track model instance.

        topic:
            Lesson topic.

        level:
            starter | practitioner | champion

        duration_minutes:
            Optional target lesson duration.

        triggered_by:
            User who triggered generation.

    Returns:
        LessonContentSchema

    Raises:
        AIGenerationError:
            If generation or validation fails.
    """

    # ----------------------------------------------------------------------
    # Configuration
    # ----------------------------------------------------------------------

    try:
        ai_model = _get_ai_model()
    except RuntimeError as exc:
        logger.error(str(exc))

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=str(exc),
            model="",
        )

        raise AIGenerationError(str(exc)) from exc

    max_tokens = _get_max_tokens()

    api_key = getattr(
        settings,
        "ANTHROPIC_API_KEY",
        None,
    )

    if not api_key:
        message = (
            "ANTHROPIC_API_KEY is not configured in Django settings."
        )

        logger.error(message)

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=message,
            model=ai_model,
        )

        raise AIGenerationError(message)

    # ----------------------------------------------------------------------
    # Import Anthropic
    # ----------------------------------------------------------------------

    try:
        import anthropic
    except ImportError as exc:
        message = (
            "The Anthropic SDK is not installed. "
            "Install the project's AI dependencies first."
        )

        logger.exception(message)

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=message,
            model=ai_model,
        )

        raise AIGenerationError(message) from exc

    # ----------------------------------------------------------------------
    # Client
    # ----------------------------------------------------------------------

    try:
        client = anthropic.Anthropic(
            api_key=api_key,
        )
    except Exception as exc:
        message = f"Failed to initialise Anthropic client: {exc}"

        logger.exception(message)

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=message,
            model=ai_model,
        )

        raise AIGenerationError(message) from exc

    # ----------------------------------------------------------------------
    # Prompt
    # ----------------------------------------------------------------------

    try:
        track_name = track.name
    except AttributeError:
        message = "Invalid track supplied to generate_lesson()."

        logger.error(message)

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=message,
            model=ai_model,
        )

        raise AIGenerationError(message)

    user_prompt = _build_user_prompt(
        topic=topic,
        track_name=track_name,
        level=level,
        duration_minutes=duration_minutes,
    )

    # ----------------------------------------------------------------------
    # Log the configuration being used
    # ----------------------------------------------------------------------

    logger.info(
        "Starting AI lesson generation: topic=%r track=%r level=%r "
        "model=%r max_tokens=%r",
        topic,
        track_name,
        level,
        ai_model,
        max_tokens,
    )

    # ----------------------------------------------------------------------
    # Anthropic request
    # ----------------------------------------------------------------------

    start = time.monotonic()

    try:
        response = client.messages.create(
            model=ai_model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            tools=[
                LESSON_TOOL_SCHEMA,
            ],
            tool_choice={
                "type": "tool",
                "name": "submit_lesson",
            },
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
        )

    except anthropic.NotFoundError as exc:
        elapsed = time.monotonic() - start

        message = (
            f"Anthropic model not found: {ai_model}. "
            "Check LESSON_AI_MODEL and make sure it contains a model "
            "currently available to your Anthropic API account."
        )

        logger.exception(
            "Anthropic model not found. topic=%r model=%r",
            topic,
            ai_model,
        )

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=f"{message} API error: {exc}",
            elapsed=elapsed,
            prompt=user_prompt,
            model=ai_model,
        )

        raise AIGenerationError(message) from exc

    except anthropic.AuthenticationError as exc:
        elapsed = time.monotonic() - start

        message = (
            "Anthropic authentication failed. "
            "Check ANTHROPIC_API_KEY."
        )

        logger.exception(
            "Anthropic authentication failed for topic=%r",
            topic,
        )

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=f"{message} API error: {exc}",
            elapsed=elapsed,
            prompt=user_prompt,
            model=ai_model,
        )

        raise AIGenerationError(message) from exc

    except anthropic.RateLimitError as exc:
        elapsed = time.monotonic() - start

        message = (
            "Anthropic rate limit reached. "
            "Please wait and try again."
        )

        logger.exception(
            "Anthropic rate limit reached for topic=%r",
            topic,
        )

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=f"{message} API error: {exc}",
            elapsed=elapsed,
            prompt=user_prompt,
            model=ai_model,
        )

        raise AIGenerationError(message) from exc

    except anthropic.APIConnectionError as exc:
        elapsed = time.monotonic() - start

        message = (
            "Could not connect to the Anthropic API."
        )

        logger.exception(
            "Anthropic connection failed for topic=%r",
            topic,
        )

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=f"{message} API error: {exc}",
            elapsed=elapsed,
            prompt=user_prompt,
            model=ai_model,
        )

        raise AIGenerationError(message) from exc

    except anthropic.APIError as exc:
        elapsed = time.monotonic() - start

        message = f"Anthropic API request failed: {exc}"

        logger.exception(
            "Anthropic API call failed for topic=%r model=%r",
            topic,
            ai_model,
        )

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=message,
            elapsed=elapsed,
            prompt=user_prompt,
            model=ai_model,
        )

        raise AIGenerationError(message) from exc

    except Exception as exc:
        elapsed = time.monotonic() - start

        message = f"Unexpected AI generation error: {exc}"

        logger.exception(
            "Unexpected AI generation error for topic=%r model=%r",
            topic,
            ai_model,
        )

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=message,
            elapsed=elapsed,
            prompt=user_prompt,
            model=ai_model,
        )

        raise AIGenerationError(message) from exc

    # ----------------------------------------------------------------------
    # Calculate duration
    # ----------------------------------------------------------------------

    elapsed = time.monotonic() - start

    # ----------------------------------------------------------------------
    # Extract tool-use response
    # ----------------------------------------------------------------------

    tool_use_block = None

    for block in getattr(response, "content", []):

        if (
            getattr(block, "type", None) == "tool_use"
            and getattr(block, "name", None) == "submit_lesson"
        ):
            tool_use_block = block
            break

    if tool_use_block is None:

        message = (
            "The AI response did not contain the required "
            "submit_lesson tool response."
        )

        logger.error(
            "%s topic=%r model=%r",
            message,
            topic,
            ai_model,
        )

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=message,
            response=response,
            elapsed=elapsed,
            prompt=user_prompt,
            model=ai_model,
        )

        raise AIGenerationError(message)

    # ----------------------------------------------------------------------
    # Validate tool output
    # ----------------------------------------------------------------------

    tool_input = getattr(
        tool_use_block,
        "input",
        None,
    )

    if not isinstance(tool_input, dict):

        message = (
            "The AI returned an invalid submit_lesson payload."
        )

        logger.error(
            "%s topic=%r",
            message,
            topic,
        )

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=message,
            response=response,
            elapsed=elapsed,
            prompt=user_prompt,
            model=ai_model,
        )

        raise AIGenerationError(message)

    try:
        lesson_data = LessonContentSchema.model_validate(
            tool_input
        )

    except ValidationError as exc:

        message = (
            f"AI output failed lesson validation: {exc}"
        )

        logger.error(
            "Lesson schema validation failed for topic=%r: %s",
            topic,
            exc,
        )

        _safe_log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=False,
            error=message,
            response=response,
            elapsed=elapsed,
            prompt=user_prompt,
            model=ai_model,
        )

        raise AIGenerationError(message) from exc

    # ----------------------------------------------------------------------
    # Successful generation
    # ----------------------------------------------------------------------

    generation_log = _safe_log_generation(
        track=track,
        topic=topic,
        level=level,
        triggered_by=triggered_by,
        ok=True,
        response=response,
        elapsed=elapsed,
        prompt=user_prompt,
        model=ai_model,
    )

    if generation_log:
        lesson_data.generation_log_id = generation_log.pk

    logger.info(
        "AI lesson generation completed successfully: "
        "topic=%r model=%r duration=%.2fs",
        topic,
        ai_model,
        elapsed,
    )

    return lesson_data


# ============================================================================
# GENERATION LOGGING
# ============================================================================

def _safe_log_generation(
    track,
    topic,
    level,
    triggered_by,
    ok,
    response=None,
    error="",
    elapsed=None,
    prompt="",
    model="",
):
    """
    Persist an AIGenerationLog record.

    Logging failures are deliberately swallowed so that a database/logging
    problem never breaks lesson generation.
    """

    try:
        return _log_generation(
            track=track,
            topic=topic,
            level=level,
            triggered_by=triggered_by,
            ok=ok,
            response=response,
            error=error,
            elapsed=elapsed,
            prompt=prompt,
            model=model,
        )

    except Exception:
        logger.exception(
            "Failed to write AIGenerationLog for topic=%r",
            topic,
        )

        return None


def _log_generation(
    track,
    topic,
    level,
    triggered_by,
    ok,
    response=None,
    error="",
    elapsed=None,
    prompt="",
    model="",
):
    """
    Create the persistent AI generation audit record.
    """

    from .models import AIGenerationLog

    usage = getattr(
        response,
        "usage",
        None,
    )

    input_tokens = getattr(
        usage,
        "input_tokens",
        0,
    ) or 0

    output_tokens = getattr(
        usage,
        "output_tokens",
        0,
    ) or 0

    response_json = {}

    if response:

        for block in getattr(
            response,
            "content",
            [],
        ):

            if getattr(
                block,
                "type",
                None,
            ) == "tool_use":

                response_json = (
                    getattr(
                        block,
                        "input",
                        {},
                    )
                    or {}
                )

                break

    return AIGenerationLog.objects.create(
        track=track,
        topic=topic,
        level=level,
        triggered_by=triggered_by,
        success=ok,
        error_message=(error or "")[:2000],
        prompt_text=prompt or "",
        response_json=response_json,
        model=model or "",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        duration_seconds=elapsed or 0,
    )
```
