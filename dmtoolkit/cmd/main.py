from pathlib import Path

import click

import dmtoolkit.cmd.classes as cmd_c
import dmtoolkit.cmd.get_monsters as cmd_m
import dmtoolkit.cmd.spells as cmd_sp
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

@main.group()
def classes():
    pass

@classes.command
@click.option("--outfile", "-o", default=cmd_c.DEFAULT_RAW, type=click.Path(writable=True, path_type=Path))
def fetch(outfile):
    cmd_c.fetch_classes(outfile)

@classes.command
@click.option("--infile", "-i", default=cmd_c.DEFAULT_RAW, type=click.Path(exists=True, path_type=Path))
@click.option("--outfile", "-o", default=cmd_c.DEFAULT_CONV, type=click.Path(writable=True, path_type=Path))
def convert(infile: Path, outfile: Path):
    cmd_c.convert(infile, outfile)

@main.group()
def spells():
    pass

@spells.command
@click.option("--outfile", "-o", default=cmd_sp.DEFAULT_RAW, type=click.Path(writable=True, path_type=Path))
def fetch(outfile):
    cmd_sp.fetch_spells(outfile)

@spells.command
@click.option("--infile", "-i", default=cmd_sp.DEFAULT_RAW, type=click.Path(exists=True, path_type=Path))
@click.option("--outfile", "-o", default=cmd_sp.DEFAULT_CONV, type=click.Path(writable=True, path_type=Path))
def convert(infile: Path, outfile: Path):
    cmd_sp.convert(infile, outfile)