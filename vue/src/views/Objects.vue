<template>
  <b-container fluid>
    <b-row>
      <b-form-select :options="ordering_options" v-model="ordering" />
    </b-row>
    <router-link
      v-for="obj in objects"
      :key="obj.id"
      :to="{name: 'Photo', params: {id: obj.photograph.id}}"
    >
      <b-img class="m-3" :src="obj.thumbnail" />
      {{ obj.label }}
    </router-link>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
export default {
  name: "Objects",
  data() {
    return {
      ordering: "-score"
    };
  },
  computed: {
    ordering_options() {
      return [
        {
          value: "-score",
          text: "Object detection confidence"
        },
        {
          value: "photograph",
          text: "Photograph"
        }
      ];
    }
  },
  asyncComputed: {
    objects() {
      return HTTP.get("/gcv/object_annotation/", {
        params: { ordering: this.ordering }
      }).then(
        response => {
          return response.data.results;
        },
        error => {
          console.log(error);
        }
      );
    }
  }
};
</script>