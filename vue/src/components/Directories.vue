<template>
  <div>
    <b-input v-model="dir_label_search" debounce="500" placeholder="Search directory names..." />
    <b-list-group>
      <b-list-group-item
        class="p-1"
        v-for="dir in directories.results"
        :key="dir.id"
        @click="$emit('input', dir)"
      >{{ dir.label }} ({{ dir.n_images }})</b-list-group-item>
    </b-list-group>
  </div>
</template>

<script>
import { HTTP } from "../main";
export default {
  name: "Directories",
  data() {
    return {
      dir_label_search: "",
      show_all: false
    };
  },
  asyncComputed: {
    directories() {
      var payload = {};
      if (this.dir_label_search != "") {
        payload["label"] = this.dir_label_search;
      }
      return HTTP.get("/directory/", {
        params: payload
      }).then(
        results => {
          return results.data;
        },
        error => {
          console.log(error);
        }
      );
    }
  }
};
</script>