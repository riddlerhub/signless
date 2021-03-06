function checkIfExists(e, t) {
    return !(void 0 === e || !e.hasOwnProperty(t))
}

function joinGame(e) {
    e.preventDefault();
    let t = document.getElementById("playerName").value;
    if ("" !== t) {
        $("#startGameButton").css("display", "block");
        let e = {
            action: actions.JOIN_GAME,
            payload: {
                playerName: t
            }
        };
        document.getElementById("playerNamePrompt").hidden = !0, playerNamePromptErr = "", GLOBAL_CLIENT_STATE.connectedPlayerName = t, socket.send(JSON.stringify(e))
    } else alert("Please enter a player name")
}

function playerNamePopUp(){
    t  = prompt('Please enter a Player Name');
    if (t != ""){
        $("#startGameButton").css("display", "block");
        let e = {
            action: actions.JOIN_GAME,
            payload: {
                playerName: t
            }
        };
        GLOBAL_CLIENT_STATE.connectedPlayerName = t, socket.send(JSON.stringify(e))
    }else{
        playerNamePopUp()
    }
}

function resetGame() {
    let e = {
        action: actions.RESET_GAME
    };
    socket.send(JSON.stringify(e))
}

function startGame() {
    let e = {
        action: actions.START_GAME
    };
    hideAll(), showButton("resetGameButton"), showButton("resetGameButton"), socket.send(JSON.stringify(e))
}

function suggestPreparations() {
    hideAll(), showSuggest()
}

function accusePreparations() {
    hideAll(), showAccuse()
}

function showTurnAccuse(e) {
    e.can_accuse[GLOBAL_CLIENT_STATE.connectedPlayerName] && showButton("accuseButton"), showButton("endTurnButton")
}

function showTurn(e) {
    e.can_accuse[GLOBAL_CLIENT_STATE.connectedPlayerName] && (showButton("suggestButton"), showButton("accuseButton")), showButton("endTurnButton")
}

function showSuggest() {
    showButton("suspectsList"), showButton("weaponsList"), showButton("submitSuggestion")
}

function showDisprove() {
    showButton("disproveCards"), showButton("disproveButton")
}

function showAccuse() {
    showButton("suspectsList"), showButton("weaponsList"), showButton("submitAccusation")
}

function suggest() {
    let e = {
        action: actions.SUGGEST,
        weapon: document.getElementById("weaponsList").value,
        suspect: document.getElementById("suspectsList").value,
        room: getRoomOfPlayer(GLOBAL_CLIENT_STATE.connectedPlayerName),
        locations: getPieceLocations()
    };
    hideAll(), socket.send(JSON.stringify(e))
}

function disprove() {
    let e = {
        action: actions.DISPROVE,
        disproveValue: document.getElementById("disproveCards").value
    };
    hideAll(), socket.send(JSON.stringify(e))
}

function accuse() {
    let e = {
        action: actions.ACCUSE,
        weapon: document.getElementById("weaponsList").value,
        suspect: document.getElementById("suspectsList").value,
        room: getRoomOfPlayer(GLOBAL_CLIENT_STATE.connectedPlayerName)
    };
    hideAll(), socket.send(JSON.stringify(e))
}

function endTurn() {
    let e = {
        action: actions.END_TURN,
        payload: {
            current_locations: getPieceLocations()
        }
    };
    hideAll(), socket.send(JSON.stringify(e))
}

function showButton(e) {
    document.getElementById(e).style.display = "block"
}

function hideButton(e) {
    $("#" + e).css("display", "none")
}

function hideAll() {
    hideButton("startGameButton"), hideButton("suggestButton"), hideButton("accuseButton"), hideButton("disproveButton"), hideButton("endTurnButton"), hideButton("weaponsList"), hideButton("suspectsList"), hideButton("submitSuggestion"), hideButton("submitAccusation"), hideButton("disproveCards"), hideButton("disproveButton")
}

function alertInBox(e) {
    let t = document.getElementById("alerts");
    t.innerHTML = e + "<br />" + t.innerHTML
}
socket.on("connect", () => {
    socket.emit(actions.CLIENT_CONNECTION, {
        data: "Client connected"
    })
}), socket.on("message", e => {
    let t = JSON.parse(e),
        n = t.gameState,
        o = GLOBAL_CLIENT_STATE.connectedPlayerName;
    switch (statusDiv = document.getElementById("status"), statusDiv.innerHTML = "In " + GLOBAL_CLIENT_STATE.connectedPlayerName + "'s client. Current turn number: " + n.turn + " Current player's turn: " + n.current_player, setCurrentCharacterTurn(n), t.responseToken) {
        case responses.PLAYER_JOINED_GAME:
            alert("New Player Joined");
            roomDiv = document.getElementById("room"), roomDiv.innerHTML = "";
            let e = n.players.map(e => "<li>" + e + "</li>");
            roomDiv.innerHTML += "<ul>";
            for (let t = 0; t < e.length; ++t) roomDiv.innerHTML += e[t];
            roomDiv.innerHTML += "</ul>", n.players.length >= 3 && showButton("startGameButton");
            break;
        case responses.PLAYER_ALREADY_JOINED:
            playerNamePrompt = document.getElementById("playerNamePrompt"), playerNamePromptErr = document.getElementById("playerNamePromptErr"), playerNamePrompt.hidden = !1, playerNamePromptErr.innerHTML = "Player with that name has already joined the game";
            break;
        case responses.MAXIMUM_PLAYER_REACHED:
            playerNamePrompt = document.getElementById("playerNamePrompt"), playerNamePromptErr = document.getElementById("playerNamePromptErr"), playerNamePrompt.hidden = !1, playerNamePromptErr.innerHTML = "Maximum number of players (6) for this game has been reached";
            break;
        case responses.CLEARED_GAME_STATE:
            location.reload();
            break;
        case responses.GAME_STARTED_STATE:
            if (hideAll(), initGamePiecesAndBoard(n), GLOBAL_CLIENT_STATE.connectedPlayerName === n.current_player && showTurn(n), checkIfExists(n.player_cards, o)) {
                cardsDiv = document.getElementById("cards");
                for (let e = 0; e < n.player_cards[GLOBAL_CLIENT_STATE.connectedPlayerName].length; e++) {
                    const t = n.player_cards[GLOBAL_CLIENT_STATE.connectedPlayerName][e];
                    assetLocations.hasOwnProperty(t) ? cardsDiv.innerHTML += "<button class='btn btn-primary card'><img src='" + assetLocations[t] + "' alt='" + assetLocations[t] + "' width='75' /></button>" : cardsDiv.innerHTML += t + " "
                }
            }
            break;
        case responses.SUGGEST_STATE:
            updateGameBoard(n), hideAll(), console.log("From the suggest state case: ", n), n.game_ended && alertInBox("Game has ended, please restart."), GLOBAL_CLIENT_STATE.connectedPlayerName === n.current_player && showTurn(n);
            break;
        case responses.PRE_DISPROVE:
            updateGameBoard(n), alertInBox(n.current_player + " suggested that " + n.current_suggestion.suspect + " killed the victim using the " + n.current_suggestion.weapon + " in " + n.current_suggestion.room);
        case responses.DISPROVE_STATE:
            if (hideAll(), alertInBox("It is " + n.disproving_player + "'s turn to disprove the suggestion using eligible cards."), n.disproving_player === GLOBAL_CLIENT_STATE.connectedPlayerName) {
                let e = document.getElementById("disproveCards");
                if (e.innerHTML = "", GLOBAL_CLIENT_STATE.connectedPlayerName in n.can_disprove)
                    for (let t = 0; t < n.can_disprove[GLOBAL_CLIENT_STATE.connectedPlayerName].length; t++) currentVal = n.can_disprove[GLOBAL_CLIENT_STATE.connectedPlayerName][t], e.innerHTML += '<option value="' + currentVal + '">' + currentVal + "</option>";
                else e.innerHTML += '<option value="novalue">No Cards</option>';
                showDisprove()
            }
            break;
        case responses.ACCUSE_STATE:
            hideAll(), "disproveFailed" === t.payload && alertInBox("There are no players with eligible cards to disprove the suggestion."), GLOBAL_CLIENT_STATE.connectedPlayerName === n.current_player && ("disproveFailed" !== t.payload && alertInBox(t.payload), showTurnAccuse(n));
            break;
        case responses.ACCUSE_SUCCESS:
            hideAll(), alertInBox(n.current_player + " accused " + n.accusation.suspect + " of the murder using " + n.accusation.weapon + " in the " + n.accusation.room), alertInBox(n.current_player + " has the right accusation. Please restart the game.");
            break;
        case responses.ACCUSE_FAILURE:
            hideAll(), alertInBox(n.current_player + " accused " + n.accusation.suspect + " of the murder using " + n.accusation.weapon + " in the " + n.accusation.room), alertInBox("You have the wrong accusation."), alertInBox(n.solution.suspect + " murdered the victim using " + n.solution.weapon + " in the " + n.solution.room), showButton("endTurnButton");
            break;
        default:
            console.log(t)
    }
})