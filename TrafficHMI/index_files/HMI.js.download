
//'use strict';
var canvas = document.getElementById("myCanvas");
var ctx = canvas.getContext("2d");
var BOARDWIDTH = 800, BOARDHEIGHT = 800;
var CARDWIDTH = 72;
var CARDHEIGHT = 100;
var DeckofCardsSprite;
var playerProfileSprites = new Array(4);
var starSprite;
var cardImage = new Image();
cardImage.src = "_img/New_deck4.gif";
var starImage = new Image();
starImage.src = "_img/star_small.png";
var profileImage = new Array(4);
profileImage[0] = new Image();
profileImage[0].src = "_img/mario.png";
profileImage[1] = new Image();
profileImage[1].src = "_img/luigi.png";
profileImage[2] = new Image();
profileImage[2].src = "_img/wario.png";
profileImage[3] = new Image();
profileImage[3].src = "_img/yoshi.png";
var players = new Array(4);
var backOfCardsSprite;
var incremeneter = 0;
var requestedAnimate = false;
var curPlayerIndex = -1; //the person who's turn it is to play a card. starts with owner of 2 of clubs
var gameRound = -1;
var gameState = 4; //1 - players passing cards, 2 round is in play, 3 round is over, 4 game is over
var cardsInPlay = []; //an array of cards that are played in the middle of the board

var firstTrickOfRound = true; //this is the first trick of the round
var heartsBroken = false;
var originalSuit = -1;
var animationInProgress = false;
var MAXANIMATIONFRAMES = 30;
var requestTrickCleared = false;
var requestTrickResultsCheck = false;
var trickWinner; //the player that won the trick
var maxSCORE = 100;
var requestNextPlayerPlays = false;

var COMMANDS = {PASSCARDS: {value: 1},
    NOTIFYNEWROUND: {value: 2},
    PROCESSRESULTS: {value: 3},
    NOTIFYNEXTPLAYERTOPLAY: {value: 4},
    CLEARTRICK: {value: 5}};
var SUIT = {HEARTS: {value: 2},
    DIAMONDS: {value: 0},
    CLUBS: {value: 1},
    SPADES: {value: 3}};
var AVATARWIDTH = 100;
var AVATARHEIGHT = 100;

function cardObject(suit, value) {
    /*a card from the deck
     0 = HEARTS,        1 = DIAMONDS,        2 = CLUBS,        3 = SPADES
     value is between 0 and 12, 0 represents a 2, 12 represent Ace */
    this.suit = suit;
    this.value = value;
    this.xPos = 0, this.yPos = 0; //position of the card on the board
    this.isSelected = false;
    this.newX = 0;  //variables that keep track of the new location the card goes when animated
    this.newY = 0;
    this.player = null; //the player that owns this card
    this.currentlyAnimating = false;
    this.numFramesToAnimate = 0;
    this.cardFaceVisible = false;

    this.getDetails = function () {
        var msg, suitstring;
        switch (value) {
            case 9:
                msg = "Jack of ";
                break;
            case 10:
                msg = "Queen of ";
                break;
            case 11:
                msg = "King of ";
                break;
            case 12:
                msg = "Ace of ";
                break;
            default:
                msg = value + 2 + " of ";
        }
        if (suit === 0) {
            suitstring = 'Hearts';
        }
        if (suit === 1) {
            suitstring = 'Diamonds';
        }
        if (suit === 2) {
            suitstring = 'Clubs';
        }
        if (suit === 3) {
            suitstring = 'Spades';
        }
        return msg + suitstring;
    };
    this.toggleSelected = function () {
        //toggles whether or not the card is selected. if it is then change the way it looks
        this.isSelected = !this.isSelected;
        console.log(this.getDetails() + " is selected: " + this.isSelected);
    };
    this.setupForAnimation = function (newXPos, newYPos, requestedNumFrames) {
        //sets thew newX, newY, and desired number of Frames for the card
        this.newX = newXPos;
        this.newY = newYPos;
        this.numFramesToAnimate = requestedNumFrames;
        this.currentlyAnimating = true;
    };
    this.translate = function () {
        //translate in X and Y based on the number of frames remaining and the newX and newY. returns FALSE when done with animation
        if (this.currentlyAnimating === false) {
            return false;
        }
        var distX = this.newX - this.xPos;
        var distY = this.newY - this.yPos;
        this.xPos += distX / this.numFramesToAnimate;
        this.yPos += distY / this.numFramesToAnimate;
        this.numFramesToAnimate--;
        if (this.numFramesToAnimate === 0) {
            this.currentlyAnimating = false;
            return false;
        }
        return true;
    };

}
function player(name, score, hand, index, avatarXPos, avatarYPos, stockPileX, stockPileY, isComputer) {
    this.name = name;
    this.score = score;
    this.hand = hand;
    this.numSelectedCards = 0;
    this.playerIndex = index;
    this.cardsWon = []; //the cards won during this hand (hearts and Q of spades only)
    this.avatarXPos = avatarXPos;
    this.avatarYPos = avatarYPos;
    this.stockPileX = stockPileX;
    this.stockPileY = stockPileY; //where to store the players stash of cards collected
    this.isComputer = isComputer;

    this.removeCardFromHand = function (card) {
        //removes a given card from the hand Array
        var cardIndex = this.hand.indexOf(card);
        if (cardIndex === -1) {
            return false;
        } else {
            var cardRemoved = this.hand.splice(cardIndex, 1).pop();
            console.log(cardRemoved.getDetails() + " was removed from " + name + " 's hand.");
            return cardRemoved;
        }

    };
    this.hasSuitInHand = function (suit) {
        //determines if the player has a specific suit in their hand (0-3)
        //if it does, return true
        for (var x = 0; x < this.hand.length; x++) {
            if (this.hand[x].suit === suit) {
                return true;
            }
        }
        return false;
    };
    this.highestCardOfSuit = function (suit){
        var card;
        for (var x = 0; x < this.hand.length; x++) {
            if (this.hand[x].suit === suit) {
                if(card === undefined){card = this.hand[x];}
                else if(this.hand[x].value > card.value){
                    card = this.hand[x];
                }
            }
        }
        if(card === undefined){
            return false;
        }else{
            return card;
        }
    };
    this.hasCard = function (suit, value){
        for (var x = 0; x < this.hand.length; x++) {
            if (this.hand[x].suit === suit && this.hand[x].value === value) {
                return this.hand[x];
            }
        }
        return false;
    };
    this.hasOnlyHearts = function () {
        //determines if the player has any suit other than HEARTS
        //if it does, return true
        for (var x = 0; x < this.hand.length; x++) {
            if (this.hand[x].suit === SUIT.DIAMONDS.value ||
                    this.hand[x].suit === SUIT.CLUBS.value ||
                    this.hand[x].suit === SUIT.SPADES.value)
            {
                return false;
            }
        }
        return true;
    };
    this.cardsOfSuit = function (suit){
        //returns all cards of a specific suit in an array
        var cards = [];
         for (var x = 0; x < this.hand.length; x++) {
             if (this.hand[x].suit === suit){
                 cards.push(this.hand[x]);
             }
         }
         return cards;
    };
}
function updateScoreBoard() {
    document.getElementById('player0Menu').innerHTML = players[0].name + ": " + players[0].score + " points";
    document.getElementById('player1Menu').innerHTML = players[1].name + ": " + players[1].score + " points";
    document.getElementById('player2Menu').innerHTML = players[2].name + ": " + players[2].score + " points";
    document.getElementById('player3Menu').innerHTML = players[3].name + ": " + players[3].score + " points";
    
    //update the on screen talliers
            var msg = "Cards Won:<br>";
            for (i = 0; i < players.length; i++) {
                msg += players[i].name;
                for (x = 0; x < players[i].cardsWon.length; x++) {
                    if (players[i].cardsWon[x].suit === SUIT.HEARTS.value) {
                        msg += (players[i].cardsWon[x].value + 2) + "H ";
                    } else {
                        msg += (players[i].cardsWon[x].value + 2) + "Q ";
                    }
                }
                msg += '<br>';
            }
            console.log(msg);
            document.getElementById('cardsWonMenu').innerHTML = msg;
}
function clearCardsWon(){
    //clears the cards won that each player has between rounds
    players.forEach(function (gPlayer, index) {
        gPlayer.cardsWon = [];
    });
}
function initializeVariables() {
    players[0] = new player('Mario', 0, [], 0, BOARDWIDTH / 2 - AVATARWIDTH / 2, BOARDHEIGHT - CARDHEIGHT - AVATARWIDTH,
            BOARDWIDTH / 2, BOARDHEIGHT + CARDHEIGHT * 2,false);
    players[1] = new player('Luigi', 0, [], 1, CARDWIDTH, BOARDHEIGHT / 2 - AVATARWIDTH / 2,
            -CARDWIDTH * 2, BOARDHEIGHT / 2, true);
    players[2] = new player('Wario', 0, [], 2, BOARDWIDTH / 2 - AVATARWIDTH / 2, CARDHEIGHT,
            BOARDWIDTH / 2, -CARDHEIGHT * 2, true);
    players[3] = new player('Yoshi', 0, [], 3, BOARDWIDTH - CARDWIDTH - AVATARWIDTH, BOARDHEIGHT / 2 - AVATARWIDTH / 2,
            BOARDWIDTH + CARDWIDTH * 2, BOARDHEIGHT / 2, true);

    gameRound = 1;
    gameState = 1;
    updateScoreBoard();
}
function createSprites() {
    DeckofCardsSprite = new Array(4);
    for (i = 0; i < 4; i++) {
        DeckofCardsSprite[i] = new Array(13);
    }
    for (x = 0; x < DeckofCardsSprite.length; x++) {
        for (y = 0; y < DeckofCardsSprite[x].length; y++) {
            //create the sprites for each of these cards
            DeckofCardsSprite[x][y] = sprite({
                context: ctx,
                width: CARDWIDTH,
                height: CARDHEIGHT,
                image: cardImage,
                xOffset: CARDWIDTH * y,
                yOffset: CARDHEIGHT * x
            });
        }
    }

    for (var x = 0; x < playerProfileSprites.length; x++) {
        playerProfileSprites[x] = sprite({
            context: ctx,
            width: 100,
            height: 100,
            image: profileImage[x],
            xOffset: 0,
            yOffset: 0
        });
    }

    backOfCardsSprite = sprite({
        context: ctx,
        width: CARDWIDTH,
        height: CARDHEIGHT,
        image: cardImage,
        xOffset: CARDWIDTH * 4,
        yOffset: CARDHEIGHT * 4
    });

    starSprite = sprite({
        context: ctx,
        width: 25,
        height: 25,
        image: starImage,
        xOffset: 0,
        yOffset: 0
    });


}
function sprite(options) {

    var that = {};
    that.context = options.context;
    that.width = options.width;
    that.height = options.height;
    that.image = options.image;
    that.xOffset = options.xOffset;
    that.yOffset = options.yOffset;
    that.render = function (posX, posY) {
        // Clear the canvas
        that.context.clearRect(0, 0, that.width, that.height);
        // Draw the animation
        that.context.drawImage(
                that.image,
                that.xOffset,
                that.yOffset,
                that.width,
                that.height,
                posX,
                posY,
                that.width,
                that.height);
    };
    return that;
}
function sortCards() {
    for (var i = 0; i < players.length; i++) {
        players[i].hand.sort(function (a, b) {
            return ((a.suit * 13 + a.value) - (b.suit * 13 + b.value));
        });
    }
}
function updateCardPositionOnBoard() {
    //updates the card position on the board when the cards have just been dealt or are getting transferred
    var xPos, yPos;
    for (i = 0; i < players.length; i++) {
        handLength = players[i].hand.length;
        for (g = 0; g < handLength; g++) {
            switch (i) {
                case 0: //player 0
                    xOffset = (BOARDWIDTH - (13 * CARDWIDTH / 3 + CARDWIDTH / 3)) / 2;
                    yOffset = 700;
                    xPos = xOffset + (g * CARDWIDTH / 3);
                    yPos = yOffset;
                    break;
                case 1: //player 1
                    xOffset = 0;
                    yOffset = yOffset = (BOARDHEIGHT - (13 * CARDHEIGHT / 3 + CARDHEIGHT / 2)) / 2;
                    xPos = xOffset;
                    yPos = yOffset + (CARDHEIGHT / 3) * g;
                    break;
                case 2: //player 2
                    xOffset = (BOARDWIDTH - (13 * CARDWIDTH / 3 + CARDWIDTH / 3)) / 2;
                    yOffset = 0;
                    xPos = xOffset + (g * CARDWIDTH / 3);
                    yPos = yOffset;
                    break;
                case 3: //player 3
                    xOffset = BOARDWIDTH - CARDWIDTH;
                    yOffset = (BOARDHEIGHT - (13 * CARDHEIGHT / 3 + CARDHEIGHT / 2)) / 2;
                    xPos = xOffset;
                    yPos = yOffset + (CARDHEIGHT / 3) * g;
                    break;
            }
            var card = players[i].hand[g];
            card.xPos = xPos;
            card.yPos = yPos;
        }
    }
}
function shuffleAndDeal() {
    //generates a deck of cards, shuffles and issues to the players
    var Deck = new Array(52);
    for (i = 0; i < 4; i++) {
        for (j = 0; j < 13; j++) {
            Deck[13 * i + j] = new cardObject(i, j);
        }
    }
    //clear the players hands
    players[0].hand = new Array();
    players[1].hand = new Array();
    players[2].hand = new Array();
    players[3].hand = new Array();

    for (g = 0; g < 4; g++) {
        for (i = 0; i < 13; i++) {
            var randIndex = Math.floor(Math.random() * Deck.length);
            var card = Deck.splice(randIndex, 1).pop();
            if(g === 0){card.cardFaceVisible = true;}
            players[g].hand.push(card);
            card.player = players[g];

        }
    }
    //sort the cards before handing to the people
    sortCards();
    //initialize the cards location on the board
    updateCardPositionOnBoard();

}
function drawTheBoard() {
    /*this function draws the board at the start of the game*/
    canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);

    //draw the player sprites
    players.forEach(function (gPlayer, index) {
        playerProfileSprites[index].render(gPlayer.avatarXPos, gPlayer.avatarYPos);
    });

    var card;
    for (i = 0; i < players.length; i++) {
        for (g = 0; g < players[i].hand.length; g++) {
            card = players[i].hand[g];
            //if card is not selected, then just draw the card. if it is selected, draw it offset to signal it is selected
            var xOffset = 0;
            var yOffset = 0;
            if (card.isSelected) {
                //change the offset based on who the player is
                switch (i) {
                    case 0:
                        xOffset = 0; yOffset = -25;
                        break;
                    case 1:
                        xOffset = 25;
                        break;
                    case 2:
                        yOffset = 25;
                        break;
                    case 3:
                        xOffset = -25;
                        break;
                }
            }
            //player's hand is always visible
            //if(card.cardFaceVisible){
            if(i ===0){
                DeckofCardsSprite[card.suit][card.value].render(card.xPos + xOffset, card.yPos + yOffset);
            }else{
                backOfCardsSprite.render(card.xPos+xOffset,card.yPos+yOffset);
            }
            }
        }

        

    for (i = 0; i < cardsInPlay.length; i++) {
        card = cardsInPlay[i];
        DeckofCardsSprite[card.suit][card.value].render(card.xPos, card.yPos);
    }

    if (cardsInPlay.length < 4 && !animationInProgress) {
        switch (curPlayerIndex) {
            case 0:
                starSprite.render(BOARDWIDTH / 2 + 50, BOARDHEIGHT - CARDHEIGHT - 75);
                break;
            case 1:
                starSprite.render(CARDWIDTH + 50 - 13, BOARDHEIGHT / 2 + 50);
                break;
            case 2:
                starSprite.render(BOARDWIDTH / 2 + 50, CARDHEIGHT + 25);
                break;
            case 3:
                starSprite.render(BOARDWIDTH - CARDWIDTH - 50 - 25, BOARDHEIGHT / 2 - 50 - 25);
                break;
        }
    }
}
function animateLoop() {
    //runs every time the browser refreshes the screen, but only when requested by the game
    //
    //when movingTrickOffBoard is TRUE, we are clearing the trick off the table and giving it to the player that won the trick
    //this only animates cards that are
    //1. setup for animation via function call
    //2. in the cardsInPlay array

    animationInProgress = true;
    
    
    var keepAnimating = false;
    cardsInPlay.forEach(function (card, index) {
        if (card.translate() === true) {
            keepAnimating = true;
        }
    });
    if (keepAnimating) {
        animationInProgress = true;
        window.requestAnimationFrame(animateLoop);
    } else { //all cards have met their final destination
        animationInProgress = false;
        if (requestTrickCleared) {
            requestTrickCleared = false;
            gameMaster(COMMANDS.CLEARTRICK);
        } else if (requestTrickResultsCheck) {
            requestTrickResultsCheck = false;
            gameMaster(COMMANDS.PROCESSRESULTS);
        } else if (requestNextPlayerPlays){
            //it's not the 4th person playing
            requestNextPlayerPlays = false;
            gameMaster(COMMANDS.NOTIFYNEXTPLAYERTOPLAY);
        }
    }
    drawTheBoard();
}

function computerSelectCardsToTransfer(){
    /*
     * each computer player selects three cards to be handed left, right, or across
     * @returns nothing
     */
    
    //attempts to get rid of queen, king, and ace of spades, 
    //followed by face hearts, 
    //followed by face cards, 
    //followed by any hearts, 
    //followed by highest card of hearts, then other suits
    if(gameState !== 1){return;}
    

    function checkCard(player, suit, value){
        //checks if the card 
        var card = player.hasCard(suit,value);
        if(card !== false){card.toggleSelected(); return true;}
        return false;
    }
    
    
    for(i = 1; i< players.length; i++){
        var cardsSelected = 0;
        if(checkCard(players[i], SUIT.SPADES.value, 10)){players[i].numSelectedCards++;}
        if(checkCard(players[i], SUIT.SPADES.value, 12)){players[i].numSelectedCards++;}
        if(checkCard(players[i], SUIT.SPADES.value, 11)){players[i].numSelectedCards++;}
        if(players[i].numSelectedCards < 3 && checkCard(players[i], SUIT.HEARTS.value, 12)){players[i].numSelectedCards++;}
        if(players[i].numSelectedCards < 3 && checkCard(players[i], SUIT.HEARTS.value, 11)){players[i].numSelectedCards++;}
        if(players[i].numSelectedCards < 3 && checkCard(players[i], SUIT.HEARTS.value, 10)){players[i].numSelectedCards++;}
        if(players[i].numSelectedCards < 3 && checkCard(players[i], SUIT.HEARTS.value, 9)){players[i].numSelectedCards++;}
        if(players[i].numSelectedCards < 3 && checkCard(players[i], SUIT.DIAMONDS.value, 12)){players[i].numSelectedCards++;}
        if(players[i].numSelectedCards < 3 && checkCard(players[i], SUIT.CLUBS.value, 12)){players[i].numSelectedCards++;}
        if(players[i].numSelectedCards < 3 && checkCard(players[i], SUIT.DIAMONDS.value, 11)){players[i].numSelectedCards++;}
        if(players[i].numSelectedCards < 3 && checkCard(players[i], SUIT.CLUBS.value, 11)){players[i].numSelectedCards++;}
        if(players[i].numSelectedCards < 3 && checkCard(players[i], SUIT.DIAMONDS.value, 10)){players[i].numSelectedCards++;}
        if(players[i].numSelectedCards < 3 && checkCard(players[i], SUIT.CLUBS.value, 10)){players[i].numSelectedCards++;}
        
        if(players[i].numSelectedCards !== 3){
            outerLoop:
              for(x = 1; x <= 4; x++) {
                var suitValue = (3-x)%4;//checks Hearts(2) first, then clubs (1), then diamonds(0), then spades(3)
                    var suitInHand = players[i].cardsOfSuit(suitValue);
                        for(j = suitInHand.length -1; j >= 0; j--){
                         if(!suitInHand[j].isSelected){
                             players[i].numSelectedCards++;
                             suitInHand[j].toggleSelected();
                             if(players[i].numSelectedCards === 3){
                                 break outerLoop;
                             }
                         }
                     }
                }    
        }
    }
    drawTheBoard();
}

function cmdConductAI(){

    gameMaster(COMMANDS.NOTIFYNEXTPLAYERTOPLAY);
}

function cmdAIselectCards(){
    computerSelectCardsToTransfer();
}

function computerPlayCard(){
    //makes the computer play the card
    if(curPlayerIndex === 0 || cardsInPlay.length === 4){ return false;}//this is a human player. exit
    
    /* is this is the first play of the round?
     *  play the 2 of clubs
     * is this the first
     * is this the first play of the trick?
     *  play a random card (include hearts if it is broken)
     * is this not the first play of the trick?
     *  attempt to play under the highest leading suit
     *  if can't follow suit, play the queen of spades
     *  if don't have the queen of spades, play the highest heart
     *  otherwise just play a really high card
     *  
     */
    var curPlayer = players[curPlayerIndex]; var randIndex;
    var card;var leadingSuit;
    if(animationInProgress){return;}
    switch(gameState){
        case 1:
            break;
        case 2:     //round is in play
            LogOutput("Computer is playing for: " + curPlayer.name);
            if(firstTrickOfRound){
                if(cardsInPlay.length === 0){       //play the 2 of clubs
                    curPlayer.hand.forEach(function (gcard, index) {
                    if (gcard.suit === SUIT.CLUBS.value && gcard.value === 0){
                    attemptToPlayACard(gcard,curPlayer);
                    return;
                }});
                }else{      //first trick of the game, but 2-4 players. if can't follow suit, do not allow trick cards
                    leadingSuit = cardsInPlay[0].suit;
                    if(curPlayer.hasSuitInHand(leadingSuit)){
                        attemptToPlayACard(curPlayer.highestCardOfSuit(leadingSuit), curPlayer);       //following suit and playing highest card
                        return;
                    } else{     //not following suit. don't play a trick card
                        randIndex = Math.floor(Math.random() * curPlayer.hand.length);
                        card = curPlayer.hand[randIndex];
                        while(card === SUIT.HEARTS.value || (card.suit === SUIT.SPADES.value && card.value === 10)){
                            randIndex = Math.floor(Math.random() * curPlayer.hand.length);
                            card = curPlayer.hand[randIndex];
                        }
                        attemptToPlayACard(card, curPlayer);
                        return;
                    }
                }
            } else{        //not the first trick
                if(cardsInPlay.length === 0){
                    if(heartsBroken){
                        randIndex = Math.floor(Math.random() * curPlayer.hand.length);
                        card = curPlayer.hand[randIndex];
                    }else{
                        randIndex = Math.floor(Math.random() * curPlayer.hand.length);
                        card = curPlayer.hand[randIndex];
                        while(card.suit === SUIT.HEARTS.value){
                            randIndex = Math.floor(Math.random() * curPlayer.hand.length);
                            card = curPlayer.hand[randIndex];
                        }
                    }
                        attemptToPlayACard(card, curPlayer);
                        return;
                }else{
                    leadingSuit = cardsInPlay[0].suit;
                    if(curPlayer.hasSuitInHand(leadingSuit)){
                        attemptToPlayACard(curPlayer.highestCardOfSuit(leadingSuit), curPlayer);       //following suit and playing highest card
                        return;
                    }else{     //not following suit. don't play a trick card
                        if(curPlayer.hasCard(SUIT.SPADES.value, 10) !== false){
                            card = curPlayer.hasCard(SUIT.SPADES.value, 10) ;
                            attemptToPlayACard(card, curPlayer);
                            return;
                        }else if(curPlayer.hasSuitInHand(SUIT.HEARTS.value)){
                            attemptToPlayACard(curPlayer.highestCardOfSuit(SUIT.HEARTS.value), curPlayer);
                            return;
                        }else{
                            randIndex = Math.floor(Math.random() * curPlayer.hand.length);
                            card = curPlayer.hand[randIndex];
                            attemptToPlayACard(card,curPlayer);
                            return;
                        }
                    }                    
                }
            }
            break;
    }
    
    
    
}

function attemptToPlayACard(card, playerThatClicked) {
    /*several checks here
     2 of clubs must be played first
     hearts cannot be played unless hearts has been broken
     players must play in turn
     suits must match the leading suit (unless that suit is not owned)
     **/
    var playIsGood = false;
    if (players[curPlayerIndex] !== playerThatClicked) {
        LogOutput("Not your turn");
        return;
    }
    if (firstTrickOfRound && cardsInPlay.length === 0) {
        //must play the 2 of clubs
        if (card.suit === SUIT.CLUBS.value && card.value === 0) {
            playIsGood = true;
        } else {
            LogOutput("You must play the 2 of clubs");
            return;
        }
    } else {  //not the first play of the first trick
        if (cardsInPlay.length === 0) { //this is the first play of the 2+ trick
            if (heartsBroken || playerThatClicked.hasOnlyHearts()) { //can only play hearts if it has been broken or the player has no other suit.
                heartsBroken = true;
                playIsGood = true;
            } else if (card.suit === SUIT.HEARTS.value) {
                LogOutput("Hearts has not been broken");
                return false;
            } else {
                playIsGood = true;
            }
        } else { //this is the 2+ play of the trick. They must follow suit if they have it. No Trick cards can be played on the first hand
            if (firstTrickOfRound) {
                if (card.suit === SUIT.HEARTS.value || (card.suit === SUIT.SPADES.value && card.value === 10)) { //trying to play a trick card
                    LogOutput("You cannot play a heart or the Queen of Spades on the first trick");
                    return false;
                }
            }
            if (cardsInPlay[0].suit !== card.suit && playerThatClicked.hasSuitInHand(cardsInPlay[0].suit)) {
                LogOutput("You must follow suit");
                return false;
            } else { //not following suit. if the suit is hearts, it is now broken
                if (card.suit === SUIT.HEARTS.value) {
                    heartsBroken = true;
                }
                playIsGood = true;
            }
        }
    }

    if (playIsGood) {
        //plays a card from a player to the board center
        //subtracts it from that players hand and animates it
        LogOutput(playerThatClicked.name + "  played the " + card.getDetails());

        //selection location in center based on player
        switch (playerThatClicked.playerIndex) {
            case 0:
                card.newX = BOARDWIDTH / 2 - CARDWIDTH / 2;
                card.newY = BOARDHEIGHT / 2 + CARDHEIGHT / 2;
                break;
            case 1:
                card.newX = BOARDWIDTH / 2 - CARDWIDTH / 0.67;
                card.newY = BOARDHEIGHT / 2 - CARDHEIGHT / 2;
                break;
            case 2:
                card.newX = BOARDWIDTH / 2 - CARDWIDTH / 2;
                card.newY = BOARDHEIGHT / 2 - CARDHEIGHT / 2 - CARDHEIGHT;
                break;
            case 3:
                card.newX = BOARDWIDTH / 2 + CARDWIDTH / 2;
                card.newY = BOARDHEIGHT / 2 - CARDHEIGHT / 2;
                break;
        }


        cardsInPlay.push(card); //put the card on the array of animating cards
        card.setupForAnimation(card.newX, card.newY, MAXANIMATIONFRAMES);
        //take the card out of the players hand
        playerThatClicked.removeCardFromHand(card);
        //see if this is the 4th card played. if it is, tell the animateLoop method to inform the game master
        if (cardsInPlay.length !== 4) {
            curPlayerIndex = (curPlayerIndex + 1) % 4;
            requestNextPlayerPlays = true;
        } else {
            requestTrickCleared = true;
            firstTrickOfRound = false;
        }
        animateLoop();
    }
}

function clickedCanvas(e) {
    if (animationInProgress) {
        return;
    }//do nothing, currently animating
    //do a collission detection to find out what card the player just clicked on
    var card, playerThatClicked;
    var clickedACard = false;
    loop1:
            for (f = 0; f < players.length; f++) {
        for (g = players[f].hand.length - 1; g >= 0; g--) {
            card = players[f].hand[g];
            if (e.offsetX > card.xPos && e.offsetX < card.xPos + CARDWIDTH &&
                    e.offsetY > card.yPos && e.offsetY < card.yPos + CARDHEIGHT) {
                document.getElementById("btndemo").value = card.getDetails();
                //the cards are always delt in order, so the first match (descending)
                //is the card that was clicked on
                console.log(card.getDetails());
                clickedACard = true;
                playerThatClicked = players[f];
                break loop1;
            }
        }
    }
    if (!clickedACard) {
        return; //exit the function, nothing was clicked
    }

    /*do an action based on the game state
     1 - select a card to pass based on the round
     2 - select a card to play
     */

    switch (gameState) {
        case 1:      //players are selecting the cards that they want to pass
            if (card.isSelected === true) {
                card.toggleSelected();
                playerThatClicked.numSelectedCards--;
            } else if (playerThatClicked.numSelectedCards < 3 && card.isSelected === false) {
                card.toggleSelected();
                playerThatClicked.numSelectedCards++;
            } else if (playerThatClicked.numSelectedCards >= 3 && card.isSelected === false) {
                LogOutput("You have already selected 3 cards");
            }
            if (gameRound % 4 !== 0) {
                //see if all 4 players have selected cards
                var selectionComplete = true;
                for (i = 0; i < players.length; i++) {
                    if (players[i].numSelectedCards !== 3) {
                        selectionComplete = false;
                    }
                }
                if (selectionComplete === true) {
                    ///selection complte, pass the cards
                    gameMaster(COMMANDS.PASSCARDS);
                }
            }
            drawTheBoard();
            break;
        case 2:      //players are selecting cards that they want to play
            attemptToPlayACard(card, playerThatClicked);
            break;
    }
}
function LogOutput(text) {
    //logs the output to the screen
    logger = document.getElementById('pLog');
    var newText = logger.innerHTML + "<br>" + text;
    if (newText.length > 500) {
        var index = newText.search("<br>");
        newText = newText.slice(index + 4, newText.length); //eliminates the first line of the log
    }
    logger.innerHTML = newText;
}
function transferCardsBetweenPlayers(losingPlayer, gainingPlayer, card) {
    losingPlayer.removeCardFromHand(card);
    card.player = gainingPlayer;
    gainingPlayer.hand.push(card);
    console.log("moving card: " + card.getDetails() + " from " + losingPlayer.name +
            " to " + gainingPlayer.name);
}

function playerWith2ofClubs(){
    for (i = 0; i < players.length; i++) {
        for (j = 0; j < players[i].hand.length; j++) {
            if (players[i].hand[j].suit === SUIT.CLUBS.value && players[i].hand[j].value === 0) {
                return(players[i]);        
            }
        }
    }
}

function gameMaster(command) {
    /* this function is responsible for calling functions that run the rules
     * of the game
    round 1 - players must pick 3 cards to pass left
    round 2 - players pass to right
    round 3 - players pass across
    round 4 - players don't pass
    repeat
    */
    function passCards() {
        for (i = 0; i < players.length; i++) {
            var nothingSelected = false;
            var j = 0;
            while (!nothingSelected) {
                var gCard = new cardObject(0, 0);
                gCard = players[i].hand[j];
                players[i].numSelectedCards = 0;
                if (gCard.isSelected) {
                    gCard.isSelected = false;
                    switch (gameRound % 4) {
                        case 1:                             //transfer it to the guy to the left, unselect it
                            transferCardsBetweenPlayers(players[i], players[(i + 1) % 4], gCard);
                            break;
                        case 2:                            //transfer it to the guy to the right, unselect it
                            transferCardsBetweenPlayers(players[i], players[(i + 3) % 4], gCard);
                            break;
                        case 3:                             //transfer it to the guy across, unselect it
                            transferCardsBetweenPlayers(players[i], players[(i + 2) % 4], gCard);
                            break;
                    }
                    j--;
                }
                j++;
                if (j === players[i].hand.length) {
                    nothingSelected = true;
                }
            }
        }
        console.log("I transferred the cards");
        //resort the cards for the players
        sortCards();
        updateCardPositionOnBoard();
    }
    function startTheRound(){
        //select the player with the 2 of clubs
            curPlayerIndex = players.indexOf(playerWith2ofClubs());
            LogOutput(players[curPlayerIndex].name + " must play the 2 of clubs");
            firstTrickOfRound = true;
            gameState = 2;
            
            //if the player isn't human, have AI start the round
            if(curPlayerIndex !== 0){
                gameMaster(COMMANDS.NOTIFYNEXTPLAYERTOPLAY);
            }
            
    }
    switch (command) {

        case COMMANDS.PASSCARDS:
            passCards();
            drawTheBoard();
            startTheRound();
            break;
        case COMMANDS.NOTIFYNEWROUND:
            if (gameRound % 4 === 1) {
                LogOutput("Round: " + gameRound + ". Pass 3 cards to the left.");
                computerSelectCardsToTransfer();
            } else if (gameRound % 4 === 2) {
                LogOutput("Round: " + gameRound + ". Pass 3 cards to the right.");
                computerSelectCardsToTransfer();
            } else if (gameRound % 4 === 3) {
                LogOutput("Round: " + gameRound + ". Pass 3 cards across.");
                computerSelectCardsToTransfer();
            } else {
                LogOutput("Round: " + gameRound + ". Keep your cards.");
                startTheRound();
            }
            break;
        case COMMANDS.CLEARTRICK:
            //determine who won the trick
            trickWinner = cardsInPlay[0].player;
            var leadingSuit = cardsInPlay[0].suit;
            var bestCard = cardsInPlay[0];
            for (var i = 1; i < cardsInPlay.length; i++) {
                if (cardsInPlay[i].suit === leadingSuit &&
                        cardsInPlay[i].value > bestCard.value) {
                    bestCard = cardsInPlay[i];
                }
            }
            trickWinner = bestCard.player;
            LogOutput(trickWinner.name + " takes the hand with the " + bestCard.getDetails());

            cardsInPlay.forEach(function (card, index) {
                card.setupForAnimation(trickWinner.stockPileX, trickWinner.stockPileY, MAXANIMATIONFRAMES);
            });
            requestTrickResultsCheck = true;//tells animateLoop to return to gameMaster.Commands.PROCESSRESULTS
            animationInProgress = true;
            setTimeout(animateLoop, 1000);
            break;
        case COMMANDS.NOTIFYNEXTPLAYERTOPLAY:
            //if it is a computer that should play next, then have them play
            if(curPlayerIndex !== 0){computerPlayCard();}
            break;
        case COMMANDS.PROCESSRESULTS:
            //add hearts and Q of Spades to the player's stockpile
            while (cardsInPlay.length !== 0) {
                var tempCard = cardsInPlay.pop();
                currentlyAnimatingCard = tempCard;
                if (tempCard.suit === SUIT.HEARTS.value ||
                        (tempCard.suit === SUIT.SPADES.value && tempCard.value === 10)) {
                    trickWinner.cardsWon.push(tempCard);
                }
            }
            
            //check if all cards have been played
            if (players[0].hand.length === 0 && players[1].hand.length === 0 && players[2].hand.length === 0 &&
                    players[3].hand.length === 0) {
                LogOutput("We are done with this round:");
                //tally the scores
                var oldScore = [4];
                oldScore[0] = players[0].score;
                oldScore[1] = players[1].score;
                oldScore[2] = players[2].score;
                oldScore[3] = players[3].score;
                Loop1:
                        for (var i = 0; i < players.length; i++) {
                    var pointsTaken = 0;
                    var handLength = players[i].cardsWon.length;
                    if (handLength === 14) {
                        players[(i + 1) % 4].score += 26;
                        players[(i + 2) % 4].score += 26;
                        players[(i + 3) % 4].score += 26;
                        LogOutput(players[i].name + " shoots the moon.");
                        break Loop1;
                    } else {
                        for (var j = 0; j < handLength; j++) {
                            if (players[i].cardsWon[j].suit === SUIT.HEARTS.value) {
                                pointsTaken++;
                            } else if (players[i].cardsWon[j].suit === SUIT.SPADES.value &&
                                    players[i].cardsWon[j].value === 10) {
                                pointsTaken += 13;
                            }
                        }
                        players[i].score += pointsTaken;
                    }
                }

                for (var i = 0; i < players.length; i++) {
                    var diff = players[i].score - oldScore[i];
                    LogOutput(players[i].name + " takes " + diff + " points.");
                }
                updateScoreBoard();


                //check if there is a winner

                var brokeMaxScore = false;
                for(i = 0; i<players.length; i++){
                    if(players[i].score >= maxSCORE){                           
                        brokeMaxScore = true;
                    }
                }
                if(brokeMaxScore){
                    var lowestScorePlayer = players[0];
                    for(i = 1; i<players.length; i++){
                        lowestScorePlayer = players[i].score < lowestScorePlayer.score ? players[i] : lowestScorePlayer;
                    }
                     //if there is a winner display the winner and prompt to restar the game
                    LogOutput(lowestScorePlayer.name + " wins the game!");
                    gameState = 4;
                    fadeCommandButton(true, "Start Game");
                }else{//if no winner prompt to deal
                    gameState = 3;
                    fadeCommandButton(true, "Deal Next Hand");
                }
            } else{
                //we can keep playing
                updateScoreBoard();
                curPlayerIndex = players.indexOf(trickWinner);
                  //reset the first trick of round variable
                firstTrickOfRound = false;
                if(curPlayerIndex !== 0){
                    gameMaster(COMMANDS.NOTIFYNEXTPLAYERTOPLAY);
                }
            }
            break;
        default:
            LogOutput("Game master called and I don't know what to do");
    }
}

function fadeCommandButton(fadingIn, newButtonText){
    var button = document.getElementById("cmdButton");
    var opacityCounter = 0;
    if(fadingIn){
             button.style.visibility = "visible";
             button.innerHTML = newButtonText;
             var intervalId = setInterval(fadeIn, 50);
        function fadeIn() {
            opacityCounter += 10;
            button.style.opacity = opacityCounter / 100;
            if (opacityCounter === 100) {
                clearInterval(intervalId);
            }
        }
    }else{
        opacityCounter = 100;
        var intervalId = setInterval(fadeOut, 50);
        function fadeOut() {
            opacityCounter -= 10;
            button.style.opacity = opacityCounter / 100;
            if (opacityCounter === 0) {
                clearInterval(intervalId);
                button.style.visibility = "hidden";
            }
        }
    }
}

function fadeInCommandButton(){
    var button = document.getElementById("cmdButton");
    if(button.style.visibility === "visible"){
        fadeCommandButton(false,"nothing");
    }else{
    fadeCommandButton(true,"testing");}
}

function cmdClick() {
    /*
     * User clicked on the "Command" Button. Do whatever is associated with the game state at the time
     * at the time
     * 1 - players selection cards to pass
     * 2 - round is in play
     * 3 - round complete, no winner
     * 4 - round complete, there was a winner
     */
    switch(gameState){
        case 1:
            break;
        case 2:
            break;
        case 3:  //deal next hand
            fadeCommandButton(false,"nothign");
            clearCardsWon();
            shuffleAndDeal();
            drawTheBoard();
            gameState = 1;
            gameRound++;
            gameMaster(COMMANDS.NOTIFYNEWROUND);
            updateScoreBoard();
            break;
        case 4: //start a new game
            fadeCommandButton(false,"nothign");
            initializeVariables();
            shuffleAndDeal();
            drawTheBoard();
            gameState = 1;
            gameRound = 1;
            gameMaster(COMMANDS.NOTIFYNEWROUND);
            break;
    }
}

/*
 * Shuffle and Deal 52 cards
 * Let each player select 3 cards to select and pass to the left
 * Set the player with the 2 of clubs as the first to play
 * Let each player play their hands
 * Calculate/Display the score at the end of those 13 plays
 *  Each heart is worth 1 point
 *  Q of Spades is worth 13 points
 *  If player shoots the moon all other players get 26 points
 *  Winner is person with lowest points when someone gets 100 points
 * 2nd Round - shuffle and deal
 *  let each player select three cards and push them right
 *  repeat
 * 3rd Round - shuffle and deal
 *  let each player pass their cards across
 *  repeat
 * 4th round - no passing of cards
 * Display a winner
 * Let players opt to play again
 */
createSprites();
//drawAllCards();

canvas.addEventListener("mousedown", clickedCanvas);
//document.getElementById("documentBody").addEventListener("keydown", clickedKeyboard);
//gameLoop();
