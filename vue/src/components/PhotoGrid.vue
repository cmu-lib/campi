<template>
  <b-container fluid v-if="!!images">
    <b-pagination v-model="current_page" :total-rows="images.count" :per-page="100" />
    <b-row flex>
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
  data() {
    return {
      current_page: 1
    };
  },
  asyncComputed: {
    images() {
      return HTTP.get("/photograph/", {
        params: { offset: this.rest_page }
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