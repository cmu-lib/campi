<template>
  <b-card class="my-2" header="Directories">
    <b-input-group class="my-2">
      <b-input v-model="dir_label_search" debounce="500" placeholder="Search directory names..." />
      <b-input-group-append v-if="dir_label_search != ''">
        <b-button variant="warning" size="sm" @click="dir_label_search=''">
          <BIconXSquare />
        </b-button>
      </b-input-group-append>
    </b-input-group>
    <b-list-group v-if="!!directories">
      <b-list-group-item
        class="p-1"
        v-for="dir in directories.results"
        :key="dir.id"
        @click="$emit('input', dir)"
      >{{ dir.label }} ({{ dir.n_images }})</b-list-group-item>
    </b-list-group>
  </b-card>
</template>

<script>
import { HTTP } from "../main";
import { BIconXSquare } from "bootstrap-vue";
export default {
  name: "Directories",
  components: {
    BIconXSquare
  },
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