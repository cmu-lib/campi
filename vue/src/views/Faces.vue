<template >
  <b-container fluid>
    <b-row>
      <b-form-select :options="ordering_options" v-model="ordering" />
    </b-row>
    <b-pagination
      v-model="current_page"
      v-if="faces.count>per_page"
      :total-rows="faces.count"
      :per-page="per_page"
      class="mr-auto"
    />
    <router-link
      v-for="face in faces.results"
      :key="face.id"
      :to="{name: 'Photo', params: {id: face.photograph.id}}"
    >
      <b-img-lazy class="m-3" :src="face.thumbnail" v-b-popover.hover.top="face_info(face)" />
    </router-link>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
export default {
  name: "Faces",
  data() {
    return {
      ordering: "-detection_confidence",
      current_page: 1,
      per_page: 100
    };
  },
  computed: {
    ordering_options() {
      return [
        {
          value: "-detection_confidence",
          text: "Face detection confidence"
        },
        {
          value: "-joy_likelihood",
          text: "Joy"
        },
        {
          value: "-sorrow_likelihood",
          text: "Sorrow"
        },
        {
          value: "-anger_likelihood",
          text: "Anger"
        },
        {
          value: "-surprise_lieklihood",
          text: "Surprise"
        },
        {
          value: "-headwear_likelihood",
          text: "Headwear"
        }
      ];
    },
    rest_page() {
      return (this.current_page - 1) * this.per_page;
    }
  },
  asyncComputed: {
    faces() {
      return HTTP.get("/gcv/face_annotation/", {
        params: {
          ordering: this.ordering,
          offset: this.rest_page,
          limit: this.per_page
        }
      }).then(
        response => {
          return response.data;
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  methods: {
    face_info(face) {
      return `
      joy: ${face.joy_likelihood}
      sorrow: ${face.sorrow_likelihood}
      anger: ${face.anger_likelihood}
      surprise_likelihood: ${face.surprise_likelihood}
      headwear_likelihood = ${face.headwear_likelihood}
      `;
    }
  }
};
</script>