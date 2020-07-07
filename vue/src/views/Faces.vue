<template >
  <b-container fluid v-if="!!faces">
    <b-row align-h="center">
      <b-form-group
        id="ordering-help"
        label-for="ordering"
        label="Ordering"
        description="Ordering by other than 'Face detection confidence' will filter the photoset to photos that score at least a 2 ('possible') on the selected feature scale."
      >
        <b-form-select
          id="ordering"
          :options="ordering_options"
          v-model="ordering"
          @input="reset_page"
        />
      </b-form-group>
    </b-row>
    <b-row align-h="center">
      <b-pagination
        v-model="current_page"
        v-if="faces.count>per_page"
        :total-rows="faces.count"
        :per-page="per_page"
      />
      <span class="ml-3">{{ faces.count }} results</span>
    </b-row>
    <b-row align-h="between">
      <router-link
        v-for="face in faces.results"
        :key="face.id"
        :to="{name: 'Photo', params: {id: face.photograph.id}}"
      >
        <b-img-lazy class="m-3" :src="face.thumbnail" v-b-popover.hover.top="face_info(face)" />
      </router-link>
    </b-row>
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
      per_page: 50
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
          value: "-surprise_likelihood",
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
    },
    core_state() {
      var payload = { ordering: this.ordering };
      if (this.ordering != "-detection_confidence") {
        const qstring = this.ordering.substr(1);
        payload[qstring] = 2;
      }
      return payload;
    },
    search_state() {
      var payload = this.core_state;
      payload.offset = this.rest_page;
      payload.limit = this.per_page;
      return payload;
    }
  },
  asyncComputed: {
    faces() {
      return HTTP.get("/gcv/face_annotation/", {
        params: this.search_state
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
    reset_page() {
      this.current_page = 1;
    },
    face_info(face) {
      return `
      joy: ${face.joy_likelihood}
      sorrow: ${face.sorrow_likelihood}
      anger: ${face.anger_likelihood}
      surprise_likelihood: ${face.surprise_likelihood}
      headwear_likelihood = ${face.headwear_likelihood}
      `;
    }
  },
  watch: {
    search_state() {
      this.$router.push({ query: this.search_state });
    }
  },
  created() {
    if (!!this.$route.query.ordering) {
      this.ordering = this.$route.query.ordering;
    }
    if (!!this.$route.query.offset) {
      this.current_page = Number(this.$route.query.offset) / this.per_page + 1;
    }
  }
};
</script>