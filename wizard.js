var http = require('http');

var tvs = ['localhost'];

function getTv(tv, cmd, value) {
	var targetVal = value ? value : '0';
	http.get( "http://" + tv + ":8080/api?" + cmd + "=" + targetVal, function(res) {
	  // console.log("Got response: " + res.statusCode);
	}).on('error', function(e) {
	  // console.log("Got error: " + e.message);
	});
}

function getIt(cmd, value) {
	if (!value) value = "foo";

	for (var i=0; i<tvs.length; i++) {
		getTv(tvs[i], cmd, value);
	}
	return false;
}

var rainIndex = 0;

function rainbowize() {
	var rainbowInterval = setInterval(function() {
		makeColorGradient(rainIndex++);
		if (rainIndex > 50) { 
			rainIndex=0;
			clearInterval(rainbowInterval);
			getIt('clearcolor');
		}
	}, 100);
	return false;
}

// RANDOMIZATION SECTION
var effects = ['none', 'negative', 'solarize', 'sketch', 'emboss', 'oilpaint', 'gpen', 'pastel', 'watercolor', 'colorswap', 'washedout', 'cartoon'];
var randomOn = false;
var imageCount = 6;

// Returns a random integer between min (included) and max (excluded)
// Using Math.round() will give you a non-uniform distribution!
function getRandomInt(min, max) {
	return Math.floor(Math.random() * (max - min)) + min;
}

function stoprandom() {
	randomOn = false;
	return false;
}

function startrandom() {
	randomOn = true;
	for (var i=0; i<tvs.length; i++) {
		nextRandom(tvs[i]);
	}
	return false;
}

function nextRandom(thisTv) {
	setTimeout(function() {
		switch(getRandomInt(0,4)) {
			case(0):
				getTv(thisTv, 'seteffect', effects[getRandomInt(0,effects.length)]);
				break;
			case(1):
				getTv(thisTv, 'colorize', JSON.stringify({'a':1,'r':getRandomInt(1,255),'g':getRandomInt(1,255),'b':getRandomInt(1,255)}));
				break;
			case(2):
				getTv(thisTv, 'overlay', getRandomInt(0,imageCount));
				break;
			case(3):
				getTv(thisTv, 'clearcolor');
				break;
			case(4):
				getTv(thisTv, 'hflip');
				// Flip it back after a bit
				setTimeout(function(){
					getTv(thisTv, 'hflip');
				}, getRandomInt(1000, 5000));
				break;
			case(5):
				getTv(thisTv, 'vflip');
				// Flip it back after a bit
				setTimeout(function(){
					getTv(thisTv, 'vflip');
				}, getRandomInt(1000, 5000));
				break;
			default:
				break;
		}

		if (randomOn) {
			nextRandom(thisTv);
		}
	}, getRandomInt(1000, 10000));
}

startrandom();