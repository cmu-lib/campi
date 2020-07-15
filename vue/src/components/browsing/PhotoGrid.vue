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
        class="m-2"
        :class="{'highlighted': highlight_ids.includes(image.id), 'dimmed': dimmed_ids.includes(image.id)}"
        :key="image.id"
        :id="`image-${image.id}`"
        :src="image.image.square"
        blank-width="150"
        blank-height="150"
        @click="$emit('photo_click', image)"
      />
      <b-popover
        v-for="image in popovers"
        :key="`pop-${image.id}`"
        triggers="hover"
        :target="`image-${image.id}`"
        :delay="{show: 1000}"
        custom-class="photo-popover"
        placement="top"
      >
        <template v-slot:title>{{ image.filename }}</template>
        <b-img :src="image.image.thumbnail" fluid />
        <b-button class="mt-2" @click="newtab(image)" variant="primary">Open in new tab</b-button>
      </b-popover>
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
    },
    dimmed_ids: {
      type: Array,
      default: function() {
        return [];
      }
    },
    popover: {
      type: Boolean,
      default: false
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
    },
    popovers() {
      if (this.popover) {
        return this.images.results;
      } else {
        return [];
      }
    }
  },
  methods: {
    newtab(image) {
      const routeData = this.$router.resolve({
        name: "Photo",
        params: { id: image.id }
      });
      window.open(routeData.href, "_blank");
    }
  },
  watch: {
    images() {
      this.$emit("images", this.images.results);
    }
  }
};
</script>

<style scoped>
.highlighted {
  outline: 3px solid greenyellow;
  filter: sepia(100%) saturate(200%) brightness(100%) hue-rotate(50deg);
}
.dimmed {
  outline: 3px solid orangered;
  filter: sepia(100%) saturate(200%) brightness(100%) hue-rotate(320deg);
}

.photo-popover {
  max-width: 600px;
}
</style>