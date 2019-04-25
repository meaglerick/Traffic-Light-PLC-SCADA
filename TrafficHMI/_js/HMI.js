
//'use strict';
var canvas = document.getElementById("myCanvas");
var ctx = canvas.getContext("2d");
var BOARDWIDTH = 800, BOARDHEIGHT = 800;

var trafficLightSprites = new Array(2);
var trafficLightImage = new Image();
var trafficLightImageSmall = new Image();
trafficLightImage.src = "_img/traffic4.png";
trafficLightImageSmall.src = "_img/traffic4_small.png";

var trafficLightWidth = 280;
var trafficLightHeight = 134;
var trafficLightWidthSmall = 280/2;
var trafficLightHeightSmall = 134/2;

var lightScaler = 0.5;
var ScreenIsSmall = false;

var LIGHT = {RED: {value: 0},
    YELLOW: {value: 1},
    GREEN: {value: 2},
    ALLOFF: {value: 3},
    ALLON: {value: 4}};

var ws = null;

var intersections = new Array(4);

function trafficIntersection(centerX, centerY, intersectionName, divControlPanel){
    this.centerX = centerX;
    this.centerY = centerY;
    this.intersectionName = intersectionName;
    this.connectionError = false;   //identifies if the intersection has an error
    this.divControlPanel = divControlPanel //the HTML div that holds this lights container contorls
    
    var trafficLights = new Array(4);
   
    trafficLights[0] = new trafficLight(this.centerX +20 ,this.centerY + 110,LIGHT.RED);
    trafficLights[2] = new trafficLight(this.centerX -20,this.centerY -90,LIGHT.RED);
    trafficLights[1] = new trafficLight(this.centerX + 60,this.centerY -25,LIGHT.RED);
    trafficLights[3] = new trafficLight(this.centerX - 60,this.centerY +45,LIGHT.RED);

    this.setErrorMode = function(isInError){
        //if isInError = true then remove the updates from the board and set the div on the HMI to a red nasty color
        //LogOutput("changing error mode at: " + this.intersectionName + " to " +isInError);
        if(isInError){
            this.connectionError = true;
            this.divControlPanel.style.backgroundColor = 'red';
        }
        else{
            
            this.connectionError = false;
            this.divControlPanel.style.backgroundColor = '#e5e5e5';
        }
    };

    this.drawToMap = function(){
       
        
        //draw to the board here
        if(!this.connectionError){
            if(!ScreenIsSmall){
                //draw at a standard resolution
                trafficLights.forEach(function (trafficLight, index) {
                    trafficLightSprites[0].render(trafficLight.avatarXPos, trafficLight.avatarYPos, trafficLight.lightIndex.value);
                });  
            }else{
                //the screen was detected to be small. draw with smaller avatars
                trafficLights.forEach(function (trafficLight, index) {
                    trafficLightSprites[1].render(trafficLight.avatarXPos/2, trafficLight.avatarYPos/2, trafficLight.lightIndex.value);
                });  
            }
        }
        
    };
    
    this.updateLights = function(updateCode){
        //Updates the entire section based on the 4 character string sent
        //typically a '0202' or a '0101'
        
        trafficLights[0].updateByValue(Number(updateCode[0]));
        trafficLights[2].updateByValue(Number(updateCode[2]));
        trafficLights[1].updateByValue(Number(updateCode[1]));
        trafficLights[3].updateByValue(Number(updateCode[3]));
    }
    
}


function trafficLight(avatarXPos, avatarYPos, lightIndex) {
    this.avatarXPos = avatarXPos;
    this.avatarYPos = avatarYPos;
    this.lightIndex = lightIndex || LIGHT.RED;
    this.setLightColor = function (value) {
        //determines if the player has any suit other than HEARTS
        //if it does, return true
        
        this.lightIndex = value;
        if(this.lightIndex > 2 || this.lightIndex < 0){
            this.lightIndex = LIGHT.RED;
        }
    };
    this.cycleLight = function (){
        
        switch (this.lightIndex){
            case LIGHT.RED:
                this.lightIndex = LIGHT.GREEN;
                break;
            case LIGHT.YELLOW:
                this.lightIndex = LIGHT.RED;
                break;
            case LIGHT.GREEN:
                this.lightIndex = LIGHT.YELLOW;
                break;
        };
    };
    this.updateByValue = function (indexValue){
        switch (indexValue){
            case 0:
                this.lightIndex = LIGHT.RED;
                break;
            case 1:
                this.lightIndex = LIGHT.YELLOW;
                break;
            case 2:
                this.lightIndex = LIGHT.GREEN;
                break;
            case 3:
                this.lightIndex = LIGHT.ALLOFF;

                break;
            case 4:
                this.lightIndex = LIGHT.ALLON;

                break;
        };
    };
}


function createSprites() {
    trafficLightSprites = new Array(2);

    
            //create the sprites for each of these cards
            trafficLightSprites[0] = sprite({       //the larger sprite
                context: ctx,
                width: trafficLightWidth,
                height: trafficLightHeight,
                image: trafficLightImage,
                xOffset: 0,
                yOffset: 0,
                frameIndex: 0,
                numberOfFrames: 5
            });
            trafficLightSprites[1] = sprite({       //the smaller sprite
                context: ctx,
                width: trafficLightWidthSmall,
                height: trafficLightHeightSmall,
                image: trafficLightImageSmall,
                xOffset: 0,
                yOffset: 0,
                frameIndex: 0,
                numberOfFrames: 5
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
    that.frameIndex = options.frameIndex;
    that.numberOfFrames = options.numberOfFrames || 1;
    
    that.render = function (posX, posY, frameIndex) {
        // Clear the canvas
        that.context.clearRect(0, 0, that.width/that.numberOfFrames, that.height);
        // Draw the animation
        that.context.drawImage(
                that.image,
                frameIndex * that.width / that.numberOfFrames,
                that.yOffset,
                that.width / that.numberOfFrames,
                that.height,
                posX,
                posY,
                that.width / that.numberOfFrames * lightScaler, //can use this for scaling
                that.height *lightScaler);

    };
    return that;
}
function initializeVariables() {

    intersections[0] = new trafficIntersection(172,220,"NW Street", document.getElementById("divNW"));
    intersections[1] = new trafficIntersection(172,525,"SW Street", document.getElementById("divSW"));
    intersections[2] = new trafficIntersection(520,220,"NE Street", document.getElementById("divNE"));
    intersections[3] = new trafficIntersection(520,525,"SE Street", document.getElementById("divSE"));
   
}

function drawTheBoard() {
    //this function draws the board at the start of the game
    
    //detect if the screen is too small. if it is, change the element size, if not, leave it big
    var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

        if(w < 1500 || h < 900){   
            document.getElementById("myCanvas").width="400";
           document.getElementById("myCanvas").height="400";
           document.getElementById("myCanvas").style="border:5px solid greenyellow; background: url('./_img/back_small.jpg')";
           ScreenIsSmall = true;
       }else{
           document.getElementById("myCanvas").width="800";
           document.getElementById("myCanvas").height="800";
           document.getElementById("myCanvas").style="border:5px solid greenyellow; background: url('./_img/back.jpg')"; 
           ScreenIsSmall = false;
       }
     
    
    canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
    
    //draw the player sprites
  
    intersections.forEach(function (intersect, index) {
        intersect.drawToMap();
    });


}


function LogOutput(text) {
    //logs the output to the screen
    logger = document.getElementById('pLog');
    var newText = logger.innerHTML + "<br>" + text;
    if (newText.length > 700) {
        var index = newText.search("<br>");
        newText = newText.slice(index + 4, newText.length); //eliminates the first line of the log
    }
    logger.innerHTML = newText;
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
    drawTheBoard();
    LogOutput("clicked start");
}

function cmdUseSocket(uname,pwd,ip) {

    
    if ("WebSocket" in window)
    {
       // Let us open a web socket
        document.getElementById("loginupdate").innerHTML = "Connecting...";
       if(ws === null){
            LogOutput("Establishing connection to: " + ip + " with username: " + uname + " with entered password");
           
           connString = "ws://" + ip + ":9999";
           ws = new WebSocket(connString);
            
           //ws = new WebSocket("ws://192.168.174.129:9999");
       } else{
           ws.onopen();
       }

       ws.onopen = function()
       {
          // Web Socket is connected, send data using send()
          
          LogOutput("Connection established");
            drawTheBoard();
            hideLoginPage();
           
       };

       ws.onmessage = function (evt) 
       { 
          var received_msg = evt.data;
            //LogOutput(received_msg);
            var lines = received_msg.split('\n');
            console.log(received_msg);
            if(lines[0] === 'LightData90210' && lines.length >= 6){ //this is updated traffic light information, follows the format:
                 //LogOutput("updating");
                    //0. "LightData90210"
                    //1. Intersection Title
                    //2. North Light
                    //3. East Light
                    //4. South Light
                    //5. West Light
                    //6. Status - 0 should be normal, 1, for maintenance, 2 for test mode
                    
                    intersections.forEach(function (intersect, index) {
                        if(lines[1] === intersect.intersectionName) {//updates if there is a name match
                            var code = lines[2] + lines[3] + lines[4] + lines[5];
                            intersect.setErrorMode(false);
                             intersect.updateLights(code);
                             var stat = lines[6];
                             //LogOutput("NW Street error code is: " + stat + "\nSTATUS: " + code);
                             var msg;
                             if(stat ==='0'){
                                 msg = "Reported Mode: Normal";
                             }else if (stat === '1'){
                                 msg = "Reported Mode: Maintenance";
                             }else if (stat === '2'){
                                  msg = "Reported Mode: TESTING";
                             }
                             document.getElementById("lbl" + intersect.intersectionName.substring(0,2) + "Status").innerHTML = msg;
                             LogOutput("Update received at:" + intersect.intersectionName);
                        }
                        else{
                            //ignore...doesn't apply to this intersection
                        }
                    });
                   drawTheBoard();
                   //LogOutput("Received a traffic light update from the SCADA");
           }else if(lines[0] === 'NAMES'){
               //updating the names of the intersection
             //   LogOutput("Received intersection names");
               intersections[0].intersectionName = lines[1];
               intersections[1].intersectionName = lines[2];
               intersections[2].intersectionName = lines[3];
               intersections[3].intersectionName = lines[4];              
           }else if (lines[0].search('ERROR') > -1){
               
               var msg = lines[0];
               intersections.forEach(function (intersect, index) {
                   if(msg.search(intersect.intersectionName) > -1 && msg.search('No Connection' > -1)){
                        LogOutput("ERROR: no connection to: " + intersect.intersectionName);
                        intersect.setErrorMode(true);
                   }
                    
               });  
           }
           
           else{
                LogOutput("New Message:\n" + received_msg);
           }
           
       };

       ws.onclose = function()
       { 
          // websocket is closed.
          LogOutput("Connection either failed to open or is closed"); 
           document.getElementById("loginupdate").innerHTML = "Connectiont to remote SCADA is closed";
          ws = null;
            showLoginPage();
          
       };

       window.onbeforeunload = function(event) {
          socket.close();
       };

    }

    else
    {
       // The browser doesn't support WebSocket
       LogOutput("WebSocket NOT supported by your Browser!");
    }



}


function cmdMaintenance(btn){
    
    if(ws !== null && ws.readyState === ws.OPEN){
        LogOutput("Putting the intersection at : " + intersections[btn.value].intersectionName + " into maintenance mode");
        ws.send("MAINTENANCE" + intersections[btn.value].intersectionName);
    }else{
        LogOutput("Not connected!");
    }
}
function cmdNormalOps(btn){
   if(ws !== null && ws.readyState === ws.OPEN){
        LogOutput("Putting the intersection at : " + intersections[btn.value].intersectionName + " into normal mode");
        ws.send("NORMAL" + intersections[btn.value].intersectionName);
    }else{
        LogOutput("Not connected!");
    }
}
function cmdTestMode(btn){
    if(ws !== null && ws.readyState === ws.OPEN){
        LogOutput("Putting the intersection at : " + intersections[btn.value].intersectionName + " into test mode");
        ws.send("TEST" + intersections[btn.value].intersectionName);
    }else{
        LogOutput("Not connected!");
    }
}
function Logout(){
    if(ws !== null && ws.readyState === ws.OPEN){
        ws.close();
    }
}

function showLoginPage(){
    //hides the main body and shows the login page
    document.getElementById("mainLogin").style.display = 'block';
    document.getElementById("mainBody").style.display = 'none';
}
function hideLoginPage(){
    //hides the login page and shows the main body
    document.getElementById("mainLogin").style.display = 'none';
    document.getElementById("mainBody").style.display = 'block';
}

createSprites();
initializeVariables();

