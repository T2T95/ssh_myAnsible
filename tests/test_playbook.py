"""Unit tests for Playbook."""

import pytest
import tempfile
import os
from mylittleansible.playbook import Playbook, ExecutionResult


class TestPlaybook:
    """Test Playbook class."""

    def test_playbook_load_list_format(self):
        """Test loading playbook in list format."""
        yaml_content = """
- module: ping
  params: {}
- module: command
  params:
    cmd: echo "test"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                playbook = Playbook.load(f.name)
                assert len(playbook.tasks) == 2
                assert playbook.tasks[0]['module'] == 'ping'
            finally:
                os.unlink(f.name)

    def test_playbook_init_dry_run(self):
        """Test Playbook with dry_run."""
        tasks = [{'module': 'ping', 'params': {}}]
        playbook = Playbook(tasks, dry_run=True)
        assert playbook.dry_run is True

    def test_playbook_load_file_not_found(self):
        """Test loading non-existent playbook."""
        with pytest.raises(FileNotFoundError):
            Playbook.load('/nonexistent/playbook.yml')


class TestExecutionResult:
    """Test ExecutionResult class."""

    def test_execution_result_is_success_true(self):
        """Test is_success when successful."""
        result = ExecutionResult(success=True, ok=5, failed=0)
        assert result.is_success is True

    def test_execution_result_is_success_false(self):
        """Test is_success when failures exist."""
        result = ExecutionResult(success=True, ok=3, failed=2)
        assert result.is_success is False

    def test_execution_result_str(self):
        """Test string representation."""
        result = ExecutionResult(ok=3, failed=1, changed=2, skipped=0)
        result_str = str(result)
        assert "ok=3" in result_str
        assert "failed=1" in result_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
