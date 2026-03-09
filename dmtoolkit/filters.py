import string
import re
from urllib.parse import quote
from flask import url_for
from dmtoolkit.api import items
import importlib.metadata

def sanitize_names(name: str) -> str:
    """Sanitize the names for use in a javascript string."""
    return name.replace("'", r"\'").replace('"', r"\"")

def split_text(text: str) -> tuple[str, str, str]:
    split_text = [s.strip() for s in text.split("|")]
    id = split_text[0]
    src = split_text[1] if len(split_text) > 1 else ""
    display_string = split_text[2] if len(split_text) > 2 else ""
    return (id, src, display_string)

def titlecase(s: str) -> str:
    """Returns a smartly-titled string."""
    ignore_words = ["A", "Of", "And", "The", "Or", "An"]
    s = string.capwords(s)
    return " ".join(wd.lower() if wd in ignore_words else wd for wd in s.split(" "))


class Macro5e:
    damage = re.compile(r"{@damage (.*?)}")
    dc = re.compile(r"\{@dc (\d+)\}")
    dice = re.compile(r"\{@dice (\d+)?d(\d+)\}")
    hit = re.compile(r"{@hit (.*?)}")
    on_hit = re.compile(r"{@h}")
    italics = re.compile(r"{@i(?:talics)? (.*?)}")
    item = re.compile(r"\{@item (.*?)\}")
    skill = re.compile(r"{@skill (.*?)}")
    spell = re.compile(r"\{@spell (.*?)}")
    status = re.compile(r"\{@status (\w+)(?:\s*\|\|\s*(\w+))?}")

    @staticmethod
    def render_macros(text: str) -> str:
        """Turns the 5etools macros (like {@spell magic missile}) into the appropriate HTML elements."""
        text = str(text) # Just in case

        """
        List of all 5e macros (not all have been implemented yet)
            5etools, actResponse, actSave, actSaveFail, actSaveFailBy, actSaveSuccess,
            actSaveSuccessOrFail, actTrigger, action, adventure, area, atk, atkr, b, book, card,
            chance, class, classFeature, color, condition, creature, d20, damage, dc, deck,
            deity, dice, disease, filter, h, hazard, hit, hom, i, italic, item, language,
            link, note, object, optfeature, quickref, race, recharge, scaledamage, scaledice, sense,
            skill, skillCheck, spell, status, subclassFeature, table, variantrule
        """
        renderers = {
            r"{@actResponse}": r"<em>Response: </em>",
            r"{@actSave (\w+)}": Macro5e.render_act_save,
            r"{@actSaveFail}": r"<em>Failure: </em>",
            r"{@actSaveFailBy (\d+)}": r"<em>Failure by \1 or More: ",
            r"{@actSaveSuccess}": r"<em>Success: </em>",
            r"{@actSaveSuccessOrFail}": r"<em>Failure or Success: </em>",
            r"{@actTrigger}": r"<em>Trigger: </em>",
            r"{@action ([\w\s]+)}": r"\1 Action",
            r"{@adventure (.*?)}": Macro5e.render_adventure,
            r"{@area (.*?)}": Macro5e.render_area,
            r"{@atk (.*?)}": Macro5e.render_atk,
            r"{@atkr (.*?)}": Macro5e.render_atkr,
            r"{@b (.*?)}": r"<strong>\1</strong>",
            r"{@book ([^|}]+).*?}": r"\1", # Keep just first part as display text
            r"{@card ([^|}]+).*?}": r"\1", # Keep just first part as display text
            r"{@chance (.*?)}": Macro5e.render_chance,
            r"{@class (.*?)}": Macro5e.render_class,
            r"{@classFeature ([^|}]+).*?}": r"\1", # Keep just first part as display text
            r"{@color (.*?)\|(.*?)}": r'<span style="color: \2">\1</span>',
            r"{@condition (\w+)}": Macro5e.render_condition,
            r"{@creature (.*?)}": Macro5e.render_creatures,
            r"{@d20 ([\-\+]\d+)}": Macro5e.render_d20_mod,
            r"{@damage (.*?)}": r"\1",
            r"{@dc (\d+)}": r"DC \1",
            r"{@deck (.*?)}": Macro5e.render_deck,
            r"{@deity (.*?)}": r"\1",
            r"{@dice (\d+)?d(\d+)}": Macro5e.render_dice,
            r"{@disease ([^|}]+).*?}": r"\1", # Keep just first part as display text
            r"{@filter ([^|}]+).*?}": r"\1", # Filters open a page on 5e.tools with a filtered list of spells/items/etc.
            r"{@h}": r"<em>Hit: </em>",
            r"{@hazard (.*?)}": Macro5e.render_hazard,
            r"{@hit (.*?)}": Macro5e.render_hit,
            r"{@hom}": r"<em>Hit or Miss: </em>",
            r"{@i(?:talics)? (.*?)}": r"<em>\1</em>",
            r"{@item (.*?)}": Macro5e.render_item,
            r"{@language}": Macro5e.render_language,
            r"{@link (.*?)\|(.*?)}": r"""<a href="\2">\1</a>""",
            r"{@note (.*?)}": r"""<span class="note">\1</span>""",
            r"{@object (.*?)}": Macro5e.render_object,
            r"{@optfeature ([^|}]+).*?}": r"\1", # Keep just first part as display text
            r"{@quickref (.*?)}": Macro5e.render_quickref,
            r"{@race ([^|}]+).*?}": r"\1", # Keep just first part as display text
            r"{@recharge ([^|}]+).*?}": r"(Recharge \1-6)",
            r"{@scaledamage \dd\d\|\d-\d\|(\dd\d)}": "\1",
            r"{@scaledice \dd\d\|\d-\d\|(\dd\d)}": "\1",
            r"{@sense (.*?)}": "\1",
            r"{@skill (.*?)}": Macro5e.render_skill,
            r"{@skillCheck \w+ ([\-\+]?\d+)}": Macro5e.render_skillcheck,
            r"{@spell (.*?)}": Macro5e.render_spell,
            r"{@status (\w+)(?:\s*\|\|\s*(\w+))?}": Macro5e.render_status,
            r"{@subclassFeature ([^|}]+).*?}": r"\1", # Keep just first part as display text
            r"{@table ([^|}]+).*?}": r"\1", # Keep just first part as display text
            r"{@variantrule ([^|}]+).*?}": r"\1", # Keep just first part as display text
        }

        for pattern, renderer in renderers.items():
            text = re.sub(pattern, renderer, text)

        return text

    @staticmethod
    def render_act_save(match: re.Match) -> str:
        save_type = {
            "str": "Strength",
            "dex": "Dexterity",
            "con": "Constitution",
            "int": "Intelligence",
            "wis": "Wisdom",
            "cha": "Charisma"
        }.get(match.group(1), "")
        return f"<em>{save_type} Saving Throw:</em>".strip()


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
    def render_atkr(match: re.Match) -> str:
        # Basically the same as render_atk, but using the 2024 wording.
        atk_type = match.group(1)
        atk_str = {
            "m": "Melee Attack Rool",
            "r": "Ranged Attack Roll",
            "m,r": "Melee or Ranged Attack Roll",
        }.get(atk_type, "Attack")
        return f"<em>{atk_str}:</em>"
    
    @staticmethod
    def render_adventure(match: re.Match) -> str:
        # In 5e.tools, these link to specific parts of source books. Since we don't support 
        #   viewing source books, we'll just replace these with the intended render text without
        #   any linking.
        # Expected format: {@adventure RENDER_TEXT|SRC_BOOK|PAGE|SECTION_HEADER}
        return match.group(1).split("|")[0].strip()
    
    @staticmethod
    def render_area(match: re.Match) -> str:
        # I honestly don't know what this is supposed to be; it's only used in one place. We'll
        #   just keep the original render text.
        # Expected format: {@area RENDER_TEXT|??|??}
        return match.group(1).split("|")[0].strip()

    @staticmethod
    def render_chance(match: re.Match) -> str:
        # 5e.tools has a rolling tool which means you can click these and it automatically rolls
        #   for success. We don't, so we just want to display the render text.
        # Expected format: {@chance CHANCE_PERC|RENDER_TEXT?|???|SUCCESS_TEXT?|FAIL_TEXT?}
        parts = match.group(1).split("|")
        if len(parts) >= 2:
            # Return render text, if there is any defined
            return parts[1].strip()
        else:
            # Return inferred render text
            return f"{parts[0].strip()} percent"

    @staticmethod
    def render_class(match: re.Match) -> str:
        # Just display render text
        # Expected format: {@class CLASS_ID|SRC?|RENDER_TEXT|???|???}
        parts = match.group(1).split("|")
        if len(parts) >= 3:
            # Return render text, if there is any defined
            return parts[2].strip()
        else:
            # Return inferred render text
            return f"{parts[0].strip()}"

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
    def render_creatures(match: re.Match) -> str:
        # Expected format: {@chance CREATURE_ID|SRC|RENDER_TEXT}
        parts = match.group(1).split("|")
        if len(parts) >= 3:
            # Return render text, if there is any defined
            return parts[2].strip()
        else:
            # Return inferred render text
            return f"{parts[0].strip()}"
    
    @staticmethod
    def render_d20_mod(match: re.Match) -> str:
        return f"{int(match.group(1)):+}"

    @staticmethod
    def render_deck(match: re.Match) -> str:
        # Expected format: {@chance DECK_ID|SRC|RENDER_TEXT}
        parts = match.group(1).split("|")
        if len(parts) >= 3:
            # Return render text, if there is any defined
            return parts[2].strip()
        else:
            # Return inferred render text
            return f"{parts[0].strip()}"

    @staticmethod
    def render_dice(match: re.Match) -> str:
        groups = match.groups(default="1")
        return "d".join(groups)

    @staticmethod
    def render_hazard(match: re.Match) -> str:
        # Expected format: HAZARD|SRC
        #  If the SRC is empty, this is an SRD hazard
        parts = match.group(1).split("|")
        if len(parts) == 1:
            # Regular SRD hazards can be linked via 5esrd.com
            link = "https://www.5esrd.com/gamemastering/hazards/" + "-".join(parts[0].lower().split())
            return f"""<a href="{link}">{parts[0]}</a>"""
        # I couldn't find a site with the 2024 hazards listed for free, so just return the text
        return parts[0]

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
    def render_language(match: re.Match) -> str:
        # Expected format: {@class LANUGAGE|SRC|DIALECT}
        parts = match.group(1).split("|")
        if len(parts) >= 3:
            # Return dialect, if there is any defined
            return parts[2].strip()
        else:
            # Return base language
            return f"{parts[0].strip()}"
        
    @staticmethod
    def render_object(match: re.Match) -> str:
        # TODO: Add pop-up statblock cards for objects (like Spells have)
        # Expected format: {@class OBJ_ID|SRC|TEXT}
        parts = match.group(1).split("|")
        if len(parts) >= 3:
            # Return text, if there is any defined
            return parts[2].strip()
        else:
            # Return base object ID
            return f"{parts[0].strip()}"
    
    @staticmethod
    def render_quickref(match: re.Match) -> str:
        # TODO: Add quickref tooltips
        # Expected format: {@adventure RuleName||??||RenderText}
        parts = match.group(1).split("|")
        if len(parts) >= 5:
            # Return text, if there is any defined
            return parts[4].strip()
        else:
            # Return base rule name
            return f"{parts[0].strip()}"

    @staticmethod
    def render_skill(match: re.Match) -> str:
        """Return a link to the appripriate entry in Roll20."""
        skill = match.group(1)
        skill = string.capwords(skill)
        url = f"https://roll20.net/compendium/dnd5e/{skill}#content"

        return f"""<a href="{url}">{skill}</a>"""

    @staticmethod
    def render_skillcheck(match: re.Match) -> str:
        skill_mod = int(match.group(1))

        return f"{skill_mod:+}"
    
    @staticmethod
    def render_spell(match: re.Match) -> str:
        """Convert spell references to Roll20 links."""
        spell = string.capwords(match.group(1))
        spell_id, _, spell_name = split_text(spell)
        url = f"https://roll20.net/compendium/dnd5e/{quote(spell_id, safe='')}"

        spell_url = url_for("tracker_bp.get_spell_tooltip", spell_name=spell_id)
        spell_url = sanitize_names(spell_url)
        func = f"showNewTooltip(event, '{spell_url}')"
        
        return f"""<span class="tooltip" onmouseenter="{func}" onmouseleave="hideTooltip(event)"><a href="{url}">{titlecase(spell_name or spell_id)}</a></span>"""

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