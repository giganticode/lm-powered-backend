<template>
  <div class="home">
    <h1 @click="toggleInput()" class="uk-pointer noselect">Languagemodel-debugger <a class="uk-no-link" :uk-icon="'icon: ' + (!inputVisible ? 'chevron-down' : 'chevron-up') + '; ratio: 2'"></a></h1>

    <div v-if="inputVisible">
      <div class="uk-margin-small">
        Selected languagemodel: <b>{{$store.getters.currentModel}}</b> <a class="uk-button uk-button-text" @click="showModelSelectModel()" uk-icon="icon: pencil"></a>
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
        <p>
          <label>
            Code
            <textarea class="uk-textarea" rows="10" id="content" name="content" v-model="content"></textarea>
          </label>
        </p>

        <button class="uk-button uk-button-primary" type="button" @click="calculateEntropies()">Calculate entropies</button>
      </div>
    </div>

    <result-viewer ref="resultViewer" class="uk-margin"></result-viewer>

    <metadata :metadata="metadata"></metadata>

    <modal-select-model ref="modalSelectModel"></modal-select-model>
    <modal-loading ref="modalLoading" @cancel="cancelRequest()"></modal-loading>

  </div>
</template>

<script>

export default {
  name: "LanguagemodelDebugger",
  data() {
    return {
      content: this.$store.getters.lastDebuggerInput,
      metadata: {},
      cancel: null,
      metrics: 'full_token_entropy',
      tokenType: 'all',
      inputVisible: true
    };
  },
  mounted() {},
  beforeDestroy() {},
  created() {},
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
    calculateEntropies() {
      this.$store.commit('lastDebuggerInput', this.content);

      this.metadata = {};
      let currentModel = this.$store.getters.currentModel;
      
      let data = {
        extension: ".java",
        languageId: "java",
        // filePath: "demo/temp",
        noReturn: false,
        timestamp: Date.now(),
        content: this.content,
        resetContext: true,
        model: currentModel,
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
        .post("/api/languagemodel", data, cancelToken)
        .then(response => {
          console.log("Got response");
          console.log(response.data);
          let entropies = response.data.entropies;
          this.$refs.resultViewer.showEntropies(entropies);

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