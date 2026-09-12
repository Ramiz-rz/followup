from app.services.fallback_analyzer import analyze_fallback


def test_extracts_first_person_commitment():
    text = "Developer: I'll send the proposal tomorrow."
    result = analyze_fallback(text)
    assert len(result["commitments"]) == 1
    c = result["commitments"][0]
    assert c["person"] == "Developer"
    assert c["due_date_text"] == "tomorrow"
    assert c["confidence"] > 0.5


def test_extracts_waiting_item():
    text = "Project Manager: We are still waiting for the client to approve the design."
    result = analyze_fallback(text)
    assert len(result["waiting_items"]) == 1
    w = result["waiting_items"][0]
    assert "waiting" in w["item"].lower()


def test_does_not_commit_on_hedged_opinion():
    text = "Client: I think we should update the onboarding copy at some point."
    result = analyze_fallback(text)
    assert len(result["commitments"]) == 0


def test_no_items_in_plain_text():
    text = "Client: The weather has been nice lately."
    result = analyze_fallback(text)
    assert len(result["commitments"]) == 0
    assert len(result["waiting_items"]) == 0
