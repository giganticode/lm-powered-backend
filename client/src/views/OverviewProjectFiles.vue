<template>
  <div>
    <h1>Project overview '{{project.name}}'</h1>
    <ul class="uk-list">
      <li class="" v-for="(file, hash) in project.files" :key="hash">
        <router-link :to="'/overview/'+projectHash+'/'+hash" class="uk-padding-small uk-display-block uk-card uk-card-body uk-card-default uk-link-toggle">
          <h3 class="uk-card-title"><span class="uk-link-heading">{{file.name}}</span></h3>
          <p>Relative-path: {{file.relpath}}</p>
          <p>Absolute-path: {{file.path}}</p>
        </router-link>
      </li>
      <li v-if="project.files.length === 0 && !loaded">
        <div class="uk-width-1-1 uk-text-center uk-padding loading">
          <div class="loading" uk-spinner="ratio: 3"></div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'home',
  data() {
    return {
      loaded: false,
      projectHash: "",
      project: {
        name: '',
        files: [],
      }     
    }
  },
  created() {
    // download models
    this.projectHash = this.$route.params.projecthash;
    this.downloadFiles();
  },
  methods: {
    downloadFiles() {
      this.$http
        .get("/api/project/" + this.projectHash)
        .then(response => {
          console.log("Got response models", response.data);
          this.project = response.data;        
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
          this.loaded = true;
        });
    },
  }
}
</script>
