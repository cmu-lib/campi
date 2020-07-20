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
      <div v-for="image in images.results" :key="image.id" class="my-2 mx-4">
        <b-row>
          <b-img
            :class="{'highlighted': highlight_ids.includes(image.id), 'dimmed': dimmed_ids.includes(image.id)}"
            :src="image.image.square"
            width="230"
            height="230"
            @click="$emit('photo_click', image)"
          />
        </b-row>
        <b-row>
          <b-button
            v-if="info_button"
            size="sm"
            variant="light"
            block
            squared
            v-b-modal="`modal-${image.id}`"
          >
            <BIconInfoCircle class="mx-1" title="Click to view full size" v-b-tooltip:hover />
            <BIconFiles
              class="mx-1"
              v-if="image.in_close_match_set"
              title="This image belongs to a set of near duplicate photos. Any tagging decision will be applied to multiple photos."
              v-b-tooltip:hover
            />
          </b-button>
        </b-row>
        <b-modal
          v-if="info_button"
          :id="`modal-${image.id}`"
          size="xl"
          centered
          :title="image.filename"
          @ok="newtab(image)"
          ok-only
          ok-title="Open detail view in new tab"
        >
          <b-container fluid>
            <b-row align-h="center">
              <b-img :src="`${image.image.id}/full/!1000,800/0/default.jpg`" fluid />
            </b-row>
          </b-container>
        </b-modal>
      </div>
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
import { BIconInfoCircle, BIconFiles } from "bootstrap-vue";
export default {
  name: "PhotoGrid",
  components: { BIconInfoCircle, BIconFiles },
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
    gcv_object: {
      type: Object,
      default: null
    },
    gcv_label: {
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
    info_button: {
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
      if (!!this.gcv_object) {
        payload["gcv_object"] = this.gcv_object.id;
      }
      if (!!this.gcv_label) {
        payload["gcv_label"] = this.gcv_label.id;
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
    modals() {
      if (this.info_button) {
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