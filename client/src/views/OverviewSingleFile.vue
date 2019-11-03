<template>
  <div>
    <div v-if="entropies.length === 0 && loaded == false" class="uk-width-1-1 uk-text-center uk-padding loading">
      <div class="loading" uk-spinner="ratio: 3"></div>
    </div>
    <div>
      <h1>{{file.name}}</h1>
      <result-viewer ref="resultViewer" class="uk-margin"></result-viewer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OverviewSingleFile',
  data() {
    return {
      entropies: [],
      file: {name: ''},
      loaded: false,
    }
  },
  created() {
    this.downloadFile();
  },
  methods: {
    downloadFile() {
      let projectHash = this.$route.params.projecthash;
      let fileHash = this.$route.params.filehash;
      this.$http
        .get(`/api/project/${projectHash}/${fileHash}`)
        .then(response => {
          console.log("Got response models", response.data);
          this.projects = response.data;

          this.file = response.data.file;
          this.entropies = response.data.entropies;

          this.$refs.resultViewer.showEntropies(this.entropies)         
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
          this.loaded = true
        });
    },
  }
}
</script>
