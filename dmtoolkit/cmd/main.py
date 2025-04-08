from pathlib import Path

import click

import dmtoolkit.cmd.get_monsters as cmd_m
import dmtoolkit.cmd.races as cmd_r

@click.group
def main():
    pass


@main.group
def monsters():
    pass


@monsters.command("convert")
@click.option("--infile", "-i", default=cmd_m.DEFAULT_RAW, type=click.Path(exists=True, path_type=Path))
@click.option("--outfile", "-o", default=cmd_m.DEFAULT_CONV, type=click.Path(writable=True, path_type=Path))
def convert(infile: Path, outfile: Path):
    cmd_m.convert(infile, outfile)


@monsters.command("test")
@click.option("--infile", "-i", default=cmd_m.DEFAULT_CONV, type=click.Path(exists=True, path_type=Path))
def test(infile: Path):
    cmd_m.test(infile)


@main.group()
def races():
    pass


@races.command
@click.option("--infile", "-i", default=cmd_r.DEFAULT_RAW, type=click.Path(exists=True, path_type=Path))
@click.option("--outfile", "-o", default=cmd_r.DEFAULT_CONV, type=click.Path(writable=True, path_type=Path))
def convert(infile: Path, outfile: Path):
    cmd_r.convert(infile, outfile)


@races.command
def test():
    pass