<template>
  <div uk-modal="esc-close:true;bg-close:false;stack:true" ref="modal">
    <div class="uk-modal-dialog uk-modal-body">
      <h2 class="uk-modal-title">Select a languagemodel</h2>
      <p>
        <select class="uk-select" v-model="displayedModel">
          <option :value="item" v-for="(item, key) in models" :key="key">{{item.id}}</option>
        </select>
      </p>
      <p>
        <b>Description</b><br>
        Arch: {{displayedModel.arch}}<br>
        Best epoch: {{displayedModel.best_epoch}}<br>
        Bin entropy: {{displayedModel.bin_entropy}}<br>
        Bpe merges: {{displayedModel.bpe_merges}}<br>
        Layers config: {{displayedModel.layers_config}}<br>
        Epochs: {{displayedModel.n_epochs}}<br>
        Training time per epoch: {{displayedModel.training_time_minutes_per_epoch}} minutes<br>
        Tags: {{displayedModel.tags}}<br>
      </p>

      <p class="uk-text-right">
        <button class="uk-button uk-button-default" @click="close()" type="button">Cancel</button>
        <button class="uk-button uk-button-primary" @click="select()" type="button">Select</button>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModalSelectModel',
  data () {
    return {
      modal: null,
      models: [],
      displayedModel: {},
    }
  },
  props: {
    commit: {
      default: true,
      type: Boolean
    },
    modelName: {
      default: 'currentModel', 
      type: String
    }
  },
  beforeDestroy() {
    if (this.modal !== null)
      this.modal.$destroy(true);
  },  
  methods: {
    show() {
      if (this.modal === null)
        this.modal = UIkit.modal(this.$refs.modal);
      this.models = this.$store.getters.models;
      
      let selectedModelID = this.$store.getters[this.modelName];
      this.displayedModel = this.models[selectedModelID];

      this.modal.show();
    },
    close() {
      this.modal.hide();
    },
    select() {
      if (this.displayedModel == null || !this.displayedModel.id) {
        UIkit.modal.alert('Please select a model!').then(function () {});
      } else {
        if (this.commit) {
          this.$store.commit(this.modelName, this.displayedModel.id);
        }
        this.$emit('selected', this.displayedModel)
        this.modal.hide();
      }
      this.displayedModel = {};
    }
  }
}
</script>

<style>

</style>
