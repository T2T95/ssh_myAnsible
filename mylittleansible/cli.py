#!/usr/bin/env python3
"""
CLI module for MyLittleAnsible.
Handles command-line interface and playbook execution.
"""

import click
from mylittleansible.playbook import Playbook
from mylittleansible.inventory import Inventory
from mylittleansible.utils import get_logger

logger = get_logger("mla")


@click.command()
@click.option('-f', '--file', required=True, help='Path to playbook YAML file')
@click.option('-i', '--inventory', required=True, help='Path to inventory YAML file')
@click.option('--dry-run', is_flag=True, help='Run in dry-run mode (no changes)')
@click.option('-v', '--verbose', count=True, help='Increase verbosity (-v, -vv, -vvv)')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def main(file, inventory, dry_run, verbose, debug):
    """MyLittleAnsible - Simple Ansible-like automation tool."""
    
    # Display header
    click.echo("🎉 MyLittleAnsible - RattrapageTICNUX4 ✅")
    click.echo(f"📄 Playbook: {file}")
    click.echo(f"📋 Inventory: {inventory}")
    
    if dry_run:
        click.echo("🔄 DRY-RUN MODE ACTIVÉ")
    
    if verbose:
        click.echo(f"🔊 Verbosity: {verbose}")
    
    if debug:
        click.echo("🐛 DEBUG MODE ACTIVÉ")
    
    try:
        # Load playbook and inventory
        playbook = Playbook.load(file, dry_run=dry_run)
        inventory_obj = Inventory.load(inventory)
        
        # Execute playbook
        result = playbook.execute(inventory_obj)
        
        # Display summary with actual results
        click.echo(f"✅ Résumé: {result}")
        
        # Return appropriate exit code
        if result.is_success:
            exit(0)
        else:
            exit(1)
        
    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if debug:
            import traceback
            traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()
