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
    <b-row align-h="center" class="my-1">
      <b-button-toolbar justify>
        <b-button-group class="mx-1">
          <b-button size="sm" variant="secondary" :pressed="is_tagged">Tag as "{{ task_tag.label }}"</b-button>
          <b-button size="sm" variant="secondary" v-b-modal.add-tag>View/edit other tags</b-button>
        </b-button-group>
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
      </b-button-toolbar>
    </b-row>
    <b-row class="my-2" align-h="center">
      <b-img :src="`${photograph.image.id}/full/!750,525/0/default.jpg`" />
    </b-row>
    <b-row>
      <b-badge
        variant="warning"
        v-for="tag in photograph.photograph_tags"
        :key="tag.id"
      >{{ tag.tag.label }}</b-badge>
    </b-row>
    <b-modal id="add-tag" title="Add tag(s) to photograph" @ok="register_selected_tags">
      <b-form-select v-model="selected_tags" :options="tag_choices" multiple :select-size="20" />
    </b-modal>
  </b-card>
</template>

<script>
import { HTTP } from "@/main";
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
    available_tags: {
      type: Array
    },
    task_tag: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      selected_tags: []
    };
  },
  computed: {
    is_tagged() {
      return this.photograph.photograph_tags
        .map(t => t.tag.id)
        .includes(this.task_tag.id);
    },
    tag_choices() {
      // Disable the current tag
      return this.available_tags.map(t => {
        const disabled = t.id == this.task_tag.id;
        var tlabel = "";
        if (disabled) {
          tlabel = `${t.label} (to add this current task tag, click on the tag button photo detail)`;
        } else {
          tlabel = t.label;
        }
        return {
          text: tlabel,
          value: t.id,
          disabled: disabled
        };
      });
    },
    new_tags() {
      // Tags to be added that aren't already attached to this photograph
      return _.difference(
        this.selected_tags,
        this.photograph.photograph_tags.map(t => t.tag.id)
      );
    }
  },
  methods: {
    button_truncate(str) {
      return _.truncate(str, { length: 25 });
    },
    activate_sidebar(payload) {
      this.$emit("activate_sidebar", payload);
    },
    add_tag(photograph_id, tag_id) {
      // Adding an arbitrary, non-task tag
      HTTP.post("tagging/photograph_tag/", {
        tag: tag_id,
        photograph: photograph_id
      }).then(
        response => {
          const image_index = _.findIndex(this.sidebar_grid_state, {
            id: photograph_id
          });
          this.sidebar_grid_state[image_index].photograph_tags.push({
            id: response.data.id,
            tag: { id: response.data.tag }
          });
          this.$emit("new_tagged_photo", this.sidebar_grid_state[image_index]);
        },
        error => {
          console.log(error);
        }
      );
    },
    remove_tag(photograph_id, tag_id) {
      // Removing an arbitrary, non-task tag
      const image_index = _.findIndex(this.sidebar_grid_state, {
        id: photograph_id
      });
      console.log(`Image index: ${image_index}`);
      const photograph_tag_index = _.findIndex(
        this.sidebar_grid_state[image_index].photograph_tags,
        pt => pt.tag.id == tag_id
      );
      console.log(`phototag index: ${photograph_tag_index}`);
      const photograph_tag_id = this.sidebar_grid_state[image_index]
        .photograph_tags[photograph_tag_index].id;
      HTTP.delete(`tagging/photograph_tag/${photograph_tag_id}/`).then(
        response => {
          console.log(response);
          this.sidebar_grid_state[image_index].photograph_tags.splice(
            photograph_tag_index,
            1
          );
        },
        error => {
          console.log(error);
        }
      );
    },
    register_selected_tags() {
      Promise.all(
        this.new_tags.map(tag => this.add_tag(this.photograph.id, tag))
      ).then(onfulfilled => {
        this.get_photograph();
        console.log(onfulfilled);
      });
    },

    close_photo_detail() {
      this.$emit("close_photo_detail");
    }
  }
};
</script>