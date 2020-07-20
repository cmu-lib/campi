<template>
  <b-container fluid v-if="!!objects">
    <b-container class="mt-3">
      <p>Results from Google Cloud Vision API's "object localization" feature, which tries to identify generic types of objects/products within pictures and draw boxes around them.</p>
    </b-container>
    <b-row class="mt-3" align-h="around">
      <b-form-group id="ordering-help" label-for="ordering" label="Ordering">
        <b-form-select
          id="ordering"
          :options="ordering_options"
          v-model="ordering"
          @input="reset_page"
        />
      </b-form-group>
      <b-form-group id="labels-help" label-for="labels" label="Localized object label">
        <b-form-select
          id="labels"
          v-if="!!labels"
          :options="labels"
          v-model="label"
          @input="reset_page"
        />
      </b-form-group>
    </b-row>
    <b-row align-h="center">
      <b-pagination
        v-model="current_page"
        v-if="objects.count>per_page"
        :total-rows="objects.count"
        :per-page="per_page"
      />
    </b-row>
    <b-row align-h="between">
      <router-link
        v-for="obj in objects.results"
        :key="obj.id"
        :to="{name: 'Photo', params: {id: obj.photograph.id}}"
      >
        <b-img
          class="m-3"
          :src="obj.thumbnail"
          v-b-tooltip.hover
          :title="`${obj.id} - ${obj.label} - ${obj.score.toFixed(3)}`"
          :height="thumb_height(obj)"
          :width="thumb_width(obj)"
        />
      </router-link>
    </b-row>
    <b-row align-h="center">
      <b-pagination
        v-model="current_page"
        v-if="objects.count>per_page"
        :total-rows="objects.count"
        :per-page="per_page"
      />
    </b-row>
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
      per_page: 50
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
    img_ratio(obj) {
      if (obj.height >= obj.width) {
        return 300 / obj.height;
      } else {
        return 300 / obj.width;
      }
    },
    thumb_height(obj) {
      return Math.round(obj.height * this.img_ratio(obj));
    },
    thumb_width(obj) {
      return Math.round(obj.width * this.img_ratio(obj));
    },
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