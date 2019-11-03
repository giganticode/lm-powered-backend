<template>
  <div class="about">

    <h1>Available languagemodels</h1>
    <ul class="uk-list">

      <li v-for="(model, index) in models" :key="index" class="uk-padding-small uk-display-block uk-card uk-card-body uk-card-default">
        <h4><b>{{index}}</b></h4>
        <p>
          <b>Description</b><br>
          Arch: {{model.arch}}<br>
          Best epoch: {{model.best_epoch}}<br>
          Bin entropy: {{model.bin_entropy}}<br>
          Bpe merges: {{model.bpe_merges}}<br>
          Layers config: {{model.layers_config}}<br>
          Epochs: {{model.n_epochs}}<br>
          Training time per epoch: {{model.training_time_minutes_per_epoch}} minutes<br>
          Tags: {{model.tags}}<br>
        </p>
      </li>

    </ul>

    <h1>Color mapping</h1>
    <ul class="uk-list">

      <li class="uk-padding-small uk-display-block uk-card uk-card-body uk-card-default">
        <h4><b>Color mapping for entropy values</b></h4>
        <div><a @click="showColorMappingEntropy">Edit current color mapping for entropy values <span uk-icon="icon: pencil"></span></a></div>
      </li>

      <li class="uk-padding-small uk-display-block uk-card uk-card-body uk-card-default">
        <h4><b>Color mapping for difference in percent</b></h4>
        <div><a @click="showColorMappingPercent">Edit current color mapping for difference in percent <span uk-icon="icon: pencil"></span></a></div>
      </li>

    </ul>
  
    <modal-color-mapping-entropy ref="modalColorMappingEntropy"></modal-color-mapping-entropy>
    <modal-color-mapping-percent ref="modalColorMappingPercent"></modal-color-mapping-percent>

  </div>
</template>

<script>
export default {
  name: 'About',
  data() {
    return {
      models: this.$store.getters.models,
    }
  },
  methods: {
    showColorMappingEntropy() {
      this.$refs.modalColorMappingEntropy.show();
    },
    showColorMappingPercent() {
      this.$refs.modalColorMappingPercent.show();
    },
  }
}
</script>
