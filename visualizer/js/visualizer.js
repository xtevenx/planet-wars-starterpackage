const ParserUtils = {
    parseFleet: function (data) {
        data = data.split('.');
        // (owner, numShips, sourcePlanet, destinationPlanet, totalTripLength, turnsRemaining)
        return {
            owner: parseInt(data[0]),
            numShips: parseInt(data[1]),
            source: Visualizer.planets[data[2]],
            source_id: data[2],
            destination: Visualizer.planets[data[3]],
            destination_id: data[3],
            tripLength: parseInt(data[4]),
            progress: parseInt(data[4]) - parseInt(data[5])
        };
    },

    parsePlanet: function (data) {
        data = data.split(',');
        // (x, y, owner, numShips, growthRate)
        return {
            x: parseFloat(data[0]),
            y: parseFloat(data[1]),
            owner: parseInt(data[2]),
            numShips: parseInt(data[3]),
            growthRate: parseInt(data[4])
        };
    },

    parsePlanetState: function (data) {
        data = data.split('.');
        // (owner, numShips)
        return {
            owner: parseInt(data[0]),
            numShips: parseInt(data[1])
        };
    },

    _eof: true
};


const Visualizer = {
    canvas: null, // defined in setup()
    ctx: null, // defined in setup()
    frame: 0,
    turnSpeed: 4, // Integer version of turn speed for easier management
    turnsPerSecond: ((1 + Math.sqrt(5)) / 2) ** 4, // TurnsPerSecond = Phi ** turnSpeed
    playing: false,
    haveDrawnBackground: false,
    frameDrawStarted: null,
    frameDrawEnded: null,
    players: ["Player A", "Player B"],
    playerIds: ["-1", "-1"],
    map_id: 0,
    planets: [],
    moves: [],
    error_message: '',
    dirtyRegions: [],
    active_planet: -1,
    shipCount: [0, 0, 0],
    growthRate: [0, 0, 0],
    // See comment in this.switchPlanetZOrder() about how planetZOrder works.
    planetZOrder: [], // defined in setup()
    config: {
        planet_font: 'bold 14px Arial,Helvetica',
        fleet_font: 'normal 12px Arial,Helvetica',
        planet_pixels: [7, 10, 13, 17, 23, 29],
        showFleetText: true,
        display_margin: 35,
        teamColor: ['#334444', '#aa0000', '#5588aa'],
        teamColor_highlight: ['#445555', '#ff0000', '#88bbdd'],
        fleetColor: ['rgba(64,080,080,1.00)', 'rgba(192,000,000,1.00)', 'rgba(112,160,240,1.00)'],
        planetColor: ['rgba(64,080,080,1.00)', 'rgba(192,000,000,0.40)', 'rgba(112,160,240,0.40)']
    },

    setup: function (data) {
        // Setup Context
        this.canvas = document.getElementById('display');
        this.ctx = this.canvas.getContext('2d');
        this.ctx.textAlign = 'center';

        // Parse data
        this.parseData(data);

        // Calculate offset and range so the map is centered and fills the area
        let max_coords = {x: -999, y: -999};
        let min_coords = {x:  999, y:  999};
        for (let i = 0; i < this.planets.length; i++) {
            this.planetZOrder.push(i);
            let p = this.planets[i];
            if (p.x > max_coords.x) max_coords.x = p.x;
            if (p.x < min_coords.x) min_coords.x = p.x;
            if (p.y > max_coords.y) max_coords.y = p.y;
            if (p.y < min_coords.y) min_coords.y = p.y;
        }

        this.planetZOrder.sort((p, q) => {
            return this.planets[q].growthRate - this.planets[p].growthRate;
        });

        let ranges = [max_coords.x - min_coords.x, max_coords.y - min_coords.y];
        let range = Math.max(...ranges);

        let display_margin = this.config.display_margin;
        let unit_to_pixel = (this.canvas.height - display_margin * 2) / range;

        this.config.unit_to_pixel = unit_to_pixel;
        this.config.offset = [(-min_coords.x * unit_to_pixel) + display_margin,
                              (-min_coords.y * unit_to_pixel) + display_margin];
        this.config.offset[0] += ((range - ranges[0]) / 2) * unit_to_pixel;
        this.config.offset[1] += ((range - ranges[1]) / 2) * unit_to_pixel;

        // Draw first frame
        this.drawFrame(0);
    },

    changeSpeed: function (difference) {
        const newSpeed = this.turnSpeed + difference
        if (0 <= newSpeed && newSpeed <= 8) {
            this.turnSpeed = newSpeed;
            this.turnsPerSecond = ((1 + Math.sqrt(5)) / 2) ** this.turnSpeed;
        }
    },

    unitToPixel: function (unit) {
        return this.config.unit_to_pixel * unit;
    },

    pixelToUnit: function (pixel) {
        return pixel / this.config.unit_to_pixel;
    },

    drawBackground: function () {
        const ctx = this.ctx;

        // Draw background
        ctx.fillStyle = '#000000';
        if (this.haveDrawnBackground === false) {
            ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            this.haveDrawnBackground = true;
        }

        for (let i = 0; i < this.dirtyRegions.length; i++) {
            const region = this.dirtyRegions[i];
            ctx.fillRect(
                parseInt(region[0]),
                parseInt(region[1]),
                parseInt(region[2]),
                parseInt(region[3])
            );
        }

        this.dirtyRegions = [];
    },

    drawFrame: function (frame) {
        const ctx = this.ctx;

        let display_x = 0;
        let display_y = 0;

        let frameNumber = Math.floor(frame);
        if (frameNumber >= this.moves.length)
            frameNumber = this.moves.length - 1;

        const planetStats = this.moves[frameNumber].planets;
        const fleets = this.moves[frameNumber].moving;
        const numShips = [0, 0];
        const production = [0, 0];

        this.haveDrawnBackground = false;
        this.drawBackground();

        // Draw Planets
        ctx.font = this.config.planet_font;
        ctx.textAlign = 'center';

        const activePlanet = this.planetZOrder[this.planets.length];
        for (let i = 0; i < this.planetZOrder.length; i++) {
            const z = this.planetZOrder[i];
            if (z == activePlanet && i < this.planets.length) {
                continue;
            }

            const planet = this.planets[z];
            planet.owner = planetStats[z].owner;
            planet.numShips = planetStats[z].numShips;
            const highlight_this_planet = this.active_planet >= 0 && this.active_planet === z;

            this.shipCount[planet.owner] += planet.numShips;
            this.growthRate[planet.owner] += planet.growthRate;

            if (planet.owner > 0) {
                numShips[planet.owner - 1] += planet.numShips;
                production[planet.owner - 1] += planet.growthRate;
            }

            display_x = this.unitToPixel(planet.x) + this.config.offset[0];
            display_y = this.unitToPixel(planet.y) + this.config.offset[1];

            // Add shadow
            ctx.beginPath();
            ctx.arc(display_x + 0.5, this.canvas.height - display_y + 0.5, this.config.planet_pixels[planet.growthRate] + 1, 0, Math.PI * 2, true);
            ctx.closePath();
            ctx.fillStyle = "#000000";
            ctx.fill();

            let color = this.config.teamColor[planet.owner];
            if (highlight_this_planet) {
                color = this.config.teamColor_highlight[planet.owner];
            }

            // Draw circle
            ctx.beginPath();
            ctx.arc(display_x, this.canvas.height - display_y, this.config.planet_pixels[planet.growthRate], 0, Math.PI * 2, true);
            ctx.closePath();
            ctx.fillStyle = color;
            ctx.fill();

            ctx.fillStyle = "#ffffff";
            if (highlight_this_planet) {
                ctx.fillText(z, display_x, this.canvas.height - display_y - 5);
                ctx.fillText(planet.numShips + " (+" + planet.growthRate + ")",
                             display_x, this.canvas.height - display_y + 10);
            } else {
                ctx.fillText(planet.numShips, display_x, this.canvas.height - display_y + 5);
            }

        }

        // Draw Fleets
        this.ctx.font = this.config.fleet_font;
        for (let i = 0; i < fleets.length; i++) {
            const fleet = fleets[i];

            numShips[fleet.owner - 1] += fleet.numShips;

            const progress = (fleet.progress + 1 + (frame - frameNumber)) / (fleet.tripLength + 2);
            fleet.x = fleet.source.x + (fleet.destination.x - fleet.source.x) * progress;
            fleet.y = fleet.source.y + (fleet.destination.y - fleet.source.y) * progress;
            display_x = this.unitToPixel(fleet.x) + this.config.offset[0];
            display_y = this.unitToPixel(fleet.y) + this.config.offset[1];

            let color = this.config.teamColor[fleet.owner];
            if (this.active_planet >= 0
                    && (this.active_planet == fleet.destination_id || this.active_planet == fleet.source_id)) {
                color = this.config.teamColor_highlight[fleet.owner];
            }

            // Draw ship
            ctx.fillStyle = color;

            ctx.beginPath();
            ctx.save();
            ctx.translate(display_x, this.canvas.height - display_y);

            const scale = Math.log(Math.max(fleet.numShips, 4)) * 0.03;
            ctx.scale(scale, scale);

            let angle = Math.PI / 2 - Math.atan(
                (fleet.source.y - fleet.destination.y) / (fleet.source.x - fleet.destination.x)
            );

            if (fleet.source.x - fleet.destination.x < 0) {
                angle = angle - Math.PI;
            }

            ctx.rotate(angle);

            ctx.moveTo(  0, -10);
            ctx.lineTo( 40, -30);
            ctx.lineTo(  0, 100);
            ctx.lineTo(-40, -30);
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = "#ffffff";
            ctx.stroke();
            ctx.restore();

            // Draw text
            if (this.config.showFleetText === true) {
                angle = -1 * (angle + Math.PI / 2); // Switch the axis around a little
                display_x += -11 * Math.cos(angle);
                display_y += -11 * Math.sin(angle) - 5;
                ctx.fillText(fleet.numShips, display_x, this.canvas.height - display_y);
            }

            this.dirtyRegions.push([display_x - 25, this.canvas.height - display_y - 35, 60, 60])
        }

        $(this.canvas).trigger('drawn');

        // Update move indicator on chart
        this.drawChart(frame);

        // Update status next to usernames
        $('.player1Name').html(
            // '<a href="profile.php?user_id=' + Visualizer.playerIds[0] + '">' +
            '<a>' + Visualizer.players[0] + '</a><br />' + numShips[0] + ' (+' + production[0] + ')');
        $('.player1Name a').css({'color': Visualizer.config.teamColor[1], 'text-decoration': 'none'});

        $('.player2Name').html(
            // '<a href="profile.php?user_id=' + Visualizer.playerIds[1] + '">' +
            '<a>' + Visualizer.players[1] + '</a><br />' + numShips[1] + ' (+' + production[1] + ')');
        $('.player2Name a').css({'color': Visualizer.config.teamColor[2], 'text-decoration': 'none'})
    },

    drawChart: function (frame) {
        const canvas = document.getElementById('chart');
        const ctx = canvas.getContext('2d');
        ctx.lineWidth = 1.3;

        // This allows us to restore scale and translate
        ctx.restore();
        ctx.save();

        ctx.scale(1, -1);
        ctx.translate(0, -canvas.height);
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Total the ship counts
        let mostShips = 100;
        let mostProduction = 5;
        for (let i = 0; i < this.moves.length; i++) {
            const turn = this.moves[i];

            turn.shipCount = [0, 0, 0];
            turn.prodCount = [0, 0, 0];

            for (let j = 0; j < turn.moving.length; j++) {
                const fleet = turn.moving[j];
                turn.shipCount[fleet.owner] += fleet.numShips
            }

            for (let j = 0; j < turn.planets.length; j++) {
                const planet = turn.planets[j];
                turn.shipCount[planet.owner] += planet.numShips;
                turn.prodCount[planet.owner] += this.planets[j].growthRate;
            }

            for (let j = 0; j < turn.shipCount.length; j++) {
                mostShips = Math.max(mostShips, turn.shipCount[j])
            }

            for (let j = 0; j < turn.prodCount.length; j++) {
                mostProduction = Math.max(mostProduction, turn.prodCount[j])
            }
        }

        // Draw production graph
        let heightFactor = canvas.height / mostProduction / 1.05;
        let widthFactor = canvas.width / Math.max(200, this.moves.length);
        for (let i = 1; i <= 2; i++) {
            ctx.strokeStyle = this.config.planetColor[i];
            ctx.fillStyle = this.config.planetColor[i];
            ctx.beginPath();
            ctx.moveTo(0, this.moves[0].prodCount[i] * heightFactor);
            for (let j = 1; j < this.moves.length; j++) {
                const prodCount = this.moves[j].prodCount[i];
                ctx.lineTo(j * widthFactor, prodCount * heightFactor)
            }
            ctx.stroke();

            ctx.beginPath();
        }

        heightFactor = canvas.height / mostShips / 1.05;
        widthFactor = canvas.width / Math.max(200, this.moves.length);
        for (let i = 1; i <= 2; i++) {
            ctx.strokeStyle = this.config.teamColor[i];
            ctx.fillStyle = this.config.teamColor[i];
            ctx.beginPath();
            ctx.moveTo(0, this.moves[0].shipCount[i] * heightFactor);
            for (let j = 1; j < this.moves.length; j++) {
                const shipCount = this.moves[j].shipCount[i];
                ctx.lineTo(j * widthFactor, shipCount * heightFactor)
            }
            ctx.stroke();

            ctx.beginPath();
        }

        // Draw move indicator
        if (typeof frame != "undefined") {
            widthFactor = canvas.width / Math.max(200, this.moves.length);
            ctx.strokeStyle = "#666666";
            ctx.fillStyle = "#666666";
            ctx.beginPath();
            ctx.moveTo(widthFactor * frame, 0);
            ctx.lineTo(widthFactor * frame, canvas.height);
            ctx.stroke();
        }
    },

    start: function () {
        this.playing = true;
        setTimeout(function () {
            Visualizer.run.apply(Visualizer);
        }, 1);
        $("#play-button").html("&#9553;");
    },

    stop: function () {
        this.playing = false;
        this.frameDrawEnded = null;
        $('#play-button').html("&#9654;");
    },

    run: function () {
        if (this.frame > Visualizer.moves.length - 1) {
            this.frame = Visualizer.moves.length - 1;
            this.drawFrame(this.frame);
            this.stop();
        }

        if (!this.playing) return;

        this.frameDrawStarted = new Date().getTime();
        if (this.frameDrawEnded != null) {
            this.frame += (this.frameDrawStarted - this.frameDrawEnded) / 1000 * this.turnsPerSecond;
        }
        this.drawFrame(this.frame);
        this.frameDrawEnded = new Date().getTime();
        this.frame += (this.frameDrawEnded - this.frameDrawStarted) / 1000 * this.turnsPerSecond;

        setTimeout(function () { Visualizer.run.apply(Visualizer); }, 0);
    },

    setFrame: function (targetFrame) {
        this.frame = Math.max(0, Math.min(this.moves.length - 1, Math.floor(targetFrame)));
    },

    parseData: function (input) {
        input = input.split(/\n/);

        let data;
        if (input.length === 1)
            data = input[0];
        else {
            for (let i = 0; i < input.length; i++) {
                const value = input[i].split('=');
                switch (value[0]) {
                    case "player_one":
                        this.players[0] = value[1];
                        break;
                    case "player_two":
                        this.players[1] = value[1];
                        break;
                    case "playback_string":
                        data = value[1];
                        break;
                    case "user_one_id":
                        this.playerIds[0] = value[1];
                        break;
                    case "user_two_id":
                        this.playerIds[1] = value[1];
                        break;
                    case "error_message":
                        this.error_message = value[1];
                        break;
                    case "map_id":
                        this.map_id = value[1];
                        break;
                }
            }
        }

        data = data.split('|');

        // planets: [(x,y,owner,numShips,growthRate)]
        this.planets = data[0].split(':').map(ParserUtils.parsePlanet);

        // insert planets as first move
        this.moves.push({
            'planets': this.planets.map(function (a) {
                return {
                    owner: parseInt(a.owner),
                    numShips: parseInt(a.numShips),
                    growth: parseInt(a.growthRate)
                };
            }),
            'moving': []
        });

        // turns: [(owner,numShips)]
        // ++ [(owner,numShips,sourcePlanet,destinationPlanet,totalTripLength,turnsRemaining)]
        if (data.length < 2) {
            return // No turns.
        }
        const turns = data[1].split(':');
        for (let i = 0; i < turns.length; i++) {
            const turn = turns[i].split(',');
            const move = {};

            move.planets = turn.slice(0, this.planets.length).map(ParserUtils.parsePlanetState);
            let fleet_strings = turn.slice(this.planets.length);
            if (fleet_strings.length === 1 && fleet_strings[0] === '') {
                fleet_strings = []
            }
            move.moving = fleet_strings.map(ParserUtils.parseFleet);

            this.moves.push(move);
        }
    },

    updateActivePlanet: function (x, y) {
        x = this.pixelToUnit(x - this.config.offset[0]);
        y = this.pixelToUnit(y - this.config.offset[1]);

        let new_active_planet = -1;
        for (let i = this.planets.length - 1; i >= 0; --i) {
            let z = this.planetZOrder[i];
            const planet = this.planets[z];
            const size = this.pixelToUnit(this.config.planet_pixels[planet.growthRate]);
            const dx = x - planet.x;
            const dy = y - planet.y;
            if (dx * dx + dy * dy < size) {
                new_active_planet = z;
                break;
            }
        }

        if (new_active_planet !== this.active_planet) {
            this.active_planet = new_active_planet;
            this.switchPlanetZOrder(new_active_planet);
            this.drawFrame(Visualizer.frame);
        }
    },

    switchPlanetZOrder: function (id) {
        // this.planetZOrder can be one longer than the number of planets.
        // This is done to efficiently keep the sorted order of planets.
        // If some planet is active, then the value of the last element in the
        // array is set to be that planet's id.
        // Therefore, the array has length exactly the number of planets if and
        // only if there is no active planet, otherwise, it is exactly one
        // longer than the number of planets.
        if (id !== -1) {
            this.planetZOrder[this.planets.length] = id;
        } else if (this.planetZOrder.length > this.planets.length) {
            this.planetZOrder.pop();
        }
    },

    _eof: true
};


(function ($) {
    Visualizer.setup(data);

    const playAction = function () {
        if (!Visualizer.playing) {
            if (Visualizer.frame > Visualizer.moves.length - 2) {
                Visualizer.setFrame(0);
            }
            Visualizer.start();
        } else {
            Visualizer.stop();
        }
        return false;
    };
    $('#play-button').click(playAction);

    $('#start-button').click(function () {
        Visualizer.setFrame(0);
        Visualizer.drawFrame(Visualizer.frame);
        Visualizer.stop();
        return false;
    });

    $('#end-button').click(function () {
        Visualizer.setFrame(Visualizer.moves.length - 1);
        Visualizer.drawFrame(Visualizer.frame);
        Visualizer.stop();
        return false;
    });

    const prevAction = function () {
        Visualizer.setFrame(Visualizer.frame - 1);
        Visualizer.drawFrame(Visualizer.frame);
        Visualizer.stop();
        return false;
    };
    $('#prev-frame-button').click(prevAction);

    const nextAction = function () {
        Visualizer.setFrame(Visualizer.frame + 1);
        Visualizer.drawFrame(Visualizer.frame);
        Visualizer.stop();
        return false;
    };
    $('#next-frame-button').click(nextAction);


    const speeddownAction = function () {
        Visualizer.changeSpeed(-1);
        return false;
    };
    const speedupAction = function () {
        Visualizer.changeSpeed(+1);
        return false;
    };

    $('#speeddown').click(speeddownAction);
    $('#speedup').click(speedupAction);

    window.addEventListener("keydown", function (event) {
        if (event.code === "ArrowLeft") { // Left Arrow
            prevAction();
        } else if (event.code === "ArrowRight") { // Right Arrow
            nextAction();
        } else if (event.code === "Space") { // Space bar
            playAction();
        } else if (event.code === "ArrowDown") { // Down Arrow
            speeddownAction();
        } else if (event.code === "ArrowUp") { // Up Arrow
            speedupAction();
        } else {
            return true;
        }
        event.preventDefault();
        return false;
    }, true);

    const updateMove = function (evt) {
        const chart = $("#chart");
        const move = Math.max(200, Visualizer.moves.length) * (evt.pageX - chart.offset().left) / chart.width();
        Visualizer.setFrame(move);
        Visualizer.drawFrame(Visualizer.frame);
        Visualizer.stop();
        return false;
    };
    const moveAction = function (evt) {
        updateMove(evt);
        const chart = $("#chart");
        chart.bind('mousemove.chart', updateMove);
        $('body').bind('mouseup', function () {
            chart.unbind('mousemove.chart');
        });
    };
    $("#chart").mousedown(moveAction);

    let display = $('#display');

    display.mousemove(function (evt) {
        const display = $(this);
        const x = evt.pageX - display.offset().left;
        const y = evt.pageY - display.offset().top;

        Visualizer.updateActivePlanet(x, display.height() - y);
        return false;
    });

    display.mouseleave(function(evt) {
        // This should never be a planet due to the margins on the display.
        Visualizer.updateActivePlanet(0, 0);
        return false;
    })

    display.bind('drawn', function () {
        $('#turnCounter').text('Turn: ' + Math.floor(Visualizer.frame) + ' of ' + (Visualizer.moves.length - 1))
    });

    $('#error_message').text(Visualizer.error_message).css({'color': Visualizer.config.teamColor[1]});

    // $('.player1Name').html('<a href="profile.php?user_id=' + Visualizer.playerIds[0] + '">' + Visualizer.players[0] + '</a>');
    $('.player1Name a').css({'color': Visualizer.config.teamColor[1], 'text-decoration': 'none'});
    // $('.player2Name').html('<a href="profile.php?user_id=' + Visualizer.playerIds[1] + '">' + Visualizer.players[1] + '</a>');
    $('.player2Name a').css({'color': Visualizer.config.teamColor[2], 'text-decoration': 'none'});

    $('.playerVs').text('v.s.');
    $('title').text(Visualizer.players[0] + ' v.s. ' + Visualizer.players[1] + ' - Planet Wars');

    Visualizer.start();
    Visualizer.drawChart();
})(window.jQuery);
