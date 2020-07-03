<template >
  <b-container fluid>
    <b-row>
      <b-form-select :options="ordering_options" v-model="ordering" />
    </b-row>
    <router-link
      v-for="face in faces"
      :key="face.id"
      :to="{name: 'Photo', params: {id: face.photograph.id}}"
    >
      <b-img class="m-3" :src="face.thumbnail" v-b-popover.hover.top="face_info(face)" />
    </router-link>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
export default {
  name: "Faces",
  data() {
    return {
      ordering: "-detection_confidence"
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
    }
  },
  asyncComputed: {
    faces() {
      return HTTP.get("/gcv/face_annotation/", {
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