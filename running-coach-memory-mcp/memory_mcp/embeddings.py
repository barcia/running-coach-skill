"""OpenRouter client for embeddings."""

from openai import OpenAI, APIError, APIConnectionError, RateLimitError

from memory_mcp.config import Settings
from memory_mcp.logging import logger


def get_embedding_client(settings: Settings) -> OpenAI:
    """Get OpenAI client configured for OpenRouter."""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )


def create_embedding(client: OpenAI, text: str, model: str) -> list[float]:
    """Create embedding for text using OpenRouter.

    Args:
        client: OpenAI client configured for OpenRouter
        text: Text to create embedding for
        model: Model identifier to use

    Returns:
        List of floats representing the embedding vector

    Raises:
        EmbeddingError: If embedding creation fails
    """
    try:
        logger.debug("Creating embedding for text (length=%d) with model=%s", len(text), model)
        response = client.embeddings.create(
            model=model,
            input=text,
        )
        logger.debug("Embedding created successfully, dimensions=%d", len(response.data[0].embedding))
        return response.data[0].embedding

    except RateLimitError as e:
        logger.error("Rate limit exceeded for OpenRouter API: %s", e)
        raise EmbeddingError(f"Rate limit exceeded. Please try again later. Details: {e}") from e

    except APIConnectionError as e:
        logger.error("Connection error to OpenRouter API: %s", e)
        raise EmbeddingError(f"Failed to connect to OpenRouter API. Check your network connection. Details: {e}") from e

    except APIError as e:
        logger.error("OpenRouter API error (status=%s): %s", getattr(e, 'status_code', 'unknown'), e)
        raise EmbeddingError(f"OpenRouter API error: {e}") from e

    except Exception as e:
        logger.exception("Unexpected error creating embedding: %s", e)
        raise EmbeddingError(f"Unexpected error creating embedding: {e}") from e


class EmbeddingError(Exception):
    """Custom exception for embedding-related errors."""

    pass
