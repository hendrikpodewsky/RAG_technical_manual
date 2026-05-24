from wissenssystem.config import Settings


def test_default_urls():
    s = Settings(_env_file=None)
    assert s.ollama_url == "http://localhost:11434"
    assert s.qdrant_url == "http://localhost:6333"
    assert s.qdrant_api_key is None


def test_default_models():
    s = Settings(_env_file=None)
    assert s.llm_model == "qwen2.5:3b"
    assert s.vision_model == "moondream"
    assert s.embedding_model == "paraphrase-multilingual-MiniLM-L12-v2"


def test_default_thresholds():
    s = Settings(_env_file=None)
    assert s.intent_confidence_threshold == 0.7
    assert s.machine_resolution_threshold == 0.75
    assert s.retrieval_top_k == 10


def test_default_paths():
    s = Settings(_env_file=None)
    assert str(s.data_dir) == "data"
    assert str(s.sources_dir) == "data/sources"
    assert str(s.blobs_dir) == "data/blobs"
    assert str(s.registry_db_path) == "data/registry.db"


def test_env_override_url(monkeypatch):
    monkeypatch.setenv("QDRANT_URL", "http://remote-qdrant:6333")
    s = Settings(_env_file=None)
    assert s.qdrant_url == "http://remote-qdrant:6333"


def test_env_override_top_k(monkeypatch):
    monkeypatch.setenv("RETRIEVAL_TOP_K", "20")
    s = Settings(_env_file=None)
    assert s.retrieval_top_k == 20


def test_env_override_model(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "llama3.2:3b")
    s = Settings(_env_file=None)
    assert s.llm_model == "llama3.2:3b"
