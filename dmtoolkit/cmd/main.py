from pathlib import Path

import click

import dmtoolkit.cmd.classes as cmd_c
import dmtoolkit.cmd.items as cmd_i
import dmtoolkit.cmd.get_monsters as cmd_m
import dmtoolkit.cmd.spells as cmd_sp
import dmtoolkit.cmd.races as cmd_r
import dmtoolkit.cmd.kcg_gathering as cmd_kcg_g

@click.group
def main():
    pass


@main.group
def monsters():
    pass


@monsters.command("convert")
@click.option("--infile", "-i", default=cmd_m.DEFAULT_RAW, type=click.Path(exists=True, path_type=Path))
@click.option("--outfile", "-o", default=cmd_m.DEFAULT_CONV, type=click.Path(writable=True, path_type=Path))
def convert_monsters(infile: Path, outfile: Path):
    cmd_m.convert(infile, outfile)


@monsters.command("test")
@click.option("--infile", "-i", default=cmd_m.DEFAULT_CONV, type=click.Path(exists=True, path_type=Path))
def test_monsters(infile: Path):
    cmd_m.test(infile)


@main.group()
def races():
    pass


@races.command("convert")
@click.option("--infile", "-i", default=cmd_r.DEFAULT_RAW, type=click.Path(exists=True, path_type=Path))
@click.option("--outfile", "-o", default=cmd_r.DEFAULT_CONV, type=click.Path(writable=True, path_type=Path))
def convert_races(infile: Path, outfile: Path):
    cmd_r.convert(infile, outfile)


@races.command
def test():
    pass

@main.group()
def classes():
    pass

@classes.command("fetch")
@click.option("--outfile", "-o", default=cmd_c.DEFAULT_RAW, type=click.Path(writable=True, path_type=Path))
def fetch_classes(outfile):
    cmd_c.fetch_classes(outfile)

@classes.command("convert")
@click.option("--infile", "-i", default=cmd_c.DEFAULT_RAW, type=click.Path(exists=True, path_type=Path))
@click.option("--outfile", "-o", default=cmd_c.DEFAULT_CONV, type=click.Path(writable=True, path_type=Path))
def convert_classes(infile: Path, outfile: Path):
    cmd_c.convert(infile, outfile)

@main.group()
def spells():
    pass

@spells.command("fetch")
@click.option("--outfile", "-o", default=cmd_sp.DEFAULT_RAW, type=click.Path(writable=True, path_type=Path))
def fetch_spells(outfile):
    cmd_sp.fetch_spells(outfile)

@spells.command("convert")
@click.option("--infile", "-i", default=cmd_sp.DEFAULT_RAW, type=click.Path(exists=True, path_type=Path))
@click.option("--outfile", "-o", default=cmd_sp.DEFAULT_CONV, type=click.Path(writable=True, path_type=Path))
def convert_spells(infile: Path, outfile: Path):
    cmd_sp.convert(infile, outfile)

@main.group()
def items():
    pass

@items.command("fetch")
@click.option("--outfile", "-o", default=cmd_i.DEFAULT_RAW, type=click.Path(writable=True, path_type=Path))
def fetch_items(outfile):
    cmd_i.fetch_items(outfile)

@items.command("convert")
@click.option("--infile", "-i", default=cmd_i.DEFAULT_RAW, type=click.Path(exists=True, path_type=Path))
@click.option("--outfile", "-o", default=cmd_i.DEFAULT_CONV, type=click.Path(writable=True, path_type=Path))
def convert_items(infile: Path, outfile: Path):
    cmd_i.convert(infile, outfile)

@main.group()
def kcg_gathering():
    pass

@kcg_gathering.command("convert")
def kcg_gathering_convert():
    cmd_kcg_g.convert()