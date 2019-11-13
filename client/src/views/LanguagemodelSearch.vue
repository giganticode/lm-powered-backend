<template>
  <div>
    <h1 @click="toggleInput()" class="uk-pointer noselect">Contextual search <a class="uk-no-link" :uk-icon="'icon: ' + (!inputVisible ? 'chevron-down' : 'chevron-up') + '; ratio: 2'"></a></h1>
    <div v-if="inputVisible">
      <div class="uk-margin-small">
        Selected languagemodel: <b>{{$store.getters.currentModel}}</b> <a class="uk-button uk-button-text" @click="showModelSelectModel()" uk-icon="icon: pencil"></a>
      </div>

      <div class="uk-margin-small">
        <div class="uk-margin-small uk-grid uk-grid-small">
          <div class="uk-width-1-1 uk-width-3-4@s">
            <label>
              Search query
              <input class="uk-input" v-model="search" />
            </label>
          </div>

          <div class="uk-width-1-1 uk-width-1-4@s">
            <label>
              Search interval
              <input class="uk-input" type="text" v-model.number="interval" />
            </label>
          </div>
        </div>

        <div class="uk-margin-small uk-grid uk-grid-small">
          <label class="uk-width-1-2@s uk-width-1-1">
            Metrics
            <select class="uk-select" v-model="metrics">
              <option v-for="(item, key) in $store.getters.metrics" :key="key">{{item}}</option>
            </select>
          </label>
          <label class="uk-width-1-2@s uk-width-1-1">
            Token-types
            <select class="uk-select" v-model="tokenType">
              <option v-for="(item, key) in $store.getters.tokenTypes" :key="key">{{item}}</option>
            </select>
          </label>
        </div>

        <div class="uk-margin-small">
          <label>
            Code
            <textarea class="uk-textarea" rows="10" v-model="content"></textarea>
          </label>
        </div>

        <button class="uk-button uk-button-primary" type="button" @click="sendSearchQuery()">Search</button>
      </div>
    </div>

    <result-viewer-comparator ref="compareResultViewer" :caption-code="'Code'" :caption-diff="'Diff (%)'" :caption-first="'Original'" :caption-second="'Search'" class="uk-margin"></result-viewer-comparator>

    <metadata :metadata="metadata"></metadata>

    <modal-select-model ref="modalSelectModel"></modal-select-model>
    <modal-loading ref="modalLoading" @cancel="cancelRequest()"></modal-loading>

  </div>
</template>

<script>

export default {
  name: "LanguagemodelSearch",
  data() {
    return {
      content: this.$store.getters.lastSearchInput,
      metadata: {},
      interval: 10,
      search: "Query",
      cancel: null,
      metrics: 'full_token_entropy',
      tokenType: 'all',
      inputVisible: true
    };
  },
  methods: {
    toggleInput() {
      this.inputVisible = !this.inputVisible;
    },
    showModelSelectModel() {
      this.$refs.modalSelectModel.show();
    },
    showModelColorMapping() {
      this.$refs.modalColorMapping.show();
    },
    cancelRequest() {
      if (this.cancel) {
        this.cancel();
      }
      this.$refs.modalLoading.hide();
    },
    sendSearchQuery() {
      this.$store.commit('lastSearchInput', this.content);

      this.metadata = {};
      let currentModel = this.$store.getters.currentModel;
      
      let data = {
        extension: ".java",
        languageId: "java",
        timestamp: Date.now(),
        content: this.content,
        resetContext: true,
        searchInterval: this.interval,
        model: currentModel,
        search: this.search,
        metrics: this.metrics,
        tokenType: this.tokenType,        
      };

      this.$refs.modalLoading.show();

      let CancelToken = this.$http.CancelToken;
      let me = this;

      let cancelToken = {
        cancelToken: new CancelToken(function executor(c) {
          me.cancel = c;
        })
      }

      this.$http
        .post("/api/search", data, cancelToken)
        .then(response => {
          console.log("Got response", response.data);

          let entropies = response.data.entropies;
          entropies.original.lines = entropies.original.lines.filter((e, i) => i % this.interval != 0);
          entropies.search.lines = entropies.search.lines.filter((e, i) => i % this.interval != 0);

          this.$refs.compareResultViewer.showEntropies(entropies.original, entropies.search);

          this.metadata = response.data.metadata;
        })
        .catch(error => {
          console.log(error);
          UIkit.notification({
            message: error,
            status: 'danger',
            pos: 'bottom-right',
            timeout: 4000
          });          
        })
        .finally(() => {
           this.$refs.modalLoading.hide();
        });
      }
    }
  };
</script>

<style>

</style>