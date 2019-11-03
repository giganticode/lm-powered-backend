<template>
  <div>
    <h1>Visualizing contextual information within Visual Studio Code</h1>
    <ul class="uk-list">
      <li class="" v-for="(route, index) in routes" :key="index">
            <router-link :to="route.url" class="uk-padding-small uk-display-block uk-card uk-card-body uk-card-default uk-link-toggle">
              <div class="uk-grid">
                  <div class="uk-width-auto uk-flex uk-flex-middle uk-flex-center">
                      <span :uk-icon="'icon: ' + route.icon + '; ratio: 2'"></span>
                  </div>
                  <div class="uk-with-expand">
                      <h3 class="uk-card-title"><span class="uk-link-heading">{{route.name}}</span></h3>
                      <p>{{route.description}}</p>
                  </div>
              </div>
          </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'home',
  data() {
    return {
      routes: [
        {url: "/debugger", name: "Languagemodel-Debugger", description: "Debug a single file in a web editor", icon: "code"},
        {url: "/comparator", name: "Languagemodel-Comparator", description: "Compare the output of two languagemodels", icon: "code"},
        {url: "/prediction", name: "Prediction", description: "Show proposals based on some context", icon: "future"},
        {url: "/search", name: "Contextual search", description: "Perform contextual search queries", icon: "search"},
        {url: "/overview", name: "Project overview", description: "Show all cached projects and files", icon: "database"},
        {url: "/about", name: "About", description: "Show information about the current environment setup", icon: "info"},
      ]
    }
  }
}
</script>
