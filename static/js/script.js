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

 function formatEntropies(data, target) {
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
                     UIkit.tooltip(newSpan, {title: `'${text}' -> entropy: ${entropy.toFixed(3)}`});
                     found = true;
                 }
                 else {
                     htmlLine.append($(`<span class="token"> </span>`));
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