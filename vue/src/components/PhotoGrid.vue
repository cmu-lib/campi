<template>
  <b-container fluid v-if="!!images">
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
  </b-container>
</template>

<script>
import { HTTP } from "../main";
export default {
  name: "PhotoGrid",
  props: {
    directory: {
      default: null
    }
  },
  data() {
    return {
      current_page: 1
    };
  },
  asyncComputed: {
    images() {
      var payload = { offset: this.rest_page, ordering: "-digitized_date" };
      if (this.directory) {
        payload["directory"] = this.directory.id;
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