"""
Playbook module for MyLittleAnsible.
Handles playbook loading and execution.
"""

import os
import yaml
from mylittleansible.inventory import Inventory
from typing import Any, Dict, List
from mylittleansible.utils import get_logger
from mylittleansible.ssh_manager import SSHManager

logger = get_logger("mla")


class ExecutionResult:
    """Result of playbook execution."""

    def __init__(self, success: bool = True, ok: int = 0, failed: int = 0,
                 changed: int = 0, skipped: int = 0):
        self.success = success
        self.ok = ok
        self.failed = failed
        self.changed = changed
        self.skipped = skipped

    @property
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.success and self.failed == 0

    def __str__(self) -> str:
        return (
            f"ok={self.ok} failed={self.failed} "
            f"changed={self.changed} skipped={self.skipped}"
        )


class Playbook:
    """Playbook class for managing tasks."""

    def __init__(self, tasks: List[Dict[str, Any]], dry_run: bool = False):
        """
        Initialize playbook.

        Args:
            tasks: List of task dictionaries
            dry_run: Whether to run in dry-run mode
        """
        self.tasks = tasks
        self.dry_run = dry_run

    @staticmethod
    def load(playbook_file: str, dry_run: bool = False) -> "Playbook":
        """
        Load playbook from YAML file.

        Args:
            playbook_file: Path to the playbook YAML file
            dry_run: Whether to run in dry-run mode

        Returns:
            Playbook instance

        Raises:
            FileNotFoundError: If playbook file not found
            yaml.YAMLError: If YAML parsing fails
        """
        if not os.path.exists(playbook_file):
            raise FileNotFoundError(
                f"Playbook file not found: {playbook_file}")

        logger.info(f"Loading playbook from {playbook_file}")

        with open(playbook_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data:
            raise ValueError("Playbook file is empty")

        # Handle both list and dict formats
        if isinstance(data, list):
            tasks = data
        elif isinstance(data, dict) and 'tasks' in data:
            tasks = data['tasks']
        else:
            tasks = [data]

        logger.info(f"Loaded {len(tasks)} task(s) from playbook")

        return Playbook(tasks, dry_run=dry_run)

    def execute(self, inventory: "Inventory") -> ExecutionResult:
        """
        Execute playbook on all hosts in inventory.

        Args:
            inventory: Inventory instance with hosts

        Returns:
            ExecutionResult with execution statistics
        """
        result = ExecutionResult()

        # ✅ DRY-RUN MODE: Simulate execution without SSH connection
        if self.dry_run:
            logger.warning("Running in DRY-RUN mode - no changes will be made")
            logger.info("=" * 60)

            # ✅ CORRECTION: inventory.hosts est un DICT, pas une list!
            for host_key, host_data in inventory.hosts.items():
                logger.info(f"Executing tasks on host: {host_key}")
                logger.info("=" * 60)

                for task in self.tasks:
                    module = task.get('module', 'unknown')
                    params = task.get('params', {})
                    logger.info(f"[DRY-RUN] Module: {module}")
                    logger.info(f"[DRY-RUN] Params: {params}")
                    result.ok += 1

                logger.info("=" * 60)

            logger.info(f"Playbook Summary: {result}")
            logger.info("=" * 60)
            return result

        # ✅ REAL EXECUTION: Connect to hosts and execute tasks
        logger.info("=" * 60)

        for host_key, host_data in inventory.hosts.items():
            logger.info(f"Executing tasks on host: {host_key}")
            logger.info("=" * 60)

            try:
                # ✅ FIX: Changed host_address to hostname (correct parameter name)
                ssh_manager = SSHManager(
                    hostname=host_data.get('ssh_address', 'localhost'),
                    port=host_data.get('ssh_port', 22),
                    username=host_data.get('ssh_user', 'root'),
                    password=host_data.get('ssh_password', '')
                )

                logger.info(f"Connecting to {host_key}...")
                ssh_manager.connect()
                logger.info(f"Connected to {host_key}")

                # Execute each task
                for task in self.tasks:
                    try:
                        module = task.get('module', 'unknown')
                        params = task.get('params', {})

                        logger.info(f"[{module}] Executing task...")
                        logger.debug(f"[{module}] Params: {params}")

                        # Execute the task based on module type
                        task_result = self._execute_task(
                            ssh_manager, module, params)

                        if task_result:
                            result.ok += 1
                            # ✅ FIX: Only count as 'changed' for modules that modify the system
                            if module in ["apt", "service", "copy", "template", "sysctl"]:
                                result.changed += 1
                                logger.info(f"[{module}] OK [CHANGED]")
                            else:
                                logger.info(f"[{module}] OK")
                        else:
                            result.failed += 1
                            logger.error(f"[{module}] FAILED")

                    except Exception as e:
                        result.failed += 1
                        logger.error(f"Error executing task: {str(e)}")

                # Disconnect
                ssh_manager.close()

            except Exception as e:
                result.failed += 1
                logger.error(f"Error on host {host_key}: {str(e)}")

        logger.info("=" * 60)
        logger.info(f"Playbook Summary: {result}")
        logger.info("=" * 60)

        return result

    def _execute_task(self, ssh_manager: SSHManager, module: str,
                      params: Dict[str, Any]) -> bool:
        """
        Execute a single task on a host.

        Args:
            ssh_manager: SSHManager instance for the host
            module: Module name (apt, command, copy, template, service, sysctl, ping)
            params: Module parameters

        Returns:
            True if successful, False otherwise
        """
        try:
            if module == "ping":
                return self._execute_ping(ssh_manager)

            elif module == "apt":
                return self._execute_apt(ssh_manager, params)

            elif module == "command":
                return self._execute_command(ssh_manager, params)

            elif module == "copy":
                return self._execute_copy(ssh_manager, params)

            elif module == "template":
                return self._execute_template(ssh_manager, params)

            elif module == "service":
                return self._execute_service(ssh_manager, params)

            elif module == "sysctl":
                return self._execute_sysctl(ssh_manager, params)

            else:
                logger.warning(f"Unknown module: {module}")
                return False

        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            return False

    def _execute_ping(self, ssh_manager: SSHManager) -> bool:
        """Execute ping module (SSH connectivity test)."""
        from mylittleansible.modules.ping import PingModule

        try:
            ping_module = PingModule(params={})
            result = ping_module.execute(ssh_manager.client)

            if result.is_success:
                logger.info("Ping successful: pong")
                return True
            else:
                logger.error(f"Ping failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Ping error: {str(e)}")
            return False

    def _execute_apt(self, ssh_manager: SSHManager,
                     params: Dict[str, Any]) -> bool:
        """Execute apt module (package management)."""
        name = params.get('name')
        state = params.get('state', 'present')

        if not name:
            logger.error("apt module requires 'name' parameter")
            return False

        if state == 'present':
            cmd = f"sudo apt-get install -y {name}"
        elif state == 'absent':
            cmd = f"sudo apt-get remove -y {name}"
        else:
            logger.error(f"Unknown state: {state}")
            return False

        stdin, stdout, stderr = ssh_manager.exec_command(cmd)
        exit_code = stdout.channel.recv_exit_status()
        stderr_text = stderr.read().decode("utf-8")

        if exit_code != 0 and "E:" in stderr_text:
            logger.error(f"apt error: {stderr_text}")
            return False

        logger.info(f"Package '{name}' state set to '{state}'")
        return True

    def _execute_command(self, ssh_manager: SSHManager,
                         params: Dict[str, Any]) -> bool:
        """Execute command module (raw command execution)."""
        command = params.get('cmd') or params.get('command')

        if not command:
            logger.error("command module requires 'cmd' parameter")
            return False

        logger.info(f"Executing command: {command}")
        stdin, stdout, stderr = ssh_manager.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        stdout_text = stdout.read().decode("utf-8")
        stderr_text = stderr.read().decode("utf-8")

        if stdout_text:
            logger.debug(f"stdout: {stdout_text}")
        if stderr_text:
            logger.debug(f"stderr: {stderr_text}")

        return exit_code == 0

    def _execute_copy(self, ssh_manager: SSHManager,
                      params: Dict[str, Any]) -> bool:
        """Execute copy module (file transfer)."""
        src = params.get('src')
        dest = params.get('dest')

        if not src or not dest:
            logger.error("copy module requires 'src' and 'dest' parameters")
            return False

        if not os.path.exists(src):
            logger.error(f"Source file not found: {src}")
            return False

        logger.info(f"Copying {src} to {dest}")

        try:
            sftp = ssh_manager.open_sftp()
            sftp.put(src, dest)
            sftp.close()
            logger.info(f"File copied successfully to {dest}")
            return True
        except Exception as e:
            logger.error(f"Copy failed: {str(e)}")
            return False

    def _execute_template(self, ssh_manager: SSHManager,
                          params: Dict[str, Any]) -> bool:
        """Execute template module (Jinja2 template rendering)."""
        from jinja2 import Template

        src = params.get('src')
        dest = params.get('dest')

        if not src or not dest:
            logger.error(
                "template module requires 'src' and 'dest' parameters")
            return False

        if not os.path.exists(src):
            logger.error(f"Template file not found: {src}")
            return False

        # Extract template variables (all params except src/dest)
        template_vars = {k: v for k, v in params.items() if k not in [
            'src', 'dest']}

        logger.info(
            f"Rendering template {src} with variables: {template_vars}")

        try:
            with open(src, 'r', encoding='utf-8') as f:
                template_content = f.read()

            template = Template(template_content)
            rendered = template.render(template_vars)

            # Write rendered content to remote file
            stdin, stdout, stderr = ssh_manager.exec_command(
                f"cat > {dest} << 'TEMPLATE_EOF'\n{rendered}\nTEMPLATE_EOF"
            )
            exit_code = stdout.channel.recv_exit_status()

            return exit_code == 0
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            return False

    def _execute_service(self, ssh_manager: SSHManager,
                         params: Dict[str, Any]) -> bool:
        """Execute service module (service management)."""
        name = params.get('name')
        state = params.get('state', 'started')

        if not name:
            logger.error("service module requires 'name' parameter")
            return False

        if state == 'started':
            cmd = f"sudo systemctl start {name}"
        elif state == 'stopped':
            cmd = f"sudo systemctl stop {name}"
        elif state == 'restarted':
            cmd = f"sudo systemctl restart {name}"
        elif state == 'enabled':
            cmd = f"sudo systemctl enable {name}"
        elif state == 'disabled':
            cmd = f"sudo systemctl disable {name}"
        else:
            logger.error(f"Unknown service state: {state}")
            return False

        stdin, stdout, stderr = ssh_manager.exec_command(cmd)
        exit_code = stdout.channel.recv_exit_status()
        stderr_text = stderr.read().decode("utf-8")

        if exit_code != 0 and "Error" in stderr_text:
            logger.error(f"service error: {stderr_text}")
            return False

        logger.info(f"Service '{name}' state set to '{state}'")
        return True

    def _execute_sysctl(self, ssh_manager: SSHManager,
                        params: Dict[str, Any]) -> bool:
        """Execute sysctl module (system kernel parameters)."""
        attribute = params.get('attribute')
        value = params.get('value')
        permanent = params.get('permanent', False)

        if not attribute or value is None:
            logger.error(
                "sysctl module requires 'attribute' and 'value' parameters")
            return False

        # Set the parameter temporarily
        cmd = f"sudo sysctl -w {attribute}={value}"
        stdin, stdout, stderr = ssh_manager.exec_command(cmd)
        exit_code = stdout.channel.recv_exit_status()
        stderr_text = stderr.read().decode("utf-8")

        if exit_code != 0 and "Error" in stderr_text:
            logger.error(f"sysctl error: {stderr_text}")
            return False

        # Persist if requested
        if permanent:
            persist_cmd = f"echo '{attribute}={value}' | sudo tee -a /etc/sysctl.conf"
            ssh_manager.exec_command(persist_cmd)
            logger.info(f"Persisted {attribute}={value} to /etc/sysctl.conf")

        logger.info(f"Set {attribute}={value}")
        return True
