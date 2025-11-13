function nextCombatant() {
    cycleCombatants(1);
}

function prevCombatant() {
    cycleCombatants(-1);
}

function cycleCombatants(step) {
    combatants = $("table#turntracker").children().eq(0).children();
    next = $("tr.selected");
    current = $("tr.selected");

    for (let i = 0; i < Math.abs(step); i++) {
        nRetries = 0; // Track how many times we've moved to another entry because of a dead person
        do {
            nRetries += 1;
            if (step < 0) {
                next = next.prev();
                // Loop to bottom if needed
                if (next.attr("id") == "tracker-header") {
                    next = $("table#turntracker").children().eq(0).children().last();
                }
            } else {
                next = next.next();
                // Loop back to top if needed
                if (next.length == 0) {
                    next = $("table#turntracker").children().eq(0).children().eq(1);
                }
            }
        } while (nRetries < combatants.length && (next.data("type") == "npc" && next.data("dead") == true))
    }
    next.addClass("selected");
    current.removeClass("selected");
}


function sortInitiativeTable() {
    table = $('#turntracker');
    rows = table.find('tr:gt(0)').toArray().sort(compareRows).reverse();
    for (i = 0; i < rows.length; i++) {
        table.append(rows[i]);
    }
}

function compareRows(r1, r2) {
    v1 = getInitiative(r1), v2 = getInitiative(r2);
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
    refreshLoot();
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

    monster = self.closest('tr').data();
    if ((hp <= 0 && monster.dead == false) || (hp > 0 && monster.dead == true)) {
        monster.dead = !monster.dead;
        refreshLoot();
        refreshXP();
        if (monster.dead) {
            addStatus(self, 'incapacitated', prepend=true);
        } else {
            removeStatus(self, 'incapacitated');
        }
    }
}

function addMonster(monsterId, params={}) {
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
            statusCell = $(`<td style="vertical-align: middle; width: 140px;"></td>`);
            statusCell.html(getAddStatusWidget());
            trow.append(statusCell);
            trow.data("id", monsterId);
            trow.data("type", "npc");
            trow.data("initMod", data.initMod);
            trow.data("xp", data.xp);
            trow.data("dead", data.dead);
            trow.data("loot", data.loot);
            trow.data('hasXp', data.flag_xp);
            trow.data('hasLoot', data.flag_loot);
            trow.data('statuses', data.statuses);

            // Some functions might provide some overrides we should use
            if ('hasXp' in params) {
                trow.data('hasXp', params.hasXp);
            }
            if ('hasLoot' in params) {
                trow.data('hasLoot', params.hasLoot);
            }

            trow.click(function(event) { updateStatblockTarget(event); });
            trow.on('contextmenu', trackerContextMenu);

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
                trow.append(`<td style="vertical-align: middle">${data.pp}</td>`);
                statusCell = $(`<td style="vertical-align: middle; width: 140px;"></td>`);
                statusCell.html(getAddStatusWidget());
                trow.append(statusCell);
                
                trow.data("id", `${playerName}.player`);
                trow.data("statuses", []);

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
                // deleteRow(event);
                $(this).find(".remove-btn").trigger("click");
                updateAddPlayerButtons();
            }
        });
    }
}

function setContentAjax(target, url) {
    // Set the HTML content of an element as the response of a GET request to a URL
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
    $.ajax({
        url: `/statblock/${monsterId}`,
        method: 'GET',
        success: function(response) {
            $('#statblock-div').html(response);
        }
    })
}

function rollInitiative() {
    tbody = $("#turntracker").children().eq(0);
    tbody.children().each(function() {
        rollInitiativeSingle(this);
    })
}

function rollInitiativeSingle(elem) {
    data = $(elem).data();
    if (data.type == "npc") {
        initMod = parseInt(data.initMod);
        initCell = $(elem).children().eq(4);
        initCell.text(1 + Math.floor(Math.random()*20) + initMod);
    }
}

function refreshXP() {
    // Update the XP totals at the bottom of the tracker
    tbody = $("#turntracker").children().eq(0);
    xp = 0;
    total_xp = 0;
    tbody.children().each(function() {
        data = $(this).data();
        if (data.type == "npc" && data.hasXp) {
            if (data.dead == true) {
                xp += data.xp;
            }
            total_xp += data.xp;
        }
    });
    $("#xp-to-award").text(xp);
    $("#xp-total").text(total_xp);
}

function refreshLoot() {
    // Update the loot totals at the bottom of the tracker
    tbody = $("#turntracker").children().eq(0);
    total = 0; // Total loot in CP
    items = [];
    tbody.children().each(function() {
        data = $(this).data();
        if (data.type == 'npc' && data.dead == true && data.hasLoot) {
            total += data.loot.total;
            items = items.concat(data.loot.items);
        }
    });

    cp = total % 10;
    sp = Math.floor((total % 100) / 10);
    gp = Math.floor((total % 1000) / 100);
    pp = Math.floor(total / 1000);

    loot_str = "";
    if (cp > 0) { loot_str += `${cp} CP, `; }
    if (sp > 0) { loot_str += `${sp} SP, `; }
    if (gp > 0) { loot_str += `${gp} GP, `; }
    if (pp > 0) { loot_str += `${pp} PP, `; }
    loot_str = loot_str.slice(0, -2);
    $("#loot-total").text(loot_str);

    $("#loot-items").empty();
    $(items).each(function() {
        node = $('<li>')
        node.append($('<div>').html(this.html).text());
        $("#loot-items").append(node);
    });

    $.ajax({
        url: `/lootblock`,
        data: JSON.stringify({items: items, coinage: total}),
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accepts': 'application/json'
        },
        success: function(response) {
            $('#lootblock').html(response)
        }
    })
}

function refreshStatus(tr) {
    if (!tr.is('tr')) {
        tr = tr.closest('tr');
    }

    // Get unique statuses
    statuses = [...new Set(tr.data('statuses'))]

    statusCell = tr.children().eq(6);
    if (statuses.length == 0) {
        statusCell.html(getAddStatusWidget());
    } else {
        statusCell.empty();
        height = 40;
        if (statuses.length > 3) {
            height = 20;
        }
        $.each(statuses, function(_, status) {
            console.log(status);
            image = $(`<img src="inittracker/static/status-markers/${status}.png" style="height:${height}px" alt="blinded">`);
            image.click(function(event) {
                removeStatus(event.target, status);
            })
            statusCell.append(image);
        });
    }
}

function addStatus(elem, status, prepend=false) {
    // Get root table row
    tr = $(elem);
    if (!tr.is('tr')) {
        tr = tr.closest('tr');
    }

    // Add status
    statuses = tr.data("statuses");
    if (prepend) {
        statuses = [status, ...statuses];
    } else {
        statuses.append(status);
    }
    tr.data("statuses", statuses);
    refreshStatus(tr);
}

function removeStatus(elem, status) {
    // Get root table row
    tr = $(elem);
    if (!tr.is('tr')) {
        tr = tr.closest('tr');
    }

    // Remove status
    oldStatuses = tr.data("statuses");
    newStatuses = $.grep(oldStatuses, function(val) {
        return val !== status;
    })
    tr.data("statuses", newStatuses);
    refreshStatus(tr);
}

function getAddStatusWidget() {
    elem = $('<span class="w3-button w3-white w3-ripple">Add Status</span>');
    elem.click(function (event) {
        tr = $(event.target);
        if (!tr.is('tr')) {
            tr = tr.closest('tr');
        }
        tr.data('statuses', ['blinded', 'bleeding-out', 'blessed']);
        refreshStatus(tr);
    })
    return elem
}

function showTab(elem) {
    $("#tab-pages").children().each(function() {
        if ($(this).is(elem)) {
            $(this).show();
        } else {
            $(this).hide();
        }
    })
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

function listEncounters() {
    // Fetches the encounter list from localStorage.
    savedEncounters = localStorage.getItem('savedEncounters');
    if (savedEncounters === null || Object.keys(JSON.parse(savedEncounters)).length == 0) {
        console.info("No saved encounters found; adding defaults")
        return {
            'Mines of Moria': {
                'monsters': [
                    {'id': 'Balor-MM', 'hasLoot': false},
                    {'id': 'Goblin-MM'},
                    {'id': 'Goblin-MM'},
                    {'id': 'Hobgoblin-MM'}
                ],
                'title': 'Mines of Moria',
                'desc': 'The mines are home to goblins, and something worse...'
            },
            'March on Isengard': {
                'monsters': [
                    {'id': 'Treant-MM', 'hasLoot': false},
                    {'id': 'Treant-MM', 'hasLoot': false},
                    {'id': 'Twig Blight-MM', 'hasLoot': false},
                    {'id': 'Twig Blight-MM', 'hasLoot': false},
                    {'id': 'Twig Blight-MM', 'hasLoot': false},
                    {'id': 'Archmage-MM'}
                ],
                'title': 'March on Isengard',
                'desc': 'The ents move against Saruman the White'
            }
        }
    }
    return JSON.parse(savedEncounters);
}

function updateEncounters(encounters) {
    // Updates the encounter list saved in localStorage.
    localStorage.setItem('savedEncounters', JSON.stringify(encounters));
}

function refreshEncounters() {
    // Get encounter info
    encounters = listEncounters();

    numEncounters = Object.keys(encounters).length;
    console.log(`Found ${numEncounters} saved encounters in localStorage.`);
    if (numEncounters > 0) {
        // Remove default encounters
        $('.saved-encounter-list').empty();
    } else {
        console.log('No encounters loaded; using default placeholders.')
    }

    $.each(encounters, function(eid, enc) {
        item = $('<div class="saved-encounter-list-item"></div>');
        item.data("monsters", enc.monsters);
        item.data("encounter", enc);
        item.data("id", eid);
        item.dblclick(function() { loadEncounter(this); });
        item.append($(`<div>${enc.title}</div>`));
        item.append($(`<div>${enc.desc}<div>`));
        closeButton = ($(`<div class="w3-button w3-ripple">&times</div>`));
        closeButton.click(function(event) {
            deleteEncounter(event);
        })
        item.append(closeButton);
        $('.saved-encounter-list').append(item);
    });
}

function deleteEncounter(event) {
    self = $(event.target);
    encounterItem = self;
    if (!self.hasClass('saved-encounter-list-item')) {
        encounterItem = self.closest(".saved-encounter-list-item");
    }
    encounterId = $(encounterItem).data("id");
    console.log($(encounterItem).data("encounter"));
    console.log(`Removing encounter '${encounterId}'`);

    savedEncounters = listEncounters();
    delete savedEncounters[encounterId];
    updateEncounters(savedEncounters);
    refreshEncounters();
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
    $($(encounterItem).data("monsters")).each(function (_, monster) {
        addMonster(monster.id, monster);
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

    // Copy monster data from the initative tracker
    $('#turntracker tr:gt(0)').each(function () {
        data = $(this).data();
        if (data.type != 'npc') {
            return
        }
        entry = {
            'id': data.id,
            'hasXp': data.hasXp,
            'hasLoot': data.hasLoot,
        }
        monsters.push(entry);
    })

    encounter = {
        "title": encounterTitle,
        "desc": encounterDesc,
        "monsters": monsters
    }

    // Update Encounter List
    encounters = listEncounters();
    numEncounters = Object.keys(encounters).length;

    encounterId = encounterTitle;
    encounters[encounterId] = encounter;
    updateEncounters(encounters);

    if (Object.keys(encounters).length == numEncounters) {
        console.log(`Updated encounter: '${encounterId}'`);
    } else {
        console.log(`Saved new encounter: '${encounterId}'`);
    }

    // Refresh encounter list UI
    refreshEncounters();
}

function showTooltip(event) {
    // Show a tooltip over/under the element which triggered the event
    if ($('#tooltip').is(":visible")) {
        return // Don't trigger a new popup inside the existing one
    }
    $('#tooltip').show();
    target = $(event.target);
    target.append($('#tooltip-sleeve'));
    bounds = event.target.getBoundingClientRect();
    offset = target.offset();
    // Set sleeve coordinates
    $('#tooltip-sleeve').css({left: offset.left+bounds.width, top: offset.top});
    if ((offset.top / $(window).height()) < 0.5) {
        $('#tooltip').css({top: bounds.height, bottom: ""});
    } else {
        $('#tooltip').css({bottom: 0, top: ""});
    }
    if ((offset.left / $(window).width()) < 0.5) {
        $('#tooltip').css({left: bounds.width, right: ""});
    } else {
        $('#tooltip').css({right: 0, left: ""});
    }
}

function hideTooltip(event) {
    // Don't trigger if triggered from inside a tooltip
    if ($(event.target).parents('#tooltip').length) {
        return;
    }
    // Stop displaying a tooltip
    $('#tooltip').hide();
    $('#content').append($('#tooltip-sleeve'));
}

function showNewTooltip(event, url) {
    // Displays the tooltip and sets it's content to the value returned by the URL
    
    // Don't do anythign if this function is triggered from inside the tooltip
    if ($(event.target).parents('#tooltip').length) {
        return;
    }
    showTooltip(event);
    setContentAjax($('#tooltip'), url);
}

function trackerContextMenu(event) {
    // Override default browser context menu
    event.preventDefault();

    // Get references to objects of interest
    tr = $(event.target).closest("tr");
    cm = $("#contextmenu");
    checkXp = $('#tracker-context-has-xp');
    checkLoot = $('#tracker-context-has-loot');
    rerollInitBtn = $('#tracker-context-reroll-init');
    deleteBtn = $('#tracker-context-delete-item');

    // Update checkboxe states
    checkXp.prop('checked', tr.data('hasXp')); //tr.data('hasXp');
    checkLoot.prop('checked', tr.data('hasLoot'));

    // Add Event Listeners
    checkXp.off('change');
    checkXp.change(function() {
        if (tr.data('type') == 'npc') {
            tr.data('hasXp', checkXp.is(':checked'));
            refreshXP();
        }
    });

    checkLoot.off('change');
    checkLoot.change(function() {
        if (tr.data('type') == 'npc') {
            tr.data('hasLoot', checkLoot.is(':checked'));
            refreshLoot();
        }
    });

    rerollInitBtn.off('click');
    rerollInitBtn.click(function() {
        rollInitiativeSingle(tr);
    })

    deleteBtn.off('click');
    deleteBtn.click(function() {
        deleteRow(event);
        cm.hide();
    })

    cm.css({left: event.pageX, top: event.pageY});
    cm.show();
}