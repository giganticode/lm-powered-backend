<template>
  <div class="uk-text-center">
    <div>
      <h1>404 - Page not found</h1>
      <h3>Ooops, something went wrong</h3>
    
      <router-link to="/home">Home</router-link> | <a @click="goBack">Back</a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Page404',
  methods: {
   goBack() {
     this.$router.go(-1);
   }
  }
}
</script>
