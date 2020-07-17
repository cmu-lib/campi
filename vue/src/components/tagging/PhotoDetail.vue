<template>
  <b-card v-if="!!photograph">
    <template v-slot:header>
      <b-row align-h="between" align-v="center" class="px-2">
        <span>{{ photograph.filename }}</span>
        <h3 class="my-0">
          <BIconX @click="close_photo_detail" class="pointer" />
        </h3>
      </b-row>
    </template>
    <b-button-toolbar>
      <b-button
        size="sm"
        :variant="tag_button_variant"
        :pressed="is_tagged"
        @click="toggle_photo"
      >{{ tag_button_label }}</b-button>
      <b-button-group class="mx-1">
        <b-button
          size="sm"
          v-if="!!photograph.job"
          variant="info"
          @click="activate_sidebar({class: 'job', object: photograph.job})"
          v-b-tooltip:hover
          title="Click to tag other photos in job"
        >
          <BIconCamera />
          "{{ button_truncate(photograph.job.label) }}"
        </b-button>
        <b-button size="sm" v-else disabled variant="info">
          <BIconCamera class="mr-1" />
          <span>No associated job</span>
        </b-button>
        <b-button
          size="sm"
          variant="primary"
          @click="activate_sidebar({class: 'directory', object: photograph.directory})"
          v-b-tooltip:hover
          title="Click to tag other photos in directory"
        >
          <BIconFolderFill />
          "{{ button_truncate(photograph.directory.label) }}"
        </b-button>
      </b-button-group>
      <b-button
        size="sm"
        variant="warning"
        class="mx-1"
        @click="$emit('new_seed_photo', photograph)"
        title="Swap out the current seed photo in exchange for this photo. (Will reload the page.)"
        v-b-tooltip:hover
      >Use as seed photo</b-button>
      <b-button
        size="sm"
        class="mx-1"
        variant="light"
        @click="detail_tab_href"
        title="Open photo in a new tab to inxpect all tags, look at annotations, and more."
        v-b-tooltip:hover
      >Open in new tab</b-button>
    </b-button-toolbar>
    <b-row class="my-2" align-h="center">
      <b-img :src="`${photograph.image.id}/full/!750,525/0/default.jpg`" />
    </b-row>
  </b-card>
</template>

<script>
import _ from "lodash";
import { BIconCamera, BIconFolderFill, BIconX } from "bootstrap-vue";

export default {
  name: "PhotoDetail",
  components: {
    BIconCamera,
    BIconFolderFill,
    BIconX
  },
  props: {
    photograph: {
      type: Object,
      required: true
    },
    task_tag: {
      type: Object,
      default: null
    },
    highlighted_photos: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      selected_tags: []
    };
  },
  computed: {
    is_tagged() {
      return this.highlighted_photos.includes(this.photograph.id);
    },
    tag_button_label() {
      if (this.is_tagged) {
        return `Remove tag "${this.button_truncate(this.task_tag.label)}"`;
      } else {
        return `Tag as "${this.button_truncate(this.task_tag.label)}"`;
      }
    },
    tag_button_variant() {
      if (this.is_tagged) {
        return "danger";
      } else {
        return "success";
      }
    }
  },
  methods: {
    detail_tab_href() {
      const routeData = this.$router.resolve({
        name: "Photo",
        params: { id: this.photograph.id }
      });
      window.open(routeData.href, "_blank");
    },
    button_truncate(str) {
      return _.truncate(str, { length: 25 });
    },
    activate_sidebar(payload) {
      this.$emit("activate_sidebar", payload);
    },
    toggle_photo() {
      if (this.is_tagged) {
        this.$emit("remove_tag", this.photograph.id);
      } else {
        this.$emit("add_tag", this.photograph.id);
      }
    },
    close_photo_detail() {
      this.$emit("close_photo_detail");
    }
  }
};
</script>