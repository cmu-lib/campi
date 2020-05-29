<template>
  <div id="app">
    <b-navbar variant="light">
      <b-navbar-brand>CAMPI</b-navbar-brand>
      <b-navbar-nav v-if="logged_in">
        <b-nav-item :to="{name: 'Browse'}">Browse</b-nav-item>
        <b-nav-item :to="{name: 'Similarity'}">Similarity</b-nav-item>
      </b-navbar-nav>
      <b-navbar-nav class="ml-auto">
        <b-nav-item v-if="logged_in" :href="$APIConstants.API_LOGOUT">Logout</b-nav-item>
        <b-nav-item v-else :href="$APIConstants.API_LOGIN">Login</b-nav-item>
      </b-navbar-nav>
    </b-navbar>
    <router-view />
  </div>
</template>

<script>
import { HTTP } from "./main";
export default {
  name: "app",
  data() {
    return {
      logged_in: false
    };
  },
  mounted() {
    return HTTP.get("/", {}).then(
      response => {
        this.logged_in = !!response;
      },
      error => {
        console.log(error);
        this.logged_in = false;
      }
    );
  }
};
</script>


<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
