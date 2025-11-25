import random
import string

default_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits


def generate_str(size: int = 6, chars: str = default_chars) -> str:
    """Generate a random string of specified size."""
    return "".join(random.choice(chars) for _ in range(size))


def mask_string(
    text: str,
    *,
    mask_char: str = "*",
    keep_start: int = 0,
    keep_end: int = 0,
    keep_prefix: str = "",
    keep_suffix: str = "",
    preserve_chars: str = "",
    min_length: int = 0,
) -> str:
    """
    Generic string masking function.

    Args:
        text: String to mask
        mask_char: Character to use for masking (default: "*")
        keep_start: Number of characters to keep at start
        keep_end: Number of characters to keep at end
        keep_prefix: Prefix to always keep (e.g., "sk_", "Bearer ")
        keep_suffix: Suffix to always keep (e.g., domain for emails)
        preserve_chars: Characters to not mask (e.g., "@", "-", " ")
        min_length: Minimum length to apply masking (return original if shorter)

    Returns:
        Masked string

    Examples:
        # Email
        mask_string("john@example.com", keep_start=1, keep_end=1, preserve_chars="@.")
        # Output: j***@e*****.com

        # Phone
        mask_string("+1-555-123-4567", keep_end=4, preserve_chars="+- ")
        # Output: +*-***-***-4567

        # Token
        mask_string("sk_live_abc123xyz", keep_prefix="sk_", keep_start=2, keep_end=2)
        # Output: sk_ab********yz

        # Credit card
        mask_string("4532 1234 5678 9010", keep_end=4, preserve_chars=" ")
        # Output: **** **** **** 9010

        # Password (full mask)
        mask_string("MyPassword123")
        # Output: *************

        # API Key
        mask_string("eyJhbGciOiJIUzI1NiIs", keep_start=4, keep_end=4)
        # Output: eyJh**********Is
    """
    if not text or len(text) < min_length:
        return text

    result = text

    # Handle prefix
    if keep_prefix and result.startswith(keep_prefix):
        prefix = keep_prefix
        result = result[len(keep_prefix) :]
    else:
        prefix = ""

    # Handle suffix
    if keep_suffix and result.endswith(keep_suffix):
        suffix = keep_suffix
        result = result[: -len(keep_suffix)]
    else:
        suffix = ""

    # Calculate positions
    length = len(result)

    if length <= keep_start + keep_end:
        # String too short, mask everything except preserved chars
        if preserve_chars:
            masked = "".join(c if c in preserve_chars else mask_char for c in result)
        else:
            masked = mask_char * length
    else:
        # Build masked string
        start_part = result[:keep_start]
        end_part = result[-keep_end:] if keep_end > 0 else ""
        middle_part = result[keep_start : len(result) - keep_end if keep_end > 0 else len(result)]

        # Mask middle part
        if preserve_chars:
            masked_middle = "".join(c if c in preserve_chars else mask_char for c in middle_part)
        else:
            masked_middle = mask_char * len(middle_part)

        masked = start_part + masked_middle + end_part

    return prefix + masked + suffix
