function nextCombatant() {
    current = $("tr.selected");
    next = current.next();
    if (next.length == 0) {
        next = $("table#turntracker").children().eq(0).children().eq(1);
    }
    next.addClass("selected");
    current.removeClass("selected");
}

function prevCombatant() {
    current = $("tr.selected");
    next = current.prev();
    if (next.attr("id") == "tracker-header") {
        // Don't want to select header row, so just go back another space
        next = $("table#turntracker").children().eq(0).children().last();
    }
    next.addClass("selected");
    current.removeClass("selected");
}

function sortInitiativeTable() {
    table = $('#turntracker');
    rows = table.find('tr:gt(0)').toArray().sort(compareRows).reverse();
    for (i = 0; i < rows.length; i++) {
        table.append(rows[i]);
        console.log(i);
    }
}

function compareRows(r1, r2) {
    v1 = getInitiative(r1), v2 = getInitiative(r2);
    console.log(v1);
    console.log(v2);
    console.log(v1-v2);
    return v1 - v2;
}

function getInitiative(row) {
    cell = $(row).children('td').eq(4);
    if (cell.children('input').val()) {
        return parseInt(cell.children('input').val());
    };
    return parseInt(cell.text());
}

function deleteRow(event) {
    // Don't let us delete a row that's selected
    self = $(event.target);
    row = self;
    if (!self.is("tr")) {
        row = self.closest("tr");
    }
    if (row.hasClass("selected")) {
        nextCombatant();
    }
    row.remove();
    refreshXP();
}

function updateHP(self) {
    // Get or Set current HP
    hp = parseInt(self.attr('placeholder'));
    value = $.trim(self.val());
    // If the value is a relative amount
    if (value.includes('+') || value.includes('-')) {
        hp += parseInt(value);
    } else {
        hp = parseInt(value);
    }
    self.attr('placeholder', hp);
    self.val('');
}

function addMonster(monsterId) {
    $.ajax({
        url: `/api/monsters-combat-overview?name=${monsterId}`,
        method: 'GET',
        success: function(response) {
            tbody = $("#turntracker").children().eq(0);
            trow = $("<tr></tr>");
            data = $.parseJSON(response);
            btn = $('<td class="w3-btn w3-red w3-ripple remove-btn">X</td>');
            btn.click(function (event) { deleteRow(event); });
            trow.append(btn);
            trow.append(`<td><input class=w3-input w3-border-0" type="text" value="${data.name}" style="width: 100%; text-align: left"><br/><span class="w3-small"><em>${data.name}</em></span></td>`);
            trow.append(`<td>${data.ac}</td>`);

            td = $(`<td>/${data.hp}</td>`);
            hpbox = $(`<input class="w3-input w3-border hpbox" type="text" placeholder="${data.hp}">`);
            hpbox.change(function() { updateHP($(this)); });
            td.prepend(hpbox);
            trow.append(td);
            
            trow.append(`<td></td>`);
            trow.append(`<td>${data.pp}</td>`);
            trow.data("id", monsterId);
            trow.data("type", "npc");
            trow.data("initMod", data.initMod);
            trow.data("xp", data.xp);

            trow.click(function(event) { updateStatblockTarget(event); });

            tbody.append(trow);
            refreshXP();
        }
    });
}

function togglePlayer(button) {
    playerName = button.prev().text();
    if (button.text() == "Add Player") {
        $.ajax({
            url: `/api/players/${playerName}`,
            method: 'GET',
            success: function(response) {
                tbody = $("#turntracker").children().eq(0);
                trow = $("<tr></tr>");
                data = $.parseJSON(response);
                btn = $('<td class="w3-btn w3-red w3-ripple remove-btn">X</td>');
                btn.click(function (event) { deleteRow(event); });
                trow.append(btn);
                trow.append(`<td><strong>${data.name}</strong><br/><span class="w3-small"><em>Player</em></span></td>`);
                trow.append(`<td style="vertical-align: middle"><input class="w3-input w3-border" type="text" value="${data.ac}"></td>`);

                td = $(`<td>/${data.hp}</td>`);
                hpbox = $(`<input class="w3-input w3-border hpbox" type="text" placeholder="${data.hp}">`);
                hpbox.change(function() { updateHP($(this)); });
                td.prepend(hpbox);
                trow.append(td);
                
                trow.append(`<td style="vertical-align: middle"><input class="w3-input w3-border" type="text" value=""></td>`);
                trow.append(`<td style="vertical-align: middle">${data.pp}</td>`)
                
                trow.data("id", `${playerName}.player`);

                trow.click(function(event) { updateStatblockTarget(event); });

                tbody.append(trow);
                updateAddPlayerButtons();
            }
        });
    } else {
        // Find the row with 
        $('#turntracker').find('tr').each( function(event) {
            n = $(this).children().eq(1).find("strong").first().text();
            if ($(this).find("td:gt(0)").first().find("strong").first().text() == playerName) {
                console.log("Found it!")
                // deleteRow(event);
                $(this).find(".remove-btn").trigger("click");
                updateAddPlayerButtons();
            }
        });
    }
}

function setContentAjax(target, url) {
    $.ajax({
        url: url,
        method: 'GET',
        success: function(response) {
            target.html(response);
        }
    })
}

function updateStatblockTarget(event) {
    self = $(event.target);
    if (!(self.is('tr') || self.is('td'))) {
        console.log("Is not a row or cell.");
        return;
    }
    
    // Add class
    $('#turntracker').find('tr').removeClass('statblock-target');
    self.closest('tr').addClass('statblock-target');

    row = self.closest('tr');

    monsterId = row.data("id");
    console.log(row);
    $.ajax({
        url: `/statblock/${monsterId}`,
        method: 'GET',
        success: function(response) {
            $('#statblock').html(response);
        }
    })
}

function rollInitiative() {
    tbody = $("#turntracker").children().eq(0);
    tbody.children().each(function() {
        data = $(this).data();
        if (data.type == "npc") {
            initMod = parseInt(data.initMod);
            initCell = $(this).children().eq(4);
            initCell.text(1 + Math.floor(Math.random()*20) + initMod);
        }
    })
}

function refreshXP() {
    // Update the XP totals at the bottom of the tracker
    tbody = $("#turntracker").children().eq(0);
    xp = 0;
    tbody.children().each(function() {
        data = $(this).data();
        if (data.type == "npc") {
            xp += data.xp;
        }
    });
    $("#xp-to-award").text(xp);
}

function updateAddPlayerButtons() {
    // Determine which players are already listed in the table and update the status of the
    //   "add" button accordingly.
    addedPlayers = [];
    table = $("#turntracker");
    table.find('tr:gt(0)').each(function() {
        data = $(this).data();
        if (data.type != "npc") {
            n = $(this).children().eq(1).find("strong").first().text();
            addedPlayers.push(n);
        }
    })

    $("#player-add-modal ._player-row").each(function() {
        name1 = $(this).children().eq(0);
        button = $(this).children().eq(1);
        if (addedPlayers.includes(name1.text())) {
            button.text("Remove");
        } else {
            button.text("Add Player");
        }
    })
}

function refreshEncounters() {
    // Get encounter info
    $.ajax({
        url: `/api/encounters`,
        method: 'GET',
        success: function(response) {
            $('.saved-encounter-list').html('');
            data = $.parseJSON(response)
            $.each(data, function(id, enc) {
                item = $('<div class="saved-encounter-list-item"></div>');
                item.data("monsters", enc.monsters);
                item.dblclick(function() { loadEncounter(this); });
                item.append($(`<span>${enc.title}</span>`));
                item.append($(`<span>${enc.desc}<span>`));
                $('.saved-encounter-list').append(item);
                console.log("Added encounter.");
            })
        }
    })
}

function loadEncounter(encounterItem) {
    // Clear current encounter
    tbody = $("#turntracker").children().eq(0);
    tbody.children().each(function() {
        data = $(this).data();
        if (data.type == "npc") {
            this.remove();
        }
    });

    // Add rows for new creatures
    console.log($(encounterItem).data("monsters"));
    $($(encounterItem).data("monsters")).each(function (i, monsterId) {
        addMonster(monsterId);
    })

    // Selection CSS
    $(".saved-encounter-list-item").each(function () {
        $(this).removeClass("selected");
    });
    $(encounterItem).addClass("selected");
}

function saveEncounter() {
    // Gather encounter info
    encounterTitle = $('input#encounter-name').val();
    encounterDesc = $('textarea#encounter-desc').val();

    monsters = [];

    $('#turntracker tr:gt(0)').each(function () {
        monsters.push($(this).data("id"));
    })

    encounter = {
        "title": encounterTitle,
        "desc": encounterDesc,
        "monsters": monsters
    }

    $.ajax({
        url: `/api/encounters`,
        method: 'POST',
        data: JSON.stringify(encounter),
        headers: {
            'Content-Type': 'application/json',
            'Accepts': 'application/json'
        },
        success: function(response) {
            refreshEncounters();
        }
    })
}

function showSpellTooltip(event, spellName) {
    if ($('#tooltip').is(":visible")) {
        return // Don't trigger a new popup inside the existing one
    }
    $('#tooltip').show();
    target = $(event.target);
    target.before($('#tooltip-sleeve'));
    bounds = event.target.getBoundingClientRect();
    offset = target.offset();
    // Set sleeve coordinates
    $('#tooltip-sleeve').css({left: offset.left+bounds.width, top: offset.top});
    if ((offset.top / $(window).height()) < 0.5) {
        $('#tooltip').css({top: bounds.height});
    } else {
        $('#tooltip').css({bottom: 0});
    }
    setContentAjax($('#tooltip'), `/tooltips/spells/${spellName}`);
    tooltipOffset = $('#tooltip').offset();
}

function hideSpellTooltip(event) {
    $('#tooltip').hide();
    console.log("Mouseleave")
    $('#content').append($('#tooltip-sleeve'));
}