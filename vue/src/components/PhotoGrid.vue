<template>
  <b-row flex>
    <router-link
      v-for="image in images"
      :key="image.id"
      :to="{name: 'Photo', params: {id: image.id}}"
    >
      <b-img lazy :src="image.image.square" blank-width="200" blank-height="200" />
    </router-link>
  </b-row>
</template>

<script>
import { HTTP } from "../main";
export default {
  name: "PhotoGrid",
  data() {
    return {};
  },
  asyncComputed: {
    images() {
      return HTTP.get("/photograph/").then(
        results => {
          return results.data.results;
        },
        error => {
          console.log(error);
        }
      );
    }
  }
};
</script>