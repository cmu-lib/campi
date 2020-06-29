<template>
  <b-container fluid v-if="!!images">
    <b-row align-h="center" align-v="center">
      <p class="mr-auto">{{ images.count }} results</p>
      <b-pagination
        v-model="current_page"
        v-if="images.count>per_page"
        :total-rows="images.count"
        :per-page="per_page"
        class="mr-auto"
      />
    </b-row>
    <b-row flex align-h="center">
      <b-img
        lazy
        v-for="image in images.results"
        class="m-1"
        :class="{'highlighted': highlight_ids.includes(image.id)}"
        :key="image.id"
        :src="image.image.square"
        blank-width="150"
        blank-height="150"
        @click="$emit('photo_click', image)"
      />
    </b-row>
    <b-row flex align-h="center" class="mt-3">
      <b-pagination
        v-model="current_page"
        v-if="images.count>per_page"
        :total-rows="images.count"
        :per-page="per_page"
      />
    </b-row>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
export default {
  name: "PhotoGrid",
  props: {
    directory: {
      type: Object,
      default: null
    },
    job: {
      type: Object,
      default: null
    },
    job_tag: {
      default: null
    },
    tag: {
      type: Object,
      default: null
    },
    digitized_date_before: {
      type: Number,
      default: null
    },
    digitized_date_after: {
      type: Number,
      default: null
    },
    per_page: {
      type: Number,
      default: 96
    },
    highlight_ids: {
      type: Array,
      default: function() {
        return [];
      }
    }
  },
  data() {
    return {
      current_page: 1
    };
  },
  asyncComputed: {
    images() {
      var payload = {
        offset: this.rest_page,
        ordering: "-digitized_date",
        limit: this.per_page
      };
      if (!!this.directory) {
        payload["directory"] = this.directory.id;
      }
      if (!!this.job) {
        payload["job"] = this.job.id;
      }
      if (!!this.job_tag) {
        payload["job_tag"] = this.job_tag.id;
      }
      if (!!this.tag) {
        payload["tag"] = this.tag.id;
      }
      if (!!this.digitized_date_after) {
        payload["digitized_date_after"] = `${this.digitized_date_after}-01-01`;
      }
      if (!!this.digitized_date_before) {
        payload[
          "digitized_date_before"
        ] = `${this.digitized_date_before}-01-01`;
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
    }
  },
  computed: {
    rest_page() {
      return (this.current_page - 1) * this.per_page;
    }
  }
};
</script>

<style scoped>
.highlighted {
  outline: 3px red solid;
}
</style>