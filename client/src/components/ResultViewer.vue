<template>
  <div v-if="entropies.length > 0">
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
          <label>
            <input type="checkbox" class="uk-checkbox" id="show-entropies" v-model="visualizeEntropies"/> Visualize entropies 
          </label>
          <a class="uk-button uk-button-text" id="open-colors" uk-icon="icon: pencil" @click="showModelColorMapping()"></a>
        </div>
      </div>
    </div>

    <div class="uk-flex uk-width-1-1" >
      <Split>
          <SplitArea :size="15" class="split-panel">
            <pre class="line-numbers">
              <span v-for="(entropy, key) in entropies" :key="key" class="line">{{entropy.toFixed(5)}}</span>
            </pre>        
          </SplitArea>
          <SplitArea :size="85" class="split-panel">
            <pre v-bind:class="{'token-framing': tokenFraming, 'use-colors': useColors, 'visualize-entropies': visualizeEntropies }" class="line-numbers">
              <span v-for="(tokens, key) in lines" :key="key" class="line"><span
                v-for="(token, k) in tokens" :key="k" 
                class="token" 
                v-tooltip="{placement: 'top', content: token.tooltip, boundariesElement: boundaryElement}" 
                v-bind:class="{'whitespace': token.isWhitespace}" 
                v-bind:style="{ color: token.color, backgroundColor: token.backgroundColor }"
                >{{token.text}}</span></span>
            </pre>
          </SplitArea>
      </Split>
    </div>

    <modal-color-mapping-entropy ref="modalColorMapping"></modal-color-mapping-entropy>
    
  </div>
</template>

<script>
export default {
  name: 'ResultViewer',
  data () {
    return {
      entropies: [],
      lines: [],
      colors: ['#BC2D0E', '#0E4CC8', '#AB0BAD', '#0C6407', '#AAA111', '#3F11AA', '#D9980D', '#402D03', '#37158C'],
      entropyToColorMapping: {},
      boundaryElement: undefined,
      tokenFraming: false,
      useColors: false,
      visualizeEntropies: false,
      optionsVisible: true,
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
      this.$refs.modalColorMapping.show();
    },
    mapEntropyToColor(entropy) {
      let colors = this.entropyToColorMapping;
      for (let i = 0; i < colors.length; i++) {
          let min = colors[i].min;
          let max = colors[i].max;
          let color = colors[i].color;
          if (entropy >= min && entropy < max) {
              return color;
          }
      }
      return colors[colors.length-1].color;
    },
    showEntropies(data) {
      this.entropyToColorMapping = this.$store.getters.colorMappingEntropy;
      this.entropies = [];
      this.lines = [];

      let currentColorIndex = 0;

      for (let i = 0; i < data.lines.length; i++) {
        let line = data.lines[i];
        let tokens = [];

        // parse line-entropy
        this.entropies.push(line.line_entropy);

        // parse token-entropies and tokens
        let remainingText = line.text;

        for (let j = 0; j < line.tokens.length; j++) {
          let token = line.tokens[j];
          let text = token.text.replace('</t>', '').replace(/\n/, '');

          let entropy = token.entropy;
          let tooltip = `'${text}' -> entropy: ${(entropy || 0).toFixed(3)}`
          let color = this.colors[currentColorIndex];

          // search text in line Text
          let found = false;
          let startIndex = 0;
          let endIndex = text.length;
          let iteration = 0;

          // special char: EOL
          if (token.text == '<EOL>') {
            let backgroundColor = this.mapEntropyToColor(entropy);

            tokens.push({
              isWhitespace: false,
              text: '',
              backgroundColor: backgroundColor,
              color: color,
              tooltip: `'EOL' -> entropy: ${(entropy || 0).toFixed(3)}`
            });
          } else {
            while (found === false) {
                if (remainingText.substring(startIndex, endIndex) == text) {
                    remainingText = remainingText.substring(endIndex);
  
                    let backgroundColor = this.mapEntropyToColor(entropy);
  
                    tokens.push({
                      isWhitespace: false,
                      text: text,
                      backgroundColor: backgroundColor,
                      color: color,
                      tooltip: tooltip
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

    }
  }
}
</script>

<style>

</style>
