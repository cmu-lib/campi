<template>
  <b-container fluid v-if="!!images">
    <b-row>
      <b-col cols="4">
        <b-input v-model="dir_label_search" debounce="500" placeholder="Search directory names..." />
        <b-list-group>
          <b-list-group-item
            v-for="dir in top_level_directories.results"
            :key="dir.id"
            @click="selected_directory=dir.id"
          >{{ dir.label }} ({{ dir.n_images }})</b-list-group-item>
        </b-list-group>
      </b-col>
      <b-col cols="8">
        <b-row align-h="center">
          <b-pagination v-model="current_page" :total-rows="images.count" :per-page="100" />
        </b-row>
        <b-row flex align-h="center">
          <router-link
            v-for="image in images.results"
            :key="image.id"
            :to="{name: 'Photo', params: {id: image.id}}"
            target="_blank"
            rel="noopener noreferrer"
          >
            <b-img lazy :src="image.image.square" blank-width="150" blank-height="150" />
          </router-link>
        </b-row>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import { HTTP } from "../main";
export default {
  name: "PhotoGrid",
  data() {
    return {
      current_page: 1,
      dir_label_search: "",
      selected_directory: null
    };
  },
  asyncComputed: {
    images() {
      var payload = { offset: this.rest_page, ordering: "-digitized_date" };
      if (this.selected_directory) {
        payload["directory"] = this.selected_directory;
      }
      return HTTP.get("/photograph/", {
        params: payload
      }).then(
        results => {
          return results.data;
        },
        error => {
          console.log(error);
        }
      );
    },
    top_level_directories() {
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
  },
  computed: {
    rest_page() {
      return (this.current_page - 1) * 100;
    }
  }
};
</script>