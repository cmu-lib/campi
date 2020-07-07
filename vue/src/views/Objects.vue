<template>
  <b-container fluid v-if="!!objects">
    <b-row>
      <b-form-select :options="ordering_options" v-model="ordering" @input="reset_page" />
      <b-form-select v-if="!!labels" :options="labels" v-model="label" @input="reset_page" />
    </b-row>
    <b-pagination
      v-model="current_page"
      v-if="objects.count>per_page"
      :total-rows="objects.count"
      :per-page="per_page"
      class="mr-auto"
    />
    <router-link
      v-for="obj in objects.results"
      :key="obj.id"
      :to="{name: 'Photo', params: {id: obj.photograph.id}}"
    >
      <b-img
        class="m-3"
        :src="obj.thumbnail"
        v-b-tooltip.hover
        :title="`${obj.id} - ${obj.label}`"
      />
    </router-link>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
export default {
  name: "Objects",
  data() {
    return {
      ordering: "-score",
      label: null,
      current_page: 1,
      per_page: 100
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
          value: "photograph__date_taken_early",
          text: "Photograph date"
        }
      ];
    },
    core_state() {
      var payload = { ordering: this.ordering };
      if (!!this.label) {
        payload["label"] = this.label;
      }
      return payload;
    },
    search_state() {
      var payload = this.core_state;
      payload.offset = this.rest_page;
      payload.limit = this.per_page;
      return payload;
    },
    rest_page() {
      return (this.current_page - 1) * this.per_page;
    }
  },
  asyncComputed: {
    objects() {
      return HTTP.get("/gcv/object_annotation/", {
        params: this.search_state
      }).then(
        response => {
          return response.data;
        },
        error => {
          console.log(error);
        }
      );
    },
    labels() {
      return HTTP.get("/gcv/object_annotation_labels/").then(
        response => {
          return response.data.map(l => {
            return {
              text: `${l.label} (${l.n_annotations})`,
              value: l.label
            };
          });
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
    if (!!this.$route.query.label) {
      this.label = this.$route.query.label;
    }
    if (!!this.$route.query.offset) {
      this.current_page = Number(this.$route.query.offset) / 100 + 1;
    }
  }
};
</script>