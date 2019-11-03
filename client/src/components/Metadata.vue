<template>
  <div class="uk-margin" v-if="Object.keys(metadata).length > 0">
    <h3 class="uk-margin-small noselect uk-pointer" @click="toggleContent()">Server-side-process information <a class="uk-no-link" :uk-icon="!contentVisible ? 'chevron-down' : 'chevron-up'"></a></h3>
    <div v-if="contentVisible">
      <div v-for="(item, key) in metadata" :key="key"><span>{{translateKey(key)}}</span> <b>{{item}} ms</b> </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Metadata',
  data() {
    return {
      contentVisible: true,
      keyMapping: {
        time_model_loading: 'Time needed to load the model:',
        time_model1_loading: 'Time needed to load the model1:',
        time_model2_loading: 'Time needed to load the model2:',
        time_entropy_calculation: 'Time needed to calculate the entropies:',
        time_entropy1_calculation: 'Time needed to calculate the entropies1:',
        time_entropy2_calculation: 'Time needed to calculate the entropies2:',
        time_feed: 'Time needed to feed the model:',
        time_predictions: 'Time needed to generate predictions:',
        total: 'Total server-side processing:',
        time_original_entropies: 'Time needed to calculate the entropies:',
        time_search_entropies: 'Time needed to calculate the searchentropies:',
      },
    };
  },
  props: {
    metadata: {
      default: {},
      type: Object
    }
  },
  methods: {
    toggleContent() {
      this.contentVisible = !this.contentVisible;
    },
    translateKey(key) {
      if (this.keyMapping[key]) {
        return this.keyMapping[key];
      }
      return key;
    }
  }
}
</script>

<style>

</style>
