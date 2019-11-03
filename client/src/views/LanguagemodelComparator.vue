<template>
  <div>
    <h1 @click="toggleInput()" class="uk-pointer noselect">Compare languagemodels <a class="uk-no-link" :uk-icon="'icon: ' + (!inputVisible ? 'chevron-down' : 'chevron-up') + '; ratio: 2'"></a></h1>
    <div v-if="inputVisible">
      <div class="uk-margin-small">

        <div class="uk-margin-small">
          Languagemodel 1: <b>{{this.$store.getters.currentModel}}</b> <a class="uk-button uk-button-text" @click="showModelSelectModel1()" uk-icon="icon: pencil"></a>
        </div>
          
        <div class="uk-margin-small">
          Languagemodel 2: <b>{{this.$store.getters.currentModel2}}</b> <a class="uk-button uk-button-text" @click="showModelSelectModel2()" uk-icon="icon: pencil"></a>
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

        <button class="uk-button uk-button-primary" type="button" @click="compareEntropies()">Compare models</button>
      </div>
    </div>

    <result-viewer-comparator ref="compareResultViewer" :caption-code="'Code'" :caption-diff="'Diff (%)'" :caption-first="'Original'" :caption-second="'Search'" class="uk-margin"></result-viewer-comparator>

    <metadata :metadata="metadata"></metadata>
  
    <modal-select-model ref="modalSelectModel" :modelName="'currentModel'"></modal-select-model>
    <modal-select-model ref="modalSelectModel2" :modelName="'currentModel2'"></modal-select-model>
    <modal-loading ref="modalLoading" @cancel="cancelRequest()"></modal-loading>

  </div>
</template>

<script>

export default {
  name: "EntropyComparator",
  data() {
    return {
      content: this.$store.getters.lastComparatorInput,
      metadata: {},
      cancel: null,
      metrics: 'full_token_entropy',
      tokenType: 'all',
      inputVisible: true,
    };
  },
  methods: {
    toggleInput() {
      this.inputVisible = !this.inputVisible;
    },
    showModelSelectModel1() {
      this.$refs.modalSelectModel.show();
    },
    showModelSelectModel2() {
      this.$refs.modalSelectModel2.show();
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
    compareEntropies() {
      this.$store.commit('lastComparatorInput', this.content);
      this.metadata = {};
      
      let data = {
        extension: ".java",
        languageId: "java",
        timestamp: Date.now(),
        content: this.content,
        resetContext: true,
        model1: this.$store.getters.currentModel,
        model2: this.$store.getters.currentModel2,
        metrics: this.metrics,
        tokenType: this.tokenType
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
        .post("/api/compare", data, cancelToken)
        .then(response => {
          console.log("Got response");
          console.log(response.data);
          let entropies1 = response.data.entropies1;
          let entropies2 = response.data.entropies2;

          this.$refs.compareResultViewer.showEntropies(entropies1, entropies2, data.metrics, data.tokenType);
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
.vertical-panes {
  width: 100%;
  height: 400px;
  border: 1px solid #ccc;
}
.vertical-panes > .pane {
  text-align: left;
  padding: 15px;
  overflow: hidden;
  background: #eee;
}
.vertical-panes > .pane ~ .pane {
  border-left: 1px solid #ccc;
}

textarea {
  resize: vertical;
}
</style>