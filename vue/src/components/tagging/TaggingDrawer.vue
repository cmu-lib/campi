<template>
  <b-sidebar id="sidebar" v-model="show_sidebar" width="90%" right shadow>
    <b-container fluid>
      <h3>{{ sidebar_title }}</h3>
      <p>Click on a photograph to tag it with "{{ task.tag.label }}".</p>
      <b-button @click="register_whole_grid">
        Add "{{ task.tag.label }}" to all photos on this page
        <b-spinner v-if="requests_processing" small class="mr-1" />
      </b-button>
      <PhotoGrid
        v-if="sidebar_payload.class=='job'"
        :highlight_ids="higlighted_photos"
        :job="sidebar_payload.object"
        @photo_click="toggle_tag"
        @images="set_images"
      />
      <PhotoGrid
        v-if="sidebar_payload.class=='directory'"
        :highlight_ids="higlighted_photos"
        :directory="sidebar_payload.object"
        @photo_click="toggle_tag"
        @images="set_images"
      />
    </b-container>
  </b-sidebar>
</template>

<script>
import PhotoGrid from "@/components/browsing/PhotoGrid.vue";
import _ from "lodash";

export default {
  name: "TaggingDrawer",
  components: { PhotoGrid },
  props: {
    sidebar_payload: {
      type: Object,
      required: true
    },
    task: {
      type: Object,
      required: true
    },
    higlighted_photos: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      show_sidebar: true,
      sidebar_grid_state: [],
      requests_processing: false
    };
  },
  computed: {
    sidebar_title() {
      return `${this.sidebar_payload.class}: ${this.sidebar_payload.object.label}`;
    },
    untagged_grid_photos() {
      return _.difference(
        this.sidebar_grid_state.map(p => p.id),
        this.higlighted_photos
      );
    }
  },
  methods: {
    set_images(payload) {
      console.log("Setting images");
      this.sidebar_grid_state = payload;
    },
    toggle_tag(photograph) {
      if (this.higlighted_photos.includes(photograph.id)) {
        this.remove_tag(photograph.id);
      } else {
        this.add_tag(photograph.id);
      }
    },
    add_tag(photograph_id) {
      this.$emit("add_tag", photograph_id);
    },
    remove_tag(photograph_id) {
      this.$emit("remove_tag", photograph_id);
    },
    register_whole_grid() {
      this.requests_processing = true;
      Promise.allSettled(
        this.untagged_grid_photos.map(pid => this.toggle_tag(pid))
      ).then(onfulfilled => {
        this.requests_processing = false;
        console.log(onfulfilled);
      });
    }
  },
  watch: {
    sidebar_payload() {
      if (!!this.sidebar_payload.object) {
        this.show_sidebar = true;
      } else {
        this.show_sidebar = false;
      }
    }
  }
};
</script>