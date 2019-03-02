class GameBoard{constructor(){this.canvas=document.getElementById("gamecanvas"),this.context=this.canvas.getContext("2d"),this.pieces={},this.characterAllowedToMove=null,this.associations=null}draw(e){this.imageObj=new Image,this.imageObj.onload=(()=>{this.context.drawImage(this.imageObj,0,0,this.imageObj.width,this.imageObj.height),this.pieces=e(this.context)}),this.imageObj.src="/static/assets/gameboard.png"}setAssociations(e){this.associations=e}getAssociations(){return this.associations}setAllowedToMove(e){this.characterAllowedToMove=e}getAllowedToMove(){return this.characterAllowedToMove}clear(){this.context.clearRect(0,0,this.canvas.width,this.canvas.height)}static onCanvasClick(e){let i=e.offsetX,t=e.offsetY;console.log("Clicked"," x:",i," y:",t)}}class Piece{constructor(e,i,t,s,o,n){this.width=e,this.height=i,this.color=t,this.x=s,this.y=o,this.indexX=s,this.indexY=o,this.context=n}draw(){let e=new Image;e.onload=(()=>{this.context.drawImage(e,this.x,this.y,this.width,this.height)}),e.src={violet:"/static/assets/pieces/purple.png",white:"/static/assets/pieces/white.png",blue:"/static/assets/pieces/blue.png",green:"/static/assets/pieces/green.png",red:"/static/assets/pieces/red.png",yellow:"/static/assets/pieces/yellow.png"}[this.color]}getColor(){return this.color}getPosition(){return{x:this.x,y:this.y,indexX:this.indexX,indexY:this.indexY}}setDirectly(e,i){this.x=e,this.y=i}setIndices(e,i){this.indexX=e,this.indexY=i}newPos(e,i){let t=this.indexX,s=this.indexY;0==t&&0==s&&-1===i&&(this.x=validPositions[4][4].x,this.y=validPositions[4][4].y,this.indexX=4,this.indexY=4),4===t&&4===s&&1===i&&(this.x=validPositions[0][0].x,this.y=validPositions[0][0].y,this.indexX=0,this.indexY=0),0===t&&4===s&&1===i&&(this.x=validPositions[4][0].x,this.y=validPositions[4][0].y,this.indexX=4,this.indexY=0),4===t&&0===s&&-1===i&&(this.x=validPositions[0][4].x,this.y=validPositions[0][4].y,this.indexX=0,this.indexY=4),1==e&&0==i&&(this.x=validPositions[t+1][s].x,this.y=validPositions[t+1][s].y,this.indexX=t+1,this.indexY=s),-1==e&&0==i&&(this.x=validPositions[t-1][s].x,this.y=validPositions[t-1][s].y,this.indexX=t-1,this.indexY=s),0!=e||1!=i||4===t&&4===s||0===t&&4===s||(this.x=validPositions[t][s+1].x,this.y=validPositions[t][s+1].y,this.indexX=t,this.indexY=s+1),0!=e||-1!=i||0===t&&0===s||4===t&&0===s||(this.x=validPositions[t][s-1].x,this.y=validPositions[t][s-1].y,this.indexX=t,this.indexY=s-1)}}let myGameBoard=new GameBoard,initPiece=(e,i,t,s)=>{if(t.hasOwnProperty(e)){let o=t[e].x,n=t[e].y;myPieces[e]=new Piece(35,35,i,o,n,s),myPieces[e].draw()}},updateRoomToShowAssociations=()=>{let e=document.getElementById("room");e.innerHTML="",e.innerHTML+="<ul>";let i=myGameBoard.getAssociations();for(var t in i){let s=i[t];if(null!==myPieces[s]){let i=myPieces[s].getColor(),o="";t===GLOBAL_CLIENT_STATE.connectedPlayerName&&(o+="(You)"),"yellow"!==i&&"white"!==i?e.innerHTML+="<li style='color:"+i+";'><strong>"+t+"</strong>, "+s+o:"yellow"===i?e.innerHTML+="<li style='color:gold;'><strong>"+t+"</strong>, "+s+o:"white"===i&&(e.innerHTML+="<li style='color:#888;'><strong>"+t+"</strong>, "+s+o),e.innerHTML+="</li>"}}e.innerHTML+="</ul>"},initPieces=(e,i)=>(initPiece("plum","violet",i,e),initPiece("white","white",i,e),initPiece("peacock","blue",i,e),initPiece("green","green",i,e),initPiece("scarlet","red",i,e),initPiece("mustard","yellow",i,e),updateRoomToShowAssociations(),myPieces),drawPieces=e=>{myPieces.plum.draw(),myPieces.white.draw(),myPieces.peacock.draw(),myPieces.green.draw(),myPieces.scarlet.draw(),myPieces.mustard.draw()};function moveIfValid(e,i,t){0===e.indexX&&0===e.indexY&&-1===t?(e.newPos(i,t),myGameBoard.clear(),myGameBoard.draw(drawPieces)):4===e.indexX&&0===e.indexY&&-1===t?(e.newPos(i,t),myGameBoard.clear(),myGameBoard.draw(drawPieces)):4===e.indexX&&4===e.indexY&&1===t?(e.newPos(i,t),myGameBoard.clear(),myGameBoard.draw(drawPieces)):0===e.indexX&&4===e.indexY&&1===t?(e.newPos(i,t),myGameBoard.clear(),myGameBoard.draw(drawPieces)):e.indexX+i>4||e.indexY+t>4||e.indexX+i<0||e.indexY+t<0?alert("Can't move there"):-1!==validPositions[e.indexX+i][e.indexY+t].x?(e.newPos(i,t),myGameBoard.clear(),myGameBoard.draw(drawPieces)):alert("Can't move there")}function handleKeyDown(e){e=e||window.event;let i=myGameBoard.getAssociations(),t=GLOBAL_CLIENT_STATE.connectedPlayerName,s=!1,o=null;null!==i&&t.length>0&&(o=i[t],myGameBoard.getAllowedToMove()===o&&(s=!0));let n=!1;if(""!==o&&null!==o&&(currentConnectedPiece=myPieces[o],myPieces[o].x===startSpaces[o].x&&(n=!0)),n&&s){let e=nextMoveAfterStart[o].pos.x,i=nextMoveAfterStart[o].pos.y,t=nextMoveAfterStart[o].indicies[0],s=nextMoveAfterStart[o].indicies[1];myPieces[o].setDirectly(e,i),myPieces[o].setIndices(t,s),myGameBoard.clear(),myGameBoard.draw(drawPieces)}else"38"==e.keyCode&&s?moveIfValid(currentConnectedPiece,-1,0):"40"==e.keyCode&&s?moveIfValid(currentConnectedPiece,1,0):"37"==e.keyCode&&s?moveIfValid(currentConnectedPiece,0,-1):"39"==e.keyCode&&s&&moveIfValid(currentConnectedPiece,0,1)}function updateDomGivenRoomsOfPlayers(e,i){let t=document.getElementById("playerLocationsInner");for(var s in t.innerHTML="",e)for(var o in e[s])t.innerHTML+="<div class='location'><strong>"+o+": </strong>"+e[s][o]+"</div>";for(var s in i)for(var o in i[s])t.innerHTML+="<div class='location'><strong>"+o+": </strong>"+i[s][o]+"</div>"}function setRoomsOfPlayers(e){let i=[];if(e.hasOwnProperty("players")){let t=e.players.map(e=>({[e]:getRoomOfPlayer(e)}));if(GLOBAL_CLIENT_STATE.playerRoomLocations=t,e.hasOwnProperty("movement_info")&&e.movement_info.hasOwnProperty("unassigned_characters")){i=e.movement_info.unassigned_characters.map(e=>({[e]:getRoomOfCharacter(e)}))}updateDomGivenRoomsOfPlayers(t,i)}}function initGamePiecesAndBoard(e){if(e.hasOwnProperty("movement_info")&&e.movement_info.hasOwnProperty("current_locations")){let i=e.movement_info.current_locations;myGameBoard.draw(e=>initPieces(e,i)),setCurrentCharacterTurn(e),setRoomsOfPlayers(e)}}function setCurrentCharacterTurn(e){if(e.hasOwnProperty("movement_info")&&e.movement_info.hasOwnProperty("associations")&&e.current_player.length>0){let i=e.movement_info.associations;null===myGameBoard.getAssociations()&&myGameBoard.setAssociations(i);let t=i[e.current_player];myGameBoard.setAllowedToMove(t)}}function getRoomOfCharacter(e){if(null!==myPieces[e]){let i=myPieces[e].getPosition(),t=i.indexX+","+i.indexY;if(roomMappingIndexFirst.hasOwnProperty(t))return roomMappingIndexFirst[t]}return"hallway"}function getRoomOfPlayer(e){return getRoomOfCharacter(myGameBoard.getAssociations()[e])}document.onkeydown=handleKeyDown;