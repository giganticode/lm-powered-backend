<template>
  <div ref="modal" uk-modal="esc-close:true;bg-close:false;stack:true">
      <div class="uk-modal-dialog uk-modal-body">
        <h2 class="uk-modal-title">Color mapping for difference in %</h2>
        <div class="colors">
          <div v-for="(color, key) in colors" :key="key" class="uk-margin-small">
            <label>
              Min % <input type="number" class="uk-input" v-model.number="color.min"/>
            </label>
            <label>
              Max % <input type="number" class="uk-input" v-model.number="color.max"/>
            </label>
            <label>
              <colorpicker :color="color.color" v-model="color.color" ></colorpicker>
            </label>
            <a class="uk-button uk-button-text" @click="deleteItem(key)" :uk-icon="'trash'"></a>
          </div>
          <div>
            <a class="uk-button uk-button-default" @click="addItem()" :uk-icon="'plus'"></a>
          </div>
        </div>
        <p class="uk-text-right">
          <button class="uk-button uk-button-default" @click="close" type="button">Cancel</button>
          <button class="uk-button uk-button-default" @click="reset" type="button">Reset</button>
          <button class="uk-button uk-button-primary" @click="select" type="button">Save</button>
        </p>
      </div>
  </div>
</template>

<script>

export default {
  name: 'ModalColorMappingPercent',
  data () {
    return {
      modal: null,
      colors: [],
    }
  },
  beforeDestroy() {
    if (this.modal !== null)
      this.modal.$destroy(true);
  },  
  methods: {
    show() {
      this.colors = [];
      if (this.modal === null)
        this.modal = UIkit.modal(this.$refs.modal);

      // clone colors
      this.colors = JSON.parse(JSON.stringify(this.$store.getters.colorMappingPercent));
      this.modal.show();
    },
    close() {
      this.modal.hide();
      this.colors = [];
    },
    reset() {
      let defaultColors = JSON.parse(JSON.stringify(this.$store.getters.defaultColorMappingPercent));
      this.colors = defaultColors;
    },
    select() {
      // check ranges for validity
      let errors = [];
      if (this.colors.length === 0) {
        errors.push('No colors')
      }
      else {
        let lastMax = 0;
        for (let i = 0; i < this.colors.length; i++) {
          let color = this.colors[i];
          if (color.min > color.max) {
            errors.push(`The minimum value of the range is smaller than the maximum value (range #${i+1})`);
          }
          if (color.min !== lastMax) {
            errors.push(`The minimum value of the range must be equal to the maximum value of the previous range (range #${i+1}) => minimum value should be '${lastMax}'`);
          }
          lastMax = color.max;
        }
      }

      if (errors.length > 0) {
        for (let key in errors) {
          UIkit.notification({
            message: errors[key],
            status: 'danger',
            pos: 'bottom-right',
            timeout: 4000
          });
        }
        return;
      }
      
      this.$store.commit('setColorMappingPercent', this.colors);
      this.modal.hide();
      this.colors = [];
    },
    deleteItem(key) {
      this.colors.splice(key, 1);
    },
    addItem() {
      let lastMax = 0;
      if (this.colors.length > 0) {
        lastMax = this.colors[this.colors.length - 1].max;
      }
      this.colors.push({min: lastMax, max: lastMax + 2, color: '#09921C'});
    }
  }
}
</script>

<style>

</style>
