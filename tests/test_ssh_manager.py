"""Unit tests for SSH Manager."""

import pytest
from mylittleansible.ssh_manager import SSHManager


class TestSSHManager:
    """Test SSHManager class initialization and properties."""

    def test_ssh_manager_init(self):
        """Test SSHManager initialization."""
        manager = SSHManager(
            hostname='192.168.1.23',
            port=22,
            username='toto',
            password='password'
        )
        
        assert manager.hostname == '192.168.1.23'
        assert manager.port == 22
        assert manager.username == 'toto'
        assert manager.password == 'password'

    def test_ssh_manager_properties(self):
        """Test SSHManager properties and attributes."""
        manager = SSHManager(
            hostname='test.example.com',
            port=2222,
            username='ubuntu',
            password='secret',
            timeout=30
        )
        
        assert manager.hostname == 'test.example.com'
        assert manager.port == 2222
        assert manager.username == 'ubuntu'
        assert manager.timeout == 30

    def test_ssh_manager_default_values(self):
        """Test SSHManager default values."""
        manager = SSHManager(hostname='localhost')
        
        assert manager.hostname == 'localhost'
        assert manager.port == 22
        assert manager.username is None
        assert manager.password is None
        assert manager.timeout == 10

    def test_ssh_manager_key_file(self):
        """Test SSHManager with key file."""
        manager = SSHManager(
            hostname='host.com',
            key_file='/home/user/.ssh/id_rsa'
        )
        
        assert manager.key_file == '/home/user/.ssh/id_rsa'

    def test_ssh_manager_client_attribute(self):
        """Test SSHManager client attribute."""
        manager = SSHManager(hostname='test')
        
        # Client should be None initially (not connected yet)
        assert manager.client is None

    def test_ssh_manager_custom_timeout(self):
        """Test SSHManager with custom timeout."""
        manager = SSHManager(hostname='test', timeout=60)
        assert manager.timeout == 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
