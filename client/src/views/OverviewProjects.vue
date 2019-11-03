<template>
  <div>
    <h1>Project overview</h1>
    <ul class="uk-list">
      <li class="" v-for="(project, index) in projects" :key="index">
            <router-link :to="'overview/'+project.url" class="uk-padding-small uk-display-block uk-card uk-card-body uk-card-default uk-link-toggle">
              <h3 class="uk-card-title"><span class="uk-link-heading">Project-name: <b>{{project.name}}</b></span></h3>
              <p>Path: {{project.path}}</p>
          </router-link>
      </li>
      <li v-if="projects.length === 0 && !loaded">
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
      projects: [
        
      ]
    }
  },
  created() {
    // download models
    this.downloadProjects();
  },
  methods: {
    downloadProjects() {
      this.$http
        .get("/api/projects")
        .then(response => {
          console.log("Got response models", response.data);
          this.projects = response.data;
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
