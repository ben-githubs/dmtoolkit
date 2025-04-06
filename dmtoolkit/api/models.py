from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from flask import render_template_string

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

    def __str__(self):
        string = str(self.value)
        if self.note:
            string += f" ({self.note})"
        return string

    def from_spec(ac_spec: int | list) -> list[AC]:
        if isinstance(ac_spec, int):
            return [AC(ac_spec)]
        if isinstance(ac_spec, list):
            ac_list = []
            for spec in ac_spec:
                if isinstance(spec, int):
                    ac_list.append(AC(ac_spec))
                    continue
                value = spec["ac"]
                if "from" in spec:
                    aux_str = ", ".join(spec["from"])
                if "condition" in spec:
                    aux_str = spec["condition"]
                    if spec.get("braces"):
                        aux_str = f"({aux_str})"
                ac_list.append(AC(value, aux_str))
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


    def from_spec(speed_spec) -> Speed:
        args = {}
        for x in ("walk", "fly", "burrow", "swim", "climb"):
            if x not in speed_spec:
                continue
            if isinstance(speed_spec[x], int):
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
                f" ({self.fly.note})" if self.fly.note else ""
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
    title: str
    body: list[str|Entry]

    def from_spec(spec: dict) -> Entry:
        """Converts an entry (as it appears in the monster JSON) to an Entry object."""
        title = spec["name"]
        body = []
        
        # Sometimes, if there's only one entry, they use the `entry: str` field instead of
        #   `entries: list[str]`
        if "entry" in spec:
            assert "entries" not in spec, "Entry has both 'entry' and 'entries' keys!"
            spec["entries"] = [spec["entry"]]

        for entry in spec["entries"]:
            if isinstance(entry, str):
                body.append(entry)
            elif isinstance(entry, dict):
                match entry["type"]:
                    case "list":
                        for item in entry["items"]:
                            if isinstance(item, dict):
                                assert item["type"] == "item", f"Got {item['type']}"
                                body.append(Entry.from_spec(item))
                            elif isinstance(item, str):
                                body.append(item)
                            else:
                                raise ValueError(f"Unexpected type '{type(item).__name__}'")
                    case _:
                        raise ValueError(f"Unexpected type '{entry['type']}'")
            else:
                raise TypeError(f"Unexpected type '{type(entry).__name__}'")

        return Entry(title, body)

    def html(self) -> str:
        """Returns HTML markup."""
        template = """
            <p><strong><em>{{entry.title}}.</em></strong> {{entry.body[0]}}</p>
            {% for text in entry.body[1:] %}
                <p>{{text}}</p>
            {% endfor %}
        """
        return render_template_string(template, entry=self)



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
    slots: list[SpellList] = field(default=None)
    at_will: SpellList = field(default=None)
    daily: list[DailySpellList] = field(default=None)

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

    def from_spec(spec: dict[str, Any]) -> SpellList:
        return SpellList(
            slots = int(spec.get("slots", 0)),
            spells = spec["spells"]
        )

@dataclass
class DailySpellList:
    per_day: int
    spells: list[str]

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