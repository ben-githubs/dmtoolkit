import string
import re
from urllib.parse import quote
from flask import url_for
from dmtoolkit.api import items
import importlib.metadata

def sanitize_names(name: str) -> str:
    """Sanitize the names for use in a javascript string."""
    return name.replace("'", r"\'").replace('"', r"\"")

class Macro5e:
    damage = re.compile(r"{@damage (.*?)}")
    atk = re.compile(r"{@atk (.*?)}")
    hit = re.compile(r"{@hit (.*?)}")
    on_hit = re.compile(r"{@h}")
    condition = re.compile(r"\{@condition (\w+)\}")
    dc = re.compile(r"\{@dc (\d+)\}")
    spell = re.compile(r"\{@spell (.*?)\}")
    dice = re.compile(r"\{@dice (\d+)?d(\d+)\}")
    status = re.compile(r"\{@status (\w+)(?:\s*\|\|\s*(\w+))?}")
    skill = re.compile(r"{@skill (.*?)}")
    italics = re.compile(r"{@i (.*?)}")
    item = re.compile(r"\{@item (.*?)\}")

    @staticmethod
    def render_macros(text: str) -> str:
        """Turns the 5etools macros (like {@spell magic missile}) into the appropriate HTML elements."""
        text = str(text) # Just in case
        text = Macro5e.damage.sub(r"\1", text)
        text = Macro5e.atk.sub(Macro5e.render_atk, text)
        text = Macro5e.hit.sub(Macro5e.render_hit, text)
        text = Macro5e.on_hit.sub("<em>Hit:</em> ", text)
        text = Macro5e.condition.sub(Macro5e.render_condition, text)
        text = Macro5e.dc.sub(r"DC \1", text)
        text = Macro5e.spell.sub(Macro5e.render_spell, text)
        text = Macro5e.dice.sub(Macro5e.render_dice, text)
        text = Macro5e.status.sub(Macro5e.render_status, text)
        text = Macro5e.skill.sub(Macro5e.render_skill, text)
        text = Macro5e.italics.sub(r"<em>\1</em>", text)
        text = Macro5e.item.sub(Macro5e.render_item, text)

        return text

    @staticmethod
    def render_atk(match: re.Match) -> str:
        atk_type = match.group(1)
        atk_str = {
            "mw": "Melee Weapon Attack",
            "rw": "Ranged Weapon Attack",
            "mw,rw": "Melee or Ranged Weapon Attack",
        }.get(atk_type, "Attack")
        return f"<em>{atk_str}:</em>"

    @staticmethod
    def render_condition(match: re.Match) -> str:
        """Return a link to the appripriate entry in Roll20."""
        condition = match.group(1)
        # Roll20 doesn't have named headers, they're enumerated. It sucks.
        headers = [
            "blinded",
            "charmed",
            "deafened",
            "frightened",
            "grappled",
            "incapacitated",
            "invisible",
            "paralyzed",
            "petrified",
            "poisoned",
            "prone",
            "restrained",
            "stunned",
            "unconscious",
            "exhaustion"
        ]
        index = headers.index(condition.casefold()) + 1
        url = f"https://roll20.net/compendium/dnd5e/Conditions#toc_{index}"
        return f"""<a href="{url}">{condition}</a>"""

    @staticmethod
    def render_dice(match: re.Match) -> str:
        groups = match.groups(default="1")
        return "d".join(groups)

    @staticmethod
    def render_hit(match: re.Match) -> str:
        hit_mod = match.group(1)
        return f"{int(hit_mod):+d}"
    
    @staticmethod
    def render_item(match: re.Match) -> str:
        item_id = match.group(1)
        url = f"https://roll20.net/compendium/dnd5e/{quote(item_id, safe='')}"

        item_url = url_for("tracker_bp.get_item_tooltip", item_name=item_id)
        item_url = sanitize_names(item_url)
        func = f"showNewTooltip(event, '{item_url}')"
        item = items.get_item(item_id)

        # If we can't find an item, just print the item name.
        if not item:
            return match.group(1).split("|")[0]

        item_string = item.name if len(item_id.split("|")) < 3 else item_id.split("|")[2]
        
        return f"""<span class="tooltip" onmouseenter="{func}" onmouseleave="hideTooltip(event)"><a href="{url}">{item_string}</a></span>"""

    @staticmethod
    def render_skill(match: re.Match) -> str:
        """Return a link to the appripriate entry in Roll20."""
        skill = match.group(1)
        skill = string.capwords(skill)
        url = f"https://roll20.net/compendium/dnd5e/{skill}#content"

        return f"""<a href="{url}">{skill}</a>"""
    
    @staticmethod
    def render_spell(match: re.Match) -> str:
        """Convert spell references to Roll20 links."""
        spell = string.capwords(match.group(1))
        url = f"https://roll20.net/compendium/dnd5e/{quote(spell, safe='')}"

        spell_url = url_for("tracker_bp.get_spell_tooltip", spell_name=spell)
        spell_url = sanitize_names(spell_url)
        func = f"showNewTooltip(event, '{spell_url}')"
        
        return f"""<span class="tooltip" onmouseenter="{func}" onmouseleave="hideTooltip(event)"><a href="{url}">{spell}</a></span>"""

    @staticmethod
    def render_status(match: re.Match) -> str:
        """Handle references to thr surpriused and concentration statuses."""
        # I haven't seen any references to other kinds of statuses, just these two.
        status_name = match.group(1)
        status_text = match.group(2) or status_name

        url = {
            "surprised": "https://roll20.net/compendium/dnd5e/Combat#toc_3",
            "concentration": "https://roll20.net/compendium/dnd5e/Spells?expansion=34047#toc_22"
        }.get(status_name)

        return f"""<a href="{url}">{status_text}</a>"""

def ordinal(s: str | int) -> str:
    if isinstance(s, int):
        s = str(s)
    if any(s.endswith(suffix) for suffix in ("11", "12", "13")):
        return s + "th"
    elif s.endswith("1"):
        return s + "st"
    elif s.endswith("2"):
        return s + "nd"
    elif s.endswith("3"):
        return s + "rd"
    else:
        return s + "th"


def add_filters(app):
    app.jinja_env.filters["macro5e"] = Macro5e.render_macros
    app.jinja_env.filters["ordinal"] = ordinal

    app.jinja_env.globals["current_app_version"] = importlib.metadata.version("dmtoolkit")