<template>
  <div class="completion">
    <h1 @click="toggleInput()" class="uk-pointer noselect">Code completion <a class="uk-no-link" :uk-icon="'icon: ' + (!inputVisible ? 'chevron-down' : 'chevron-up') + '; ratio: 2'"></a></h1>
    <div v-if="inputVisible">
      <div class="uk-margin-small">
        Selected languagemodel: <b>{{$store.getters.currentModel}}</b> <a class="uk-button uk-button-text" @click="showModelSelectModel()" uk-icon="icon: pencil"></a>
      </div>

      <div class="uk-margin-small">
        <div class="uk-margin-small">
          <label>
            Context (min. 10 lines)
            <textarea class="uk-textarea" rows="10" v-model="content"></textarea>
          </label>
        </div>

        <div class="uk-margin-small">
          <label>
            Number of proposals
            <input class="uk-input" type="number" v-model="count" />
          </label>
        </div>

        <div class="uk-margin-small">
          <button class="uk-button uk-button-primary" type="button" @click="requestProposals()" >Request proposals</button>
        </div>
      </div>
    </div>

    <div v-if="proposals.length > 0">
      <h3 class="uk-margin-small">Proposals</h3>
      <div class="uk-width-1-1 uk-padding-small">
          <table class="uk-table uk-table-small uk-table-striped">
              <thead>
                  <tr>
                      <th class="uk-width-1-2 uk-text-right">Token</th>
                      <th class="uk-width-1-2 uk-text-left">Probabibility</th>
                  </tr>
              </thead>
              <tbody>
                <tr v-for="(item, key) in proposals" :key="key">
                  <td class="uk-text-right">{{item[0]}}</td>
                  <td class="uk-text-left">{{(item[1] * 100).toFixed(3)}} %</td>
                </tr>
              </tbody>
          </table>
      </div>
    </div>

    <metadata :metadata="metadata"></metadata>

    <modal-select-model ref="modalSelectModel"></modal-select-model>
    <modal-loading ref="modalLoading" @cancel="cancelRequest()"></modal-loading>

  </div>
</template>

<script>

export default {
  name: "LanguagemodelPrediction",
  data() {
    return {
      content: this.$store.getters.lastPredictionInput,
      count: 10,
      proposals: [],
      cancel: null,
      metadata: {},
      inputVisible: true,
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
    requestProposals() {
      this.$store.commit('lastPredictionInput', this.content);

      this.metadata = {};
      let currentModel = this.$store.getters.currentModel;
      
      let data = {
        extension: ".java",
        languageId: "java",
        timestamp: Date.now(),
        content: this.content,
        resetContext: true,
        proposalsCount: this.count,
        model: currentModel,
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
        .post("/api/autocompletion", data, cancelToken)
        .then(response => {
          console.log("Got response", response.data);

          this.proposals = response.data.predictions;
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