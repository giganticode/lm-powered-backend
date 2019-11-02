function insertLines(params) {
    let props = {escapeHTML: true, target: {}, lines: ""};
    Object.assign(props, params)

    let stringArray = props.lines;
    if (typeof props.lines === 'string') {
        // cut off last newline-char, the LM is this doing as well
        if (props.lines.slice(-1) === '\n') {
            props.lines = props.lines.substring(0, props.lines.length - 1);
        }
        stringArray = props.lines.split('\n');
    }
    props.target.empty();
    for(let i = 0; i < stringArray.length; i++) {
        let item = stringArray[i];
        let newLine = $(`<span></span>`);
        if (props.escapeHTML) {
            newLine.text(item);
        } else {
            newLine.html(item);
        }
        props.target.append(newLine);
    }
}

 // define a sequence of colors to color the single tokens
 const colors = ['#BC2D0E', '#0E4CC8', '#AB0BAD', '#0C6407', '#AAA111', '#3F11AA', '#D9980D', '#402D03', '#37158C'];

 function formatEntropies(data, target, colorMapping) {
     target.empty();
     let currentColorIndex = 0;

     for (let i = 0; i < data.length; i++) {
         let line = data[i];
         let htmlLine = $('<span class="line"></span>');
         let remainingText = line.text;

         for (let j = 0; j < line.prep_text.length; j++) {
             let text = line.prep_text[j];
             text = text.replace('</t>', '');

             let entropy = line.results.bin_entropy[j];
             let color = colors[currentColorIndex];

             // search text in line Text
             let found = false;
             let startIndex = 0;
             let endIndex = text.length;
             let iteration = 0;
             while (found === false) {
                 if (remainingText.substring(startIndex, endIndex) == text) {
                     remainingText = remainingText.substring(endIndex);
                     let newSpan = $(`<span class="token">${text}</span>`);
                     newSpan.css('color', color);
                     htmlLine.append(newSpan);
                     let backgroundColor = mapEntropyToColor(entropy, colorMapping);
                     newSpan.css('background-color', backgroundColor);
                     UIkit.tooltip(newSpan, {title: `'${text}' -> entropy: ${(entropy || 0).toFixed(3)}`});
                     found = true;
                 }
                 else {
                     htmlLine.append($(`<span class="token whitespace"> </span>`));
                     startIndex++;
                     endIndex++;
                 }
                 if (iteration++ > 25){
                     break;
                 }
             }
             currentColorIndex = ++currentColorIndex % colors.length;
         }

         target.append(htmlLine);
     }
 }

 function mapEntropyToColor(entropy, colors) {
    for (let i = 0; i < colors.length; i++) {
        let min = colors[i].min;
        let max = colors[i].max;
        let color = colors[i].color;
        if (entropy > min && entropy <= max) {
            return color;
        }
    }
    return "transparent";
 }

 function displayMetadata(metadata, target) {
    target.empty();
    target.append($(`<h3>Server-side-process information</h3>`))
    target.append($(`<span>Time needed to load the model: <b>${metadata.time_model_loading}ms</b></span>`))
    target.append($(`</br>`))
    target.append($(`<span>Time needed to calculate the entropies: <b>${metadata.time_entropy_calculation}ms</b></span>`))
    target.append($(`</br>`))
    target.append($(`<span>Total server-side processing: <b>${metadata.total}ms</b></span>`))
    target.append($(`</br>`))
 }

 $(document).ready(function() {
    let modalSelectModel = UIkit.modal($('#modal-select-model'), {bgClose: false, escClose: false});
    let modalColorMapping = UIkit.modal($('#modal-color-mapping'), {bgClose: false, escClose: false});

    if (localStorage.getItem('colorMapping')) {
        try {
            colorMapping = JSON.parse(localStorage.getItem('colorMapping'));
        } catch(e) {
            // alert(e); // error in the above string (in this case, yes)!
            // use default color mapping
        }
    }

    /* color mapping */
    for (let i = 0; i < colorMapping.length; i++) {
        let color = colorMapping[i].color;
        let min = colorMapping[i].min;
        let max = colorMapping[i].max;
        
        let htmlItem = $(`
        <div>
            <label>
                Min <input type="number" class="uk-input" value="${min}" id="min-${i}">
            </label>
            <label>
                Max <input type="number" class="uk-input" value="${max}" id="max-${i}">
            </label>
            Color: <input id="color-${i}" type='text'>
        </div>`);
        $('#colors').append(htmlItem);

        $(`#color-${i}`).spectrum({
            color: color,
            showAlpha: false,
            clickoutFiresChange: false,
            preferredFormat: "hex",
            showInput: true,
            change: function(color) {
                // console.log("change", color)
                // console.log(color.toHexString()); // #ff0000
                colorMapping[i].color = color.toHexString();
                // todo save colors in localStorage
            }
        })
    }

    $('#open-colors').click(function(e) {
        e.preventDefault();
        modalColorMapping.show();
    });

    $('#modal-color-mapping-save').click(function(e) {
        let lastMax = 0;
        let error = false;
        // validate min/max
        for (let i = 0; i < colorMapping.length; i++) {
            let min = parseFloat($(`#min-${i}`).val());
            let max = parseFloat($(`#max-${i}`).val());
            colorMapping[i].min = min;
            colorMapping[i].max = max;

            console.log("Iteration: ", i, min, max)

            if (min > max) {
                error = "Incorrect values";
                console.log("min > max", i, min, max)
                $(`#min-${i}`).focus();
                break;
            }

            if (min != lastMax) {
                error = `Incorrect values, the value should be '${lastMax}'`;
                console.log("min != lastMax", i, min, lastMax)
                $(`#min-${i}`).focus();
                break;
            }

            lastMax = max;
        }

        if (error !== false) {
            UIkit.notification({message: error, status: 'danger', pos: 'top-right'})
        } else {
            modalColorMapping.hide();
            let jsonEncoded = JSON.stringify(colorMapping);
            localStorage.setItem('colorMapping', jsonEncoded);
            UIkit.notification({message: "Configuration was saved successfully. Please recalculate the entropies to see the changes.", status: 'success', pos: 'top-right'})
        }

    });

    $('#modal-color-mapping-abort').click(function(e) {
        modalColorMapping.hide();
        colorMapping = localStorage.getItem('colorMapping') || defaultColorMapping;
    });
    /* end color mapping */



    if (!availableModels.includes(currentModel)) {
        currentModel = availableModels[0];
        currentModelName = availableModelNames[0];
        localStorage.setItem("selectedModel", currentModel);
        localStorage.setItem("selectedModelName", currentModelName);
    }

    function saveCurrentModel(selectedModel, selectedModelName) {
        localStorage.setItem("selectedModel", selectedModel);
        localStorage.setItem("selectedModelName", selectedModelName);
        currentModel = selectedModel;
        currentModelName = selectedModelName;
    }

    displayCurrentModel();

    function displayCurrentModel() {
        $('#current-model').text(currentModelName);
    }

    $('#open-selectlm-modal').click(function(e) {
        $('#lm-select').val(currentModel);
        if (!$('#lm-select').val()) {
            $("#lm-select").val($("#lm-select option:first").val());
        }
        $('#lm-select').change();
        modalSelectModel.show();
    });

    $('#modal-save').click(function(e) {
        let selectedModel = $('#lm-select').val();
        let selectedModelName = $("#lm-select option:selected").text();
        saveCurrentModel(selectedModel, selectedModelName);
        modalSelectModel.hide();
        displayCurrentModel();
    });

    $('#modal-abort').click(function(e) {
        modalSelectModel.hide();
    });

    $('#lm-select').change(function(e) {
        let selectedLM = $(this).val();
        $(`[data-identifier]`).hide();
        $(`[data-identifier="${selectedLM}"]`).show();
    });


 });