"""GP800 Tool — CLI entry point."""
import click

@click.group()
@click.version_option()
def main():
    """Gilera GP800 ECU map analysis and safety validation tool."""
    pass

if __name__ == "__main__":
    main()
