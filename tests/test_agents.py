"""Tests for agent name generation."""

from uzi import agents


class TestAgentNames:
    """Test agent name generation functionality."""

    def test_agent_names_list_exists(self):
        """Test that AGENT_NAMES list is populated."""
        assert len(agents.AGENT_NAMES) > 0

    def test_agent_names_are_unique(self):
        """Test that all agent names are unique (no duplicates)."""
        assert len(agents.AGENT_NAMES) == len(set(agents.AGENT_NAMES))

    def test_agent_names_count(self):
        """Test that we have expected number of agent names."""
        assert len(agents.AGENT_NAMES) == 104

    def test_get_random_agent_returns_string(self):
        """Test that get_random_agent returns a string."""
        name = agents.get_random_agent()
        assert isinstance(name, str)

    def test_get_random_agent_returns_valid_name(self):
        """Test that get_random_agent returns a name from the list."""
        name = agents.get_random_agent()
        assert name in agents.AGENT_NAMES

    def test_get_random_agent_multiple_calls(self):
        """Test that get_random_agent can be called multiple times."""
        names = [agents.get_random_agent() for _ in range(10)]
        assert len(names) == 10
        assert all(isinstance(name, str) for name in names)
        assert all(name in agents.AGENT_NAMES for name in names)

    def test_agent_names_are_lowercase(self):
        """Test that all agent names are lowercase."""
        assert all(name.islower() for name in agents.AGENT_NAMES)

    def test_agent_names_are_alphabetic(self):
        """Test that all agent names contain only alphabetic characters."""
        assert all(name.isalpha() for name in agents.AGENT_NAMES)

    def test_specific_agent_names_exist(self):
        """Test that specific expected names exist in the list."""
        expected_names = ["john", "emily", "michael", "sarah", "david"]
        for name in expected_names:
            assert name in agents.AGENT_NAMES
