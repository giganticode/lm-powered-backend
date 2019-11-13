<template>
  <div v-if="lines.length > 0">
    
    <div class="entropy-settings uk-margin-small">
      <h3 class="uk-margin-small noselect uk-pointer" @click="toggleOptions()">Options <a class="uk-no-link" :uk-icon="!optionsVisible ? 'chevron-down' : 'chevron-up'"></a></h3>
      <div v-if="optionsVisible">
        <label class="uk-display-block">
          <input type="checkbox" class="uk-checkbox" id="show-borders" v-model="tokenFraming"/> Token framing
        </label>
      
        <label class="uk-display-block">
          <input type="checkbox" class="uk-checkbox" id="show-colors" v-model="useColors"/> Use colors to distinguish tokens
        </label>
        
        <div>
            <div class="uk-form-label">Visualize entropies <a v-if="visualizeEntropies !== 'none'" class="uk-button uk-button-text" id="open-colors" uk-icon="icon: pencil" @click="showModelColorMapping()"></a></div>
            <div class="uk-form-controls">
                <label><input class="uk-radio" type="radio" value="none" name="visualize-entropies" v-model="visualizeEntropies" @change="updateBackgroundColors"> None</label><br>
                <label><input class="uk-radio" type="radio" value="diff" name="visualize-entropies" v-model="visualizeEntropies" @change="updateBackgroundColors"> Difference</label><br>
                <label><input class="uk-radio" type="radio" value="first" name="visualize-entropies" v-model="visualizeEntropies" @change="updateBackgroundColors"> Entropies of first model</label><br>
                <label><input class="uk-radio" type="radio" value="second" name="visualize-entropies" v-model="visualizeEntropies" @change="updateBackgroundColors"> Entropies of second model</label>
            </div>
        </div>
      </div>

    </div>      

    <div class="uk-flex uk-width-1-1" >
      <Split>
          <SplitArea :size="55" class="split-panel">
            <p class="uk-margin-remove uk-text-center">{{captionCode}}</p>
            <pre v-bind:class="{'token-framing': tokenFraming, 'use-colors': useColors, 'visualize-entropies': visualizeEntropies !== 'none' }" class="line-numbers">
              <span v-for="(tokens, key) in lines" :key="key" class="line"><span
                v-for="(token, k) in tokens" :key="k" 
                class="token" 
                v-tooltip="{placement: 'top', content: token.tooltip, boundariesElement: boundaryElement}" 
                v-bind:class="{'whitespace': token.isWhitespace}" 
                v-bind:style="{ color: token.color, backgroundColor: token.backgroundColor }"
                >{{token.text}}</span></span>
            </pre>
          </SplitArea>
          <SplitArea :size="15" class="split-panel">
            <p class="uk-margin-remove uk-text-center">{{captionDiff}}</p>
            <pre class="line-numbers">
              <span v-for="(entropy, key) in entropies.difference" :key="key" class="line">{{entropy.toFixed(3)}}</span>
            </pre>        
          </SplitArea>
          <SplitArea :size="15" class="split-panel">
            <p class="uk-margin-remove uk-text-center">{{captionFirst}}</p>
            <pre class="line-numbers">
              <span v-for="(entropy, key) in entropies.first" :key="key" class="line">{{entropy.toFixed(5)}}</span>
            </pre>        
          </SplitArea>
          <SplitArea :size="15" class="split-panel">
            <p class="uk-margin-remove uk-text-center">{{captionSecond}}</p>
            <pre class="line-numbers">
              <span v-for="(entropy, key) in entropies.second" :key="key" class="line">{{entropy.toFixed(5)}}</span>
            </pre>        
          </SplitArea>
      </Split>
    </div>

    <modal-color-mapping-entropy ref="modalColorMapping"></modal-color-mapping-entropy>
    <modal-color-mapping-percent ref="modalColorMappingPercent"></modal-color-mapping-percent>

  </div>

</template>

<script>
export default {
  name: 'ResultViewerComparator',
  data () {
    return {
      entropies: {first: [], second: [], difference: []},
      lines: [],
      colors: ['#BC2D0E', '#0E4CC8', '#AB0BAD', '#0C6407', '#AAA111', '#3F11AA', '#D9980D', '#402D03', '#37158C'],
      entropyColorMapping: [],
      differenceColorMapping: [],
      boundaryElement: undefined,
      visualizeEntropies: 'none',
      useColors: false,
      tokenFraming: false,
      optionsVisible: true,
    }
  },
  props: {
    captionCode: {
      default: "Code",
      type: String
    },
    captionDiff: {
      default: "Difference",
      type: String
    },
    captionFirst: {
      default: "Entropy",
      type: String
    },
    captionSecond: {
      default: "Entropy",
      type: String
    }
  },
  mounted() {
    this.boundaryElement = document.body;
  },
  methods: {
    toggleOptions() {
      this.optionsVisible = !this.optionsVisible;
    },
    showModelColorMapping() {
      if (this.visualizeEntropies === 'diff') {
        this.$refs.modalColorMappingPercent.show();
      } else if (this.visualizeEntropies !== 'none') {
        this.$refs.modalColorMapping.show();
      }
    },

    updateBackgroundColors() {
      if (this.visualizeEntropies === 'none') {
        return;
      }
      for (let i = 0; i < this.lines.length; i++) {
        let tokens = this.lines[i];
        for (let j = 0; j < tokens.length; j++) {
          let token = tokens[j];
          if (!token.isWhitespace) {
            let backgroundColor = this.mapTokenToColor(token);
            token.backgroundColor = backgroundColor;
          }
        }
      }
    },

    mapTokenToColor(token) {
      let value = '';
      let colors = this.entropyColorMapping;
      if (this.visualizeEntropies === 'diff') {
        value = token.entropyDiff;
        colors = this.differenceColorMapping;
      } else if (this.visualizeEntropies === 'first') {
        value = token.entropy1;
      } else if (this.visualizeEntropies === 'second') {
        value = token.entropy2;
      } 

      let backgroundColor = this.mapEntropyToColor(value, colors);
      return backgroundColor;
    },

    mapEntropyToColor(value, colors) {
      for (let i = 0; i < colors.length; i++) {
          let min = colors[i].min;
          let max = colors[i].max;
          let color = colors[i].color;
          if (value >= min && value < max) {
              return color;
          }
      }
      return colors[colors.length-1].color;
    },

    clearData() {
      this.entropies = [];
      this.lines = [];
    },

    showEntropies(first, second) {
      this.entropyColorMapping = this.$store.getters.colorMappingEntropy,
      this.differenceColorMapping = this.$store.getters.colorMappingPercent,
      this.entropies = {first: [], second: [], difference: []};
      this.lines = [];

      if (first.length != second.length) {
        console.log("line numbers of both entropy-results must match")
        return;
      }

      let currentColorIndex = 0;

      for (let i = 0; i < first.lines.length; i++) {
        let firstLine = first.lines[i];
        let secondLine = second.lines[i];
        let tokens = [];

        // parse line-entropy
        this.entropies.first.push(firstLine.line_entropy);
        this.entropies.second.push(secondLine.line_entropy);

        let diff = firstLine.line_entropy / secondLine.line_entropy;
        diff = ((diff < 1 ? 1 / diff : diff) - 1) * 100;
        diff = isNaN(diff) ? 0 : diff
        this.entropies.difference.push(diff);

        // parse token-entropies and tokens
        if (firstLine.text != secondLine.text) {
          console.error("text of line " + i + " does not match")
          return;
        }
        let remainingText = firstLine.text;

        for (let j = 0; j < firstLine.tokens.length; j++) {
          let firstToken = firstLine.tokens[j];
          let secondToken = secondLine.tokens[j];
          let text = firstToken.text.replace('</t>', '').replace(/\n/, '');

          let color = this.colors[currentColorIndex];

          // search text in line Text
          let found = false;
          let startIndex = 0;
          let endIndex = text.length;
          let iteration = 0;

          // special char: EOL
          if (firstToken.text == '<EOL>') {
            let firstEntropy = firstToken.entropy || 0;
            let secondEntropy = secondToken.entropy || 0;

            let diff = firstEntropy / secondEntropy;
            diff = ((diff < 1 ? 1 / diff : diff) - 1) * 100
            diff = isNaN(diff) ? 0 : diff

            tokens.push({
              isWhitespace: false,
              text: '',
              backgroundColor: 'transparent',
              color: color,
              entropy1: firstEntropy,
              entropy2: secondEntropy,
              entropyDiff: diff,
              tooltip: `'EOL' -> entropy: ${firstEntropy.toFixed(3)} <=> ${secondEntropy.toFixed(3)} (diff: ${diff.toFixed(2)} %)`,
            });
          } else {
            while (found === false) {
              let firstEntropy = firstToken.entropy || 0;
              let secondEntropy = secondToken.entropy || 0;

              let diff = firstEntropy / secondEntropy;
              diff = ((diff < 1 ? 1 / diff : diff) - 1) * 100
              diff = isNaN(diff) ? 0 : diff
              
              if (remainingText.substring(startIndex, endIndex) == text) {
                remainingText = remainingText.substring(endIndex);

                tokens.push({
                  isWhitespace: false,
                  text: text,
                  backgroundColor: 'transparent',
                  color: color,
                  entropy1: firstEntropy,
                  entropy2: secondEntropy,
                  entropyDiff: diff,
                  tooltip: `'${text}': ${firstEntropy.toFixed(3)} <=> ${secondEntropy.toFixed(3)} (diff: ${diff.toFixed(2)} %)`,
                });

                found = true;
              }
              else {
                tokens.push({
                  isWhitespace: true,
                  text: ' ',
                  color: '',
                  backgroundColor: ''
                });
                startIndex++;
                endIndex++;
              }
              if (iteration++ > 25){
                break;
              }
            }
          }
          currentColorIndex = ++currentColorIndex % this.colors.length;
        }

        this.lines.push(tokens);

      }
      this.updateBackgroundColors();
    }
  }
}
</script>

<style>

</style>
