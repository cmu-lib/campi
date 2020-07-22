<template>
  <b-sidebar id="sidebar" v-model="show_sidebar" width="90%" right shadow>
    <b-container fluid>
      <b-row align-h="between" class="m-2">
        <h3>{{ sidebar_title }}</h3>
        <b-button variant="info" @click="show_help = !show_help">
          <BIconQuestionCircleFill class="mx-1" />Toggle instructions
        </b-button>
      </b-row>
      <b-collapse class="my-2" v-model="show_help">
        <b-container>
          <ol>
            <li>Click on a photograph to tag it with "{{ task.tag.label }}". Photos tinted green are "accepted".</li>
            <li>You can reverse a decision by clicking on the photo again, which will turn it orange. This removes the tag, and will prevent that photo from showing up in future suggestions.</li>
            <li>Once you have tagged all the relevant photos on this page, hit the "Exclude all undecided photos" to exclude the rest. This will help your future tagging tasks.</li>
            <li>If this is a large job or directory, you may see pagination buttons. You will need to click through the other pages to make tagging decisions for those photos.</li>
            <li>The archivists have grouped some photos as being "close matches" that are copies or extremely similar photogrpahs. These will update simultaneously when you click on one, so you may notice multiple photographs changing when you click on just one image.</li>
            <li>Once you have gone through the whole job/directory, click the X at upper left to close the drawer and move on to a new photo.</li>
          </ol>
          <p>Click on the info button under any picture to get a full-sized preview, and a link to a full details page for the file.</p>
        </b-container>
      </b-collapse>
      <b-row align-h="center" class="mt-3">
        <b-button-group>
          <b-button @click="register_whole_grid" variant="success">
            Add "{{ task.tag.label }}" to all undecided photos on this page
            <b-spinner v-if="requests_processing" small class="mr-1" />
          </b-button>
          <b-button @click="reject_remaining_grid" variant="warning">
            Exclude all undecided photos on this page from future consideration for "{{ task.tag.label }}"
            <b-spinner v-if="requests_processing" small class="mr-1" />
          </b-button>
        </b-button-group>
      </b-row>
      <PhotoGrid
        v-if="sidebar_payload.class=='job'"
        info_button
        :highlight_ids="higlighted_photos"
        :dimmed_ids="rejected_photos"
        :job="sidebar_payload.object"
        :per_page="50"
        :key="grid_id"
        @photo_click="toggle_tag"
        @images="set_images"
      />
      <PhotoGrid
        v-if="sidebar_payload.class=='directory'"
        info_button
        :highlight_ids="higlighted_photos"
        :dimmed_ids="rejected_photos"
        :directory="sidebar_payload.object"
        :per_page="30"
        :key="grid_id"
        @photo_click="toggle_tag"
        @images="set_images"
      />
    </b-container>
  </b-sidebar>
</template>

<script>
import PhotoGrid from "@/components/browsing/PhotoGrid.vue";
import _ from "lodash";
import { BIconQuestionCircleFill } from "bootstrap-vue";
export default {
  name: "TaggingDrawer",
  components: { PhotoGrid, BIconQuestionCircleFill },
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
    },
    rejected_photos: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      show_sidebar: true,
      sidebar_grid_state: [],
      requests_processing: false,
      grid_id: 0,
      show_help: false
    };
  },
  computed: {
    sidebar_title() {
      return `${this.sidebar_payload.class}: ${this.sidebar_payload.object.label}`;
    },
    untagged_grid_photos() {
      return _.difference(
        this.sidebar_grid_state.map(p => p.id),
        _.union(this.higlighted_photos, this.rejected_photos)
      );
    },
    unaccepted_grid_photos() {
      return _.difference(
        this.sidebar_grid_state.map(p => p.id),
        this.higlighted_photos
      );
    },
    unrejected_grid_photos() {
      return _.difference(
        this.sidebar_grid_state.map(p => p.id),
        this.rejected_photos
      );
    }
  },
  methods: {
    set_images(payload) {
      this.sidebar_grid_state = payload;
      this.$emit("grid_state", this.sidebar_grid_state);
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
        this.untagged_grid_photos.map(pid => this.add_tag(pid))
      ).then(onfulfilled => {
        this.requests_processing = false;
        console.log(onfulfilled);
      });
    },
    reject_remaining_grid() {
      Promise.allSettled(
        this.untagged_grid_photos.map(pid => this.remove_tag(pid))
      ).then(onfulfilled => {
        this.requests_processing = false;
        console.log(onfulfilled);
      });
    }
  },
  watch: {
    sidebar_payload() {
      if (!!this.sidebar_payload.object) {
        this.show_help = false;
        this.grid_id += 1;
        this.show_sidebar = true;
      } else {
        this.show_help = false;
        this.grid_id += 1;
        this.show_sidebar = false;
      }
    }
  }
};
</script>