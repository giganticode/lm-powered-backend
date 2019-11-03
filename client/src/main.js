// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

import UIkit from 'uikit';
window.UIkit = UIkit;
import Icons from 'uikit/dist/js/uikit-icons';
UIkit.use(Icons);

// components
import VueSplit from 'vue-split-panel'
Vue.use(VueSplit)

import VTooltip from 'v-tooltip';
Vue.use(VTooltip);

import ResultViewer from './components/ResultViewer';
import ResultViewerComparator from './components/ResultViewerComparator';
import ModalSelectModel from './components/ModalSelectModel';
import ModalColorMappingEntropy from './components/ModalColorMappingEntropy';
import ModalColorMappingPercent from './components/ModalColorMappingPercent';
import ColorPicker from './components/ColorPicker';
import ModalLoading from './components/ModalLoading';
import Metadata from './components/Metadata';

import { Chrome } from 'vue-color'
Vue.component('chrome-picker', Chrome);
Vue.component('colorpicker', ColorPicker);

Vue.component('result-viewer', ResultViewer);
Vue.component('result-viewer-comparator', ResultViewerComparator);
Vue.component('modal-select-model', ModalSelectModel);
Vue.component('modal-color-mapping-entropy', ModalColorMappingEntropy);
Vue.component('modal-color-mapping-percent', ModalColorMappingPercent);
Vue.component('modal-loading', ModalLoading);
Vue.component('metadata', Metadata);


import Axios from 'axios'

Axios.defaults.baseURL = 'http://localhost:8080';//  (process.env.NODE_ENV !== 'production') ? 'http://localhost/bgg/api/' : '';
Axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
Axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
Axios.defaults.headers.common.crossDomain = true;
// Axios.axios.defaults.baseURL = '/api'; // TODO:::
// Axios.defaults.baseURL = (process.env.NODE_ENV !== 'production') ? 'http://localhost/bgg/api/' : '';

Vue.prototype.$http = Axios;

// register components
// import { Multipane, MultipaneResizer } from 'vue-multipane';

// Vue.component('multipane', Multipane)
// Vue.component('multipane-resizer', MultipaneResizer)

import Vuex from 'vuex';
Vue.use(Vuex)
import storeData from './store';
const store = new Vuex.Store(storeData);

Vue.config.productionTip = false
/* eslint-disable no-new */
new Vue({
  el: '#app',
  store: store,
  router: router,
  components: { App },
  template: '<App/>',
  created() {
    // download models
    this.downloadModels();
  },
  methods: {
    downloadModels() {
      this.$http
        .get("/api/models")
        .then(response => {
          console.log("Got response models");
          console.log(response.data);
          this.$store.commit('modelsDownloaded', response.data.models);
          UIkit.notification({
            message: 'Models updated',
            status: 'success',
            pos: 'bottom-right',
            timeout: 1000
          });
        })
        .catch(error => {
          console.log(error);
          UIkit.notification({
            message: 'Error: could not download model information',
            status: 'danger',
            pos: 'bottom-right',
            timeout: 2500
          });
        })
        .finally(() => {
          // loading.hide();
          // btnSubmit.removeAttr('disabled');
        });
    },
  }
})
