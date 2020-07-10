<template>
  <b-card v-if="!!photograph" header="Photo info">
    <b-row>
      <b-img :src="`${photograph.image.id}/full/!800,600/0/default.jpg`" />
    </b-row>
    <b-row align-v="center" align-h="between">
      <span>{{ photograph.filename }}</span>
      <b-badge
        variant="primary"
        @click="activate_sidebar({class: 'directory', object: photograph.directory})"
      >
        <BIconFolderFill />
        {{ photograph.directory.label }}
      </b-badge>
      <b-badge
        variant="info"
        v-if="photograph.job"
        @click="activate_sidebar({class: 'job', object: photograph.job})"
      >
        <BIconCamera />
        {{ photograph.job.label }}
      </b-badge>
    </b-row>
    <b-row>
      <b-button variant="warning" @click="$emit('new_seed_photo', photograph)">Use as seed photo</b-button>
      <b-button variant="primary" v-b-modal.add-tag>Add tag</b-button>
      <b-badge
        variant="warning"
        v-for="tag in photograph.photograph_tags"
        :key="tag.id"
      >{{ tag.tag.label }}</b-badge>
    </b-row>
    <b-modal id="add-tag" title="Add tag(s) to photograph" @ok="register_selected_tags">
      <b-form-select v-model="selected_tags" :options="tag_choices" multiple />
    </b-modal>
    <b-sidebar :id="`sidebar`" v-model="show_sidebar" v-if="show_sidebar" width="800px" right>
      <b-container>
        <h3>{{ sidebar_title }}</h3>
        <p>Click on a photograph to tag it with "{{ task_tag.label }}".</p>
        <b-button @click="register_whole_grid">
          Add "{{ task_tag.label }}" to all photos on this page
          <b-spinner v-if="requests_processing" small class="mr-1" />
        </b-button>
        <PhotoGrid
          v-if="sidebar_payload.class=='job'"
          :highlight_ids="tagged_grid_photos"
          :job="sidebar_payload.object"
          @photo_click="toggle_tag_from_grid"
          @images="set_images"
        />
        <PhotoGrid
          v-if="sidebar_payload.class=='directory'"
          :highlight_ids="tagged_grid_photos"
          :directory="sidebar_payload.object"
          @photo_click="toggle_tag_from_grid"
          @images="set_images"
        />
      </b-container>
    </b-sidebar>
  </b-card>
</template>

<script>
import { HTTP } from "@/main";
import PhotoGrid from "@/components/browsing/PhotoGrid.vue";
import _ from "lodash";
import { BIconCamera, BIconFolderFill } from "bootstrap-vue";
export default {
  name: "PhotoDetail",
  components: {
    BIconCamera,
    BIconFolderFill,
    PhotoGrid
  },
  props: {
    photograph_id: {
      type: Number,
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
      photograph: null,
      selected_tags: [],
      show_sidebar: false,
      sidebar_payload: {},
      sidebar_grid_state: [],
      requests_processing: false
    };
  },
  computed: {
    tag_choices() {
      return this.available_tags.map(t => {
        return {
          text: t.label,
          value: t.id
        };
      });
    },
    new_tags() {
      // Tags to be added that aren't already attached to this photograph
      return _.difference(
        this.selected_tags,
        this.photograph.photograph_tags.map(t => t.tag.id)
      );
    },
    sidebar_title() {
      return `${this.sidebar_payload.class}: ${this.sidebar_payload.object.label}`;
    },
    tagged_grid_photos() {
      if (!!this.task_tag) {
        return this.sidebar_grid_state
          .filter(p =>
            p.photograph_tags
              .map(t => t.tag.id)
              .some(t => t == this.task_tag.id)
          )
          .map(p => p.id);
      } else {
        return [];
      }
    },
    untagged_grid_photos() {
      return _.difference(
        this.sidebar_grid_state.map(p => p.id),
        this.tagged_grid_photos
      );
    }
  },
  methods: {
    set_images(payload) {
      console.log("Setting images");
      this.sidebar_grid_state = payload;
    },
    activate_sidebar(payload) {
      this.sidebar_payload = payload;
      this.show_sidebar = true;
    },
    get_photograph() {
      HTTP.get(`photograph/${this.photograph_id}/`).then(
        response => {
          this.photograph = response.data;
          this.selected_tags = this.photograph.photograph_tags.map(
            t => t.tag.id
          );
        },
        error => {
          console.log(error);
        }
      );
    },
    toggle_tag_from_grid(photograph) {
      if (photograph.photograph_tags.some(t => t.tag.id == this.task_tag.id)) {
        this.remove_tag(photograph.id, this.task_tag.id);
      } else {
        this.add_tag(photograph.id, this.task_tag.id);
      }
    },
    add_tag(photograph_id, tag_id) {
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
    register_whole_grid() {
      this.requests_processing = true;
      Promise.allSettled(
        this.untagged_grid_photos.map(pid =>
          this.add_tag(pid, this.task_tag.id)
        )
      ).then(onfulfilled => {
        this.requests_processing = false;
        this.get_photograph();
        console.log(onfulfilled);
      });
    }
  },
  mounted() {
    this.get_photograph();
  }
};
</script>