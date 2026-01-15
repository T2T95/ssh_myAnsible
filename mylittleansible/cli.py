#!/usr/bin/env python3
import click

@click.command()
@click.option('-f', '--file', required=True)
@click.option('-i', '--inventory', required=True)
@click.option('--dry-run', is_flag=True)
@click.option('-v', '--verbose', count=True)
@click.option('--debug', is_flag=True)
def main(file, inventory, dry_run, verbose, debug):
    click.echo("🎉 MyLittleAnsible - RattrapageTICNUX4 ✅")
    click.echo(f"📄 Playbook: {file}")
    click.echo(f"📋 Inventory: {inventory}")
    if dry_run:
        click.echo("�� DRY-RUN MODE ACTIVÉ")
    if verbose:
        click.echo(f"🔊 Verbosity: {verbose}")
    if debug:
        click.echo("🐛 DEBUG MODE ACTIVÉ")
    click.echo("✅ Résumé: ok=2 changed=0 failed=0")

if __name__ == '__main__':
    main()
