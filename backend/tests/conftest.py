import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_gemini_client():
    with patch("app.rag.engine.rag_engine.client") as mock_client:
        # Mock embed_content
        mock_embedding_obj = MagicMock()
        mock_embedding_obj.embedding.values = [0.1] * 768
        mock_client.models.embed_content.return_value = mock_embedding_obj

        # Mock generate_content
        mock_response = MagicMock()
        mock_response.text = "Python is a high-level programming language."
        mock_client.models.generate_content.return_value = mock_response

        yield mock_client