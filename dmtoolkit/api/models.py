from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, TypeVar, Generic

import dominate.tags as dtags
from flask import render_template_string

T = TypeVar("T")

class Reference(Generic[T]):
    """Used as a marker to indicate we should not directly serialize this class."""
    pass

@dataclass
class Monster:
    # This class will be moved to the Monsters API when it gets made
    name: str
    source: str
    page: int
    size_str: str
    maintype: str
    alignment: str
    ac: list[AC]
    hp: HP
    speed: Speed
    cr: str
    xp: int

    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    passive: int
    
    skills: Optional[dict[str, str]] = field(default_factory=dict)
    saves: Optional[dict[str, str]] = field(default_factory=dict)
    dmg_vulnerabilities: Optional[list[str]] = field(default_factory=list)
    dmg_resistances: Optional[list[str]] = field(default_factory=list)
    dmg_immunities: Optional[list[str]] = field(default_factory=list)
    cond_immunities: Optional[list[str]] = field(default_factory=list)
    senses: Optional[list[str]] = field(default_factory=list)
    languages: Optional[list[str]] = field(default_factory=list)
    
    traits: Optional[list[Entry]] = field(default_factory=list)
    actions: Optional[list[Entry]] = field(default_factory=list)
    bonus_actions: Optional[list[Entry]] = field(default_factory=list)
    reactions: Optional[list[Entry]] = field(default_factory=list)
    legendary_actions: Optional[Section] = None
    
    spellcasting: Optional[list[SpellCasting]] = field(default_factory=list)
    # environment: list[str]

    other_sources: list[dict] = field(default_factory=list)
    subtype: str = None
    actions_note: str = "" # See Homunculus Servant-TCE for example
    mythic: Section = None

    key: str = ""

    

    def __post_init__(self):
        if not self.key:
            self.key = f"{self.name}-{self.source}"


@dataclass
class AC:
    value: int
    note: Optional[str] = None
    with_braces: bool = False

    def __str__(self):
        string = str(self.value)
        if self.note:
            note = f"({self.note})" if not self.with_braces else self.note
            string += f" {note}"
        return f"({string})" if self.with_braces else string

    def from_spec(ac_spec: int | list) -> list[AC]:
        if isinstance(ac_spec, int):
            return [AC(ac_spec)]
        if isinstance(ac_spec, list):
            ac_list = []
            for spec in ac_spec:
                if isinstance(spec, int):
                    ac_list.append(AC(spec))
                    continue
                value = spec["ac"]
                if "from" in spec:
                    aux_str = ", ".join(spec["from"])
                if "condition" in spec:
                    aux_str = spec["condition"]
                braces = spec.get("braces", False)
                ac_list.append(AC(value, aux_str, braces))
            return ac_list
        else:
            raise TypeError(f"Unexpected type '{type(ac_spec).__name__}', {ac_spec}")


@dataclass
class HP:
    average: int = 0
    formula: str = ""
    special: str = ""

    def __str__(self):
        if self.special:
            return self.special
        return f"{self.average} ({self.formula})"


    def __int__(self):
        return self.average


@dataclass
class Scalar:
    """Represents a value with an optional note."""
    value: Any
    note: Optional[str] = ""

    def __str__(self):
        if self.note:
            return f"{self.value} ({self.note})"
        return str(self.value)
    

    def __bool__(self):
        return bool(self.value)
    

    def __int__(self):
        return int(self.value)
    

    def __float__(self):
        return float(self.value)
    

    def __bytes__(self):
        return bytes(self.value)


    def __eq__(self, other):
        if isinstance(other, Scalar):
            return self.value == other.value
        return self.value == other
    

    def __lt__(self, other):
        if isinstance(other, Scalar):
            return self.value < other.value
        return self.value < other
    

    def __gt__(self, other):
        if isinstance(other, Scalar):
            return self.value > other.value
        return self.value > other
    

    def __le__(self, other):
        if isinstance(other, Scalar):
            return self.value <= other.value
        return self.value <= other
    

    def __ge__(self, other):
        if isinstance(other, Scalar):
            return self.value >= other.value
        return self.value >= other
    

    def __add__(self, other):
        if isinstance(other, Scalar):
            return self.value + other.value
        return Scalar(self.value + other, self.note)
    

    def __sub__(self, other):
        if isinstance(other, Scalar):
            return self.value - other.value
        return Scalar(self.value - other, self.note)
    

    def __mul__(self, other):
        if isinstance(other, Scalar):
            return self.value * other.value
        return Scalar(self.value * other, self.note)
    

    def __div__(self, other):
        if isinstance(other, Scalar):
            return self.value / other.value
        return Scalar(self.value / other, self.note)
    

    def __mod__(self, other):
        if isinstance(other, Scalar):
            return self.value % other.value
        return Scalar(self.value % other, self.note)
    

    def __floordiv__(self, other):
        if isinstance(other, Scalar):
            return self.value // other.value
        return Scalar(self.value // other, self.note)
    

    def __pow__(self, other):
        if isinstance(other, Scalar):
            return self.value ** other.value
        return Scalar(self.value ** other, self.note)
    

    def __radd__(self, other):
        if isinstance(other, Scalar):
            return other.value + self.value
        return Scalar(other + self.value, self.note)
    

    def __rsub__(self, other):
        if isinstance(other, Scalar):
            return other.value - self.value
        return Scalar(other - self.value, self.note)
    

    def __rmul__(self, other):
        if isinstance(other, Scalar):
            return other.value * self.value
        return Scalar(other * self.value, self.note)
    

    def __rdiv__(self, other):
        if isinstance(other, Scalar):
            return other.value / self.value
        return Scalar(other / self.value, self.note)
    

    def __rmod__(self, other):
        if isinstance(other, Scalar):
            return other.value % self.value
        return Scalar(other % self.value, self.note)
    

    def __rfloordiv__(self, other):
        if isinstance(other, Scalar):
            return other.value // self.value
        return Scalar(other // self.value, self.note)
    

    def __rpow__(self, other):
        if isinstance(other, Scalar):
            return other.value ** self.value
        return Scalar(other ** self.value, self.note)
    

    def __neg__(self):
        return Scalar(-self.value, self.note)


@dataclass
class Speed:
    walk: Scalar = field(default_factory=lambda: Scalar(0))
    fly: Scalar = field(default_factory=lambda: Scalar(0))
    burrow: Scalar = field(default_factory=lambda: Scalar(0))
    swim: Scalar = field(default_factory=lambda: Scalar(0))
    climb: Scalar = field(default_factory=lambda: Scalar(0))
    can_hover: bool = False


    @staticmethod
    def from_spec(speed_spec: int | dict) -> Speed:
        if isinstance(speed_spec, int):
            return Speed(walk=Scalar(speed_spec))
        args = {}
        for x in ("walk", "fly", "burrow", "swim", "climb"):
            if x not in speed_spec:
                continue
            if isinstance(speed_spec[x], bool):
                # Sometimes a speed just says 'True', in which case I assume it's equal to the walk speed
                args[x] = args["walk"]
            elif isinstance(speed_spec[x], int):
                args[x] = Scalar(speed_spec[x])
            else:
                args[x] = Scalar(speed_spec[x]["number"], speed_spec[x]["condition"])
        if "canHover" in speed_spec:
            args["can_hover"] = speed_spec["canHover"]
        s = Speed(**args)
        return s

    def __str__(self) -> str:
        speed_strs = []
        if self.walk:
            speed_strs.append(str(self.walk) + "ft.")
        if self.fly:
            speed_strs.append(
                f"Fly {self.fly.value} ft."
            )
        if self.burrow:
            speed_strs.append(
                f"Burrow {self.burrow.value} ft."
                f" ({self.burrow.note})" if self.burrow.note else ""
            )
        if self.swim:
            speed_strs.append(
                f"Swim {self.swim.value} ft."
                f" ({self.swim.note})" if self.swim.note else ""
            )
        if self.climb:
            speed_strs.append(
                f"Climb {self.climb.value} ft."
                f" ({self.climb.note})" if self.climb.note else ""
            )
        
        return ", ".join(speed_strs)

@dataclass
class Entry:
    title: str = ""
    body: list[str|Entry|Table] = field(default_factory=list)
    style: dict[str, str|int] = field(default_factory=dict)

    @staticmethod
    def from_spec(spec: dict | str | list) -> Entry:
        """Converts an entry (as it appears in the monster JSON) to an Entry object."""
        if isinstance(spec, str):
            return Entry("", [spec])
        elif isinstance(spec, list):
            return Entry("", [Entry.from_spec(x) for x in spec])
        elif not isinstance(spec, dict):
            raise TypeError(f"Unexpected type '{type(spec).__name__}'")
        
        title = spec.get("name", "")
        body = []
        style = {}
        
        # Sometimes, if there's only one entry, they use the `entry: str` field instead of
        #   `entries: list[str]`
        if "entry" in spec or "entries" in spec:
            if "entry" in spec:
                assert "entries" not in spec, "Entry has both 'entry' and 'entries' keys!"
                spec["entries"] = [spec["entry"]]
                del spec["entry"]

            for entry in spec["entries"]:
                body += Entry._body_from_spec(entry)

        if "type" in spec:
            match spec["type"]:
                case "entries":
                    # Kind of a dumb type. Literally just means this is an entry :/
                    pass
                case "list":
                    for item in spec["items"]:
                        body.append(Entry._body_from_spec(item))
                case "item":
                    # There's nothing special about 'item'; it just means it's nested inside an
                    #   outer 'list'
                    pass
                case "options":
                    # Another do-nothing type
                    pass
                case "quote":
                    # Indicates this is supposed to be a quote.
                    style["font-style"] = ["italic"]
                case "statblock":
                    # Inline statblocks; these are hard to implement so I won't do it now. I don;t
                    #   think they appear that often anyway.
                    pass
                case "refOptionalfeature":
                    # Used in class specs to indicate an optional feature. However, I'm not
                    #   handling these references since I don't think it's necessary, so instead
                    #   we should just display the name of the feature
                    body.append(spec["optionalfeature"])
                case "table":
                    return Table.from_spec(spec)
                case "inset":
                    style |= {"margin-left": "24px"}
                case "abilityDc":
                    # Used in "spellcasting" entries for classes
                    ability_mod = spec["attributes"][0]
                    body.append(f"<strong>Spell save DC</strong> = 8 + {ability_mod.upper()} modifier + Proficiency Bonus")
                case "abilityAttackMod":
                    # Used in "spellcasting" entries for classes
                    ability_mod = spec["attributes"][0]
                    body.append(f"<strong>Spell attack modifier</strong> = {ability_mod.upper()} modifier + Proficiency Bonus")
                case "refFeat":
                    # Reference to a Feat
                    body.append("{{@feat {0}}}".format(spec["feat"]))
                case _:
                    raise ValueError(f"Unexpected type '{spec['type']}'")

        return Entry(title, body, style=style)

    @staticmethod
    def _body_from_spec(spec: dict | str | list) -> list[str | Entry | list[Entry]]:
        """Like Entry from spec, but only called when we already have a top-level Entry object in
        place. This was we can avoid wrapping strings which are inside a `body` field already."""
        if isinstance(spec, str):
            return [spec]
        elif isinstance(spec, list):
            lists = [Entry._body_from_spec(x) for x in spec]
            # Return the flattened list
            return [item for nested in lists for item in nested]
        elif "items" in spec:
            lists = [Entry._body_from_spec(item) for item in spec["items"]]
            return [item for nested in lists for item in nested]
        return [Entry.from_spec(spec)]

    def _dom(self) -> str:
        """Returns HTML markup."""
        stylestr = ""
        if self.style:
            stylestr = ' style="' + ", ".join([f"{k: v}" for k, v in self.style.items()]) + '"'
        root = dtags.div(style=stylestr)
        with root.add(dtags.p(style=stylestr)) as p:
            p.add(dtags.strong(dtags.em(self.title)))
            # Rather than render a full entry (which will be inside a <p> tag), we should just 
            #   extract the text.
            text = str(self.body[0])
            if isinstance(self.body[0], Entry):
                text = "\n".join([str(s) for s in self.body[0].body])
            p.add(text)
        
        for entry in self.body[1:]:
            root.add(Entry.to_dom(entry))
    
        return root
    
    def html(self):
        return str(self._dom())
    
    @staticmethod
    def to_dom(item: Entry | str):
        if isinstance(item, str):
            return dtags.p(item)
        return item._dom()


@dataclass
class Table(Entry):
    caption: str = ""
    col_labels: list[str] = field(default_factory=list)
    col_styles: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)

    def __post_init__(self):
        if len(self.col_labels) != len(self.col_styles):
            raise ValueError("Inconsistent number of columns!")
        for row in self.rows:
            if len(row) != len(self.col_labels):
                raise ValueError("Invalid number of columns in row!")

    @staticmethod
    def from_spec(spec: dict[str, Any]):
        mappings = {
            "caption": "caption",
            "colLabels": "col_labels",
            "colStyles": "col_styles",
            "rows": "rows"
        }
        return Table(**{mappings[k]: spec[k] for k in mappings if k in spec})
    
    def _dom(self) -> dtags.html_tag:
        table = dtags.table(cls="entry")
        table.add(dtags.caption(self.caption))
        with(table.add(dtags.tr())):
            for label, styles in zip(self.col_labels, self.col_styles):
                dtags.th(label, cls=styles)
        for idx, row in enumerate(self.rows):
            cls = "oddrow" if idx % 2 else ""
            with table.add(dtags.tr(cls=cls)):
                for content, styles in zip(row, self.col_styles):
                    dtags.td(content, cls=styles)
        return table
    
    
    def html(self) -> str:
        return str(self._dom())
    
    def __str__(self):
        return self.html()




@dataclass
class Section:
    title: str
    body: str
    header: str = ""

@dataclass
class SpellCasting:
    name: str
    typ: str
    ability: str = ""
    header: Entry = None
    slots: list[SpellList] = field(default_factory=list)
    at_will: SpellList = field(default_factory=list)
    daily: list[DailySpellList] = field(default_factory=list)

    @staticmethod
    def from_spec(spec: dict[str, Any]) -> SpellCasting:
        name = spec["name"]
        typ = spec["type"]
        ability = spec.get("ability")
        header = Entry.from_spec({"name": name, "entries": spec["headerEntries"]})
        spells = SpellCasting(name, typ, ability, header)
        if at_will := spec.get("will"):
            spells.at_will = SpellList.from_spec({"spells": at_will})
        if daily := spec.get("daily"):
            spells.daily = [DailySpellList.from_spec(k, v) for k, v in daily.items()]
        if spell_list := spec.get("spells"):
            max_level = max(int(k) for k in spell_list.keys())
            slots = [None]*(max_level+1)
            for k, v in spell_list.items():
                # k is the level
                # v is the spell list and number of slots
                lvl = int(k)
                s = SpellList.from_spec(v)
                slots[lvl] = s
            spells.slots = slots
        
        return spells

    def html(self) -> str:
        template = """
            {{ self.entry.html() }}
            {% if self.slots %}
                {% for spelllist in self.slots %}
                    {% if loop.index0 == 0 %}Cantrips (at will){% else %}{{ loop.index0 | ordinal }} level ({{self.slots.slots}} slots){% endif %}: {{ ", " | join(self.slots.spells)}}
                {% endfor %}
            {% endif %}
        """


@dataclass
class SpellList:
    slots: int
    spells: list[str]

    @staticmethod
    def from_spec(spec: dict[str, Any]) -> SpellList:
        return SpellList(
            slots = int(spec.get("slots", 0)),
            spells = spec["spells"]
        )

@dataclass
class DailySpellList:
    per_day: int
    spells: list[str]

    @staticmethod
    def from_spec(key: str, spells: list[str]) -> DailySpellList:
        # The 'key' will be either a integer, or something like '2e' or '3'.
        key = key.replace("e", "")
        per_day = int(key)
        return DailySpellList(per_day, spells)


@dataclass
class Modifier:
    target: str
    mod: int

    def __post_init__(self):
        # Often, it's entered as '+1' or '-5'.
        if isinstance(self.mod, str):
            self.mod = int(self.mod)


@dataclass
class SkillMod(Modifier):
    def __post_init__(self):
        # Validate skills
        allowed_skills = {"athletics", "acrobatics", "sleight of hand", "stealth", "arcana", "history", "investigation", "nature", "religion", "animal handling", "insight", "medicine", "perception", "survival", "deception", "intimidation", "performance", "persuasion"}
        if self.target.casefold() not in allowed_skills:
            raise ValueError(f"Invalid skill name: {self.target}")
        return super().__post_init__()
    

    def __str__(self):
        return "{@skill " + self.target.title() + "} " + f"{self.mod:+}"

@dataclass
class SkillList:
    skills: list[SkillMod|SkillList]
    mode: str = "all"

    def __post_init__(self):
        allowed_modes = {"all", "any", "one"}
        if self.mode not in allowed_modes:
            raise ValueError(f"Invalid mode: {self.mode}")
    
    def __str__(self):
        string = ""
        if self.mode == "one":
            string = "plus one of the following: "
        elif self.mode == "any":
            string.mode = "plus any of the following: "
        string += ", ".join(str(x) for x in self.skills)
        return string
    
    @staticmethod
    def from_spec(skill_spec: dict[str, str|dict]) -> SkillList:
        if not skill_spec:
            return None
        skills = []
        for k, v in skill_spec.items():
            if k == "other":
                # ex.: {other: [{oneOf: {arcana: +7, nature: +2}}]}
                for item in v:
                    for k_, v_ in item.items():
                        if k_ == "oneOf":
                            skills_ = SkillList.from_spec(v_)
                            skills_.mode = "one"
                            skills.append(skills_)
                        elif k_ == "anyOf":
                            skills_ = SpellList.from_spec(v_)
                            skills_.mode = "any"
                            skills.append(skills_)
                        elif k_ == "allOf":
                            # All is the default; we can just add these to the main list
                            skills += SpellList.from_spec(v_).skills
            else:
                skills.append(SkillMod(k, v))
        return SkillList(skills)

@dataclass
class AgeParams:
    maximum: int
    mature: int

    @staticmethod
    def from_spec(spec: dict[str, Any]) -> AgeParams:
        return AgeParams(spec["max"], spec.get("mature", 0))


@dataclass
class SizeParams:
    weight_base: int
    height_base: int
    weight_mod: str = ""
    height_mod: str = ""

    @staticmethod
    def from_spec(spec: dict[str, Any]) -> SizeParams:
        return SizeParams(
            weight_base = spec["baseWeight"],
            height_base = spec.get("weightMod", ""),
            weight_mod = spec["baseHeight"],
            height_mod = spec.get("heightMod", "")
        )

@dataclass
class Race:
    name: str
    source: str
    speed: Speed
    ability_scores: dict[str, int]
    
    size: list[str]
    age: AgeParams = None
    size_params: SizeParams = None
    blindsight: int = 0
    darkvision: int = 0

    skills: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    feats: list = field(default_factory=list)
    traits: list[Entry] = field(default_factory=list)

    dmg_resistances: list[str] = field(default_factory=list)
    dmg_vulnerabilities: list[str] = field(default_factory=list)
    dmg_immunities: list[str] = field(default_factory=list)
    cond_immunities: list[str] = field(default_factory=list)

    tool_profs: list[str] = field(default_factory=list)
    armor_prof: list[str] = field(default_factory=list)
    weapon_profs: list[str] = field(default_factory=list)

    key: str = ""
    _id: str = ""

    def __post_init__(self):
        self._id = f"{self.name}-{self.source}"


@dataclass
class Player:
    name: str
    hp: int
    ac: int
    pp: int
    race_id: str = ""
    class_id: str = ""
    subclass_id: str = ""

    level: int = 1
    enabled: bool = False
    notes: str = ""

@dataclass
class Class:
    name: str
    spellcasting_ability: str
    multiclassing: dict
    hitdice: str
    weapon_profs: list[str] = field(default_factory=list)
    armor_profs: list[str] = field(default_factory=list)
    tool_profs: list[str] = field(default_factory=list)
    class_features: list[Entry] = field(default_factory=list)
    subclasses: list[Subclass] = field(default_factory=list)

@dataclass
class Subclass:
    name: str
    subclass_features: list[Entry] = field(default_factory=list)

@dataclass
class ClassFeature(Entry):
    level: int = 0