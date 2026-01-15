"""Ping module for MyLittleAnsible - SSH connection test."""

from typing import Any, Dict
from mylittleansible.modules.base import BaseModule
from mylittleansible.utils import CmdResult
from paramiko import SSHClient


class PingModule(BaseModule):
    """Module for testing SSH connectivity (ping)."""

    name: str = "ping"

    def __init__(
        self,
        params: Dict[str, Any],
        dry_run: bool = False,
        changed_threshold: bool = False,
    ) -> None:
        super().__init__(params, dry_run, changed_threshold)

    def process(self, ssh_client: SSHClient) -> CmdResult:
        try:
            stdin, stdout, stderr = ssh_client.exec_command("echo 'pong'")
            exit_code = stdout.channel.recv_exit_status()
            output = stdout.read().decode("utf-8").strip()

            if exit_code == 0 and output == "pong":
                return CmdResult(
                    stdout="pong",
                    stderr="",
                    exit_code=0,
                    changed=False,
                )
            else:
                return CmdResult(
                    stdout="",
                    stderr=f"Ping failed: exit_code={exit_code}",
                    exit_code=1,
                    changed=False,
                )

        except Exception as e:
            return CmdResult(
                stdout="",
                stderr=f"Ping error: {str(e)}",
                exit_code=1,
                changed=False,
            )
