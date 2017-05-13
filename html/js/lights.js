const lights = [19, 13, 6, 5, 22, 27, 17, 4,
                18, 23, 24, 25, 12, 16, 20, 21];
const hours = ['00', '01', '02', '03', '04', '05', '06',
               '07', '08', '09', '10', '11', '12', '13',
               '14', '15', '16', '17', '18', '19', '20',
               '21', '22', '23'];

//Validate input of time textfields
function validateTimeInput() {
    let regTime = /^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$/

    let inputOn = $('#inputOn').val();
    let inputOff = $('#inputOff').val();

    if (inputOn.length > 0 && inputOff.length > 0) {
        if (regTime.test(inputOn) && regTime.test(inputOff)) {
            return true;
        }   
    }

    return false;
}

//Load time input fields & sequences from backend
function setTimeControls() {
    let updateTime = function(macro, args, response) {
        let time = response.split(";");
        $('#inputOn').val(time[0]);
        $('#inputOff').val(time[1]);    
    };

    webiopi().callMacro("getTime", [], updateTime)
}
function setSequences() {
    let updateSequences = function(macro, args, response) {
        let sequences = response.split(";");
        for (let i = 0; i < sequences.length - 1; i++) {
            $('#inputSequence').append($('<option>', {
                value : sequences[i],
                text : sequences[i]
            }));
        }
    };

    let selectCurrentSequence = function(macro, args, response) {
        let selected = response.substr(0, response.length - 4)
        $('#inputSequence').val(selected);
    };

    webiopi().callMacro("readAllSequences", [], updateSequences);
    webiopi().callMacro("getCurrentSequence", [], selectCurrentSequence);
}
//Create a button for every GPIO pin
function createGPIOButtons() {
    for (let i = 0; i < lights.length; i++) {
        let btn = webiopi().createGPIOButton(lights[i], "GPIO " + lights[i]);
        
        if (i < 8) {        
            $('#left-controls').append(btn);
        } else {
            $('#right-controls').append(btn);
        }
    }


    $('.controls button').each(function(index) {
        let indexStr;

        if (index > 7) {
            indexStr = (index + 3) + '';
        } else {
            indexStr = (index + 1) + '';
        }


        $(this).html(indexStr + '<br><span>(' +$(this).text() +')</span>')
    });
}

function addEventHandlers() {
    $('#stopStartButton').click(function () {
        if ($(this).text() === 'Stop') {
            webiopi().callMacro("stop", [], null);
            $(this).text('Start');
        } else {
            webiopi().callMacro("restart", [], null);
            $(this).text('Stop');
        }
        $('#error').text('');
    });
    $('#updateButton').click(function() {
        if (validateTimeInput()) {
            let time = [$('#inputOn').val(), $('#inputOff').val()];
            let sequence = $('#inputSequence').val() + '.txt';

            webiopi().callMacro("setTime", time, null);
            webiopi().callMacro("setCurrentSequence", sequence, null);
            webiopi().callMacro("writeToConfig", [], null);

            $('#error').css('color', '#0c0');
            $('#error').text('Gewijzigd!');
        } else {
            $('#error').css('color', '#f00');
            $('#error').text('Tijd moet in formaat hh:mm zijn!');
        }
    });
    $('#toggleAll').click(function() {
        webiopi().callMacro("toggleAllLights", [], null);
        $('#error').text('');
    });
    $('#manageSequences').click(function() {
        location.href = 'sequenties.html';
    });
}

//update status, start/stop button and all lights button
function setStatus() {
    let setupStatus = function(macro, args, response) {
        if (response === 'runningActive') {
            $('#status').text('Active and running...');
        } else if (response === 'active') {
            $('#status').text('Active...');
        } else {
            $('#status').text('Stopped...');
        }
    };

    let getStateMacro = webiopi().callMacro("getState", [], setupStatus);
    setTimeout(setStatus, 500);
}
function setStartStopButton() {
    let setupStartStopButton = function(macro, args, response) {
        if (response === 'runningActive') {
            $('#stopStartButton').text('Stop');
        } else if (response === 'active') {
            $('#stopStartButton').text('Stop');
        } else {
            $('#stopStartButton').text('Start');
        }
    };

    let getStateMacro = webiopi().callMacro("getState", [], setupStartStopButton);
    setTimeout(setStartStopButton, 500);
}
function setUpdateButton() {
    let setupUpdateButton = function(macro, args, response) {
        if (response === 'runningActive') {
            $('#updateButton').attr('disabled', true);
        } else if (response === 'active') {
            $('#updateButton').attr('disabled', true);
        } else {
            $('#updateButton').attr('disabled', false);
        }
    };

    let getStateMacro = webiopi().callMacro("getState", [], setupUpdateButton);
    setTimeout(setUpdateButton, 500);
}
function setAllLightsButton() {
    let setupAllLightsButton = function(macro, args, response) {
        if (response === 'runningActive') {
            $('#toggleAll').attr('disabled', true);
        } else if (response === 'active') {
            $('#toggleAll').attr('disabled', true);
        } else {
            $('#toggleAll').attr('disabled', false);
        }
    };

    let getStateMacro = webiopi().callMacro("getState", [], setupAllLightsButton);
    setTimeout(setAllLightsButton, 500);
}


//init
$(document).ready(function() {
    setTimeControls();
    setSequences();
    createGPIOButtons();
    addEventHandlers();

    //Recursive functions to update GUI
    setStatus();
    setUpdateButton();
    setStartStopButton();
    setAllLightsButton();

    webiopi().refreshGPIO(true);
});