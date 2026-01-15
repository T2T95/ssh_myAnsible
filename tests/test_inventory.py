"""Unit tests for Inventory."""

import pytest
import tempfile
import os
from mylittleansible.inventory import Inventory


class TestInventory:
    """Test Inventory class."""

    def test_inventory_load_valid_yaml(self):
        """Test loading valid inventory YAML."""
        yaml_content = """
ubuntu24:
  ssh_address: 192.168.1.23
  ssh_port: 22
  ssh_user: toto
  ssh_password: password
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                inventory = Inventory.load(f.name)
                assert 'ubuntu24' in inventory.hosts
                assert inventory.hosts['ubuntu24']['ssh_address'] == '192.168.1.23'
            finally:
                os.unlink(f.name)

    def test_inventory_multiple_hosts(self):
        """Test loading inventory with multiple hosts."""
        yaml_content = """
web01:
  ssh_address: 192.168.1.10
web02:
  ssh_address: 192.168.1.11
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            try:
                inventory = Inventory.load(f.name)
                assert len(inventory.hosts) == 2
                assert 'web01' in inventory.hosts
                assert 'web02' in inventory.hosts
            finally:
                os.unlink(f.name)

    def test_inventory_load_file_not_found(self):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            Inventory.load('/nonexistent/inventory.yml')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
