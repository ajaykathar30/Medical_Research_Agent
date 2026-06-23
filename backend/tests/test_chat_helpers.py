from langchain_core.messages import AIMessageChunk

from router.chat import _chunk_text


def test_chunk_text_extracts_plain_string_content():
    chunk = AIMessageChunk(content="hello")
    assert _chunk_text(chunk) == "hello"


def test_chunk_text_extracts_text_blocks_from_list_content():
    chunk = AIMessageChunk(content=[{"type": "text", "text": "hello "}, {"type": "text", "text": "world"}])
    assert _chunk_text(chunk) == "hello world"


def test_chunk_text_ignores_non_text_blocks():
    chunk = AIMessageChunk(content=[{"type": "image", "data": "..."}])
    assert _chunk_text(chunk) == ""


def test_chunk_text_returns_empty_for_unexpected_content_type():
    class FakeChunk:
        content = 123

    assert _chunk_text(FakeChunk()) == ""
