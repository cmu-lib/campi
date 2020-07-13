<template>
  <div id="app">
    <b-navbar variant="light">
      <b-navbar-brand :to="{name: 'Home'}">CAMPI</b-navbar-brand>
      <b-navbar-nav v-if="logged_in">
        <b-nav-item :to="{name: 'Browse'}">Browse</b-nav-item>
        <b-nav-item :to="{name: 'CloseMatch'}">Close Matches</b-nav-item>
        <b-nav-item-dropdown text="Tagging">
          <b-dropdown-item :to="{name: 'Tags'}">Tag list</b-dropdown-item>
          <b-dropdown-item :to="{name: 'TaggingTagSelect'}">Start tagging</b-dropdown-item>
        </b-nav-item-dropdown>
        <b-nav-item-dropdown text="GCV">
          <b-dropdown-item :to="{name: 'Faces'}">Face detection</b-dropdown-item>
          <b-dropdown-item :to="{name: 'Objects'}">Object localization</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
      <b-navbar-nav v-if="user" class="ml-auto">
        <b-nav-item-dropdown :text="user.username" right>
          <b-dropdown-item disabled>Tasks</b-dropdown-item>
          <b-dropdown-item :href="$APIConstants.API_LOGOUT">Logout</b-dropdown-item>
        </b-nav-item-dropdown>
      </b-navbar-nav>
      <b-navbar-nav v-else class="ml-auto">
        <b-nav-item :href="$APIConstants.API_LOGIN">Login</b-nav-item>
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
    return HTTP.get("/").then(
      response => {
        this.logged_in = !!response;
      },
      error => {
        console.log(error);
        this.logged_in = false;
      }
    );
  },
  asyncComputed: {
    user() {
      return HTTP.get("/current_user/").then(
        response => {
          // Store the user to the root so other components can access it if needed (this is naughty, but it's the only global state we need in the app so far, so I'm doing it anyway.)
          this.$root.user = response.data;
          return response.data;
        },
        error => {
          console.log(error);
        }
      );
    }
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

.pointer {
  cursor: pointer;
}
</style>
