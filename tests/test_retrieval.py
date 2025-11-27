from app.agents.retrieval import RetrievalAgent


class DummyMem:
    def search(self, query, top_n=5):
        return [{"title": "doc1", "content": "example"}]


def test_retrieval_returns_list():
    r = RetrievalAgent(memory_system=DummyMem())
    res = r.retrieve("anything")
    assert isinstance(res, list)
    assert res and "title" in res[0]
