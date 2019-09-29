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