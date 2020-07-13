<template>
  <div>
    <b-alert variant="info" :show="loading">Loading new results - this may take a few seconds...</b-alert>
    <b-overlay :show="loading">
      <b-row>
        <b-col cols="6">
          <div v-if="!!sorted_photos">
            <b-card no-body>
              <template v-slot:header>
                <b-row align-h="between" align-v="center" class="px-2">
                  <span>Click photo to inspect and tag related photos in job/directory</span>
                  <b-button
                    size="sm"
                    @click="submit_choices"
                    title="Discard the rest of this grid and draw more photos from the similarity results"
                  >Get more photos...</b-button>
                </b-row>
              </template>
              <b-list-group flush>
                <b-list-group-item v-for="row in sorted_photos" :key="row.number">
                  <b-row align-h="between" align-v="center">
                    <b-img
                      v-for="photograph in row.data"
                      height="230"
                      width="230"
                      :key="photograph.id"
                      :src="photograph.image.square"
                      class="pointer"
                      :class="{'approved': accepted_photo_ids.includes(photograph.id)}"
                      @click="get_info(photograph)"
                    />
                  </b-row>
                </b-list-group-item>
              </b-list-group>
            </b-card>
          </div>
        </b-col>
        <b-col v-if="!loading" cols="6">
          <PhotoDetail
            :key="detail_photo.id"
            v-if="!!detail_photo & !!task"
            :photograph="detail_photo"
            :available_tags="available_tags"
            :task_tag="task.tag"
            @new_tagged_photo="remove_photo"
            @new_seed_photo="new_seed_photo"
            @close_photo_detail="detail_photo=null"
            @activate_sidebar="activate_sidebar"
          />

          <b-alert
            v-else
            show
            variant="primary"
          >Click a photo at right to inspect and tag it and the other photographs in its associated job / directory.</b-alert>
          <TaggingDrawer
            v-if="!!sidebar_payload.object"
            :sidebar_payload="sidebar_payload"
            :task="task"
            :higlighted_photos="tagged_photos"
            @add_tag="add_tag"
            @remove_tag="remove_tag"
          />
        </b-col>
      </b-row>
    </b-overlay>
  </div>
</template>

<script>
import { HTTP } from "@/main";
import _ from "lodash";
import PhotoDetail from "@/components/tagging/PhotoDetail.vue";
import TaggingDrawer from "@/components/tagging/TaggingDrawer.vue";

export default {
  name: "TaggingExecution",
  components: { PhotoDetail, TaggingDrawer },
  props: {
    task_id: {
      type: Number,
      required: true
    },
    seed_photo_id: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      task: null,
      nearest_neighbor_set: [],
      photo_decisions: [],
      loading: false,
      detail_photo: null,
      available_tags: [],
      sidebar_payload: {}
    };
  },
  computed: {
    decided_photo_ids() {
      return this.photo_decisions.map(d => d.photograph);
    },
    accepted_photo_ids() {
      return this.photo_decisions
        .filter(d => d.is_applicable == true)
        .map(d => d.photograph);
    },
    displayed_photos() {
      return this.nearest_neighbor_set.slice(0, 9);
    },
    sorted_photos() {
      // Structure the photos into a 9x9 grid
      if (this.displayed_photos.length > 0) {
        return [
          { number: 0, data: this.displayed_photos.slice(0, 3) },
          { number: 1, data: this.displayed_photos.slice(3, 6) },
          { number: 2, data: this.displayed_photos.slice(6, 9) }
        ];
      } else {
        return null;
      }
    },
    undecided_photo_ids() {
      // Photos that the user hasn't made a decision on yet. When a new set is scrolled up, any photos without a decision on them are decided FALSE
      return _.difference(
        this.displayed_photos.map(p => p.id),
        _.union(this.photo_decisions.map(d => d.photograph))
      );
    },
    tagged_photos() {
      // List of photo ids that are actively tagged
      return this.photo_decisions
        .filter(d => d.is_applicable)
        .map(d => d.photograph_id);
    }
  },
  methods: {
    new_seed_photo(photograph) {
      this.$router.push({
        name: "TaggingExecution",
        params: { task_id: this.task_id, seed_photo_id: photograph.id }
      });
      this.get_nn_set();
    },
    activate_sidebar(payload) {
      this.sidebar_payload = payload;
    },
    pop_neighbors() {
      // Remove those 9 from the nearest neighbor queue
      this.nearest_neighbor_set.splice(0, 9);
    },
    remove_photo(photograph) {
      console.log(photograph);
      const photo_index = _.findIndex(this.nearest_neighbor_set, {
        id: photograph.id
      });
      if (photo_index > -1) {
        console.log(photo_index);
        console.log(this.nearest_neighbor_set[photo_index]);
        this.nearest_neighbor_set.splice(photo_index, 1);
      }
    },
    derive_photo_decisions(photographs) {
      // Create a list of photo ids, decision ids, and true/false values
      const photo_decisions = photographs
        .filter(p => p.decisions.length > 0)
        .map(p =>
          p.decisions
            .filter(d => (d.task = this.task_id))
            .map(d => {
              return {
                photograph_id: p.id,
                decision_id: d.id,
                is_applicable: d.is_applicable
              };
            })
        )
        .flat();
      console.log(photo_decisions);
      return photo_decisions;
    },
    get_nn_set(func = null) {
      this.loading = true;
      HTTP.get(`tagging/task/${this.task_id}/get_nn/`, {
        params: { photograph: this.seed_photo_id, n_neighbors: 90 }
      }).then(
        response => {
          this.nearest_neighbor_set = response.data;
          this.photo_decisions = this.derive_photo_decisions(
            this.nearest_neighbor_set
          );
          this.loading = false;
          if (!!func) {
            // An additional function to run once a new set of photos has been loaded
            func();
          }
        },
        error => {
          console.log(error);
          this.loading = false;
        }
      );
    },
    is_photo_decided(photograph_id) {
      return this.photo_decisions
        .map(p => p.photograph_id)
        .includes(photograph_id);
    },
    toggle_photo(photograph_id) {
      if (this.decided_photo_ids.includes(photograph_id)) {
        this.add_tag(photograph_id);
      } else {
        this.remove_tag(photograph_id);
      }
    },
    add_tag(photograph_id) {
      this.set_tag(photograph_id, true);
    },
    remove_tag(photograph_id) {
      this.set_tag(photograph_id, false);
    },
    set_tag(photograph_id, value) {
      if (this.is_photo_decided(photograph_id)) {
        const photo_decision = _.find(this.photo_decisions, {
          photograph_id: photograph_id
        });
        this.update_decision(photo_decision.id, value);
      } else {
        this.create_decision(photograph_id, value);
      }
    },
    response_to_decision(response) {
      return {
        photograph_id: response.data.photograph,
        decision_id: response.data.id,
        is_applicable: response.data.is_applicable
      };
    },
    update_decision(decision_id, value) {
      HTTP.patch(`tagging/decision/${decision_id}/`, {
        is_applicable: value
      }).then(
        response => {
          const decision_index = _.findIndex(this.photo_decisions, {
            decision_id: decision_id
          });
          this.photo_decisions.splice([decision_index], 1);
          this.photo_decisions.push(this.response_to_decision(response));
        },
        error => {
          console.log(error);
        }
      );
    },
    create_decision(photograph_id, value) {
      HTTP.post("tagging/decision/", {
        task: this.task_id,
        photograph: photograph_id,
        is_applicable: value
      }).then(
        response => {
          // Add the decision (whether True or False) to the local tracking array
          this.photo_decisions.push(this.response_to_decision(response));
        },
        error => {
          console.log(error);
        }
      );
    },
    submit_choices() {
      Promise.all(this.undecided_photo_ids.map(id => this.remove_tag(id))).then(
        onfulfilled => {
          console.log(onfulfilled);
          this.photo_decisions = [];
          this.load_more_photos();
        }
      );
    },
    load_more_photos() {
      if (this.nearest_neighbor_set.length == 0) {
        this.get_nn_set(); //this.pop_neighbors
      } else {
        this.pop_neighbors();
      }
      this.detail_photo_id = null;
    },
    get_info(photograph) {
      this.detail_photo = photograph;
    },
    get_available_tags() {
      HTTP.get("tagging/tag/").then(
        response => {
          this.available_tags = response.data.results;
        },
        error => {
          console.log(error);
        }
      );
    },
    get_task() {
      HTTP.get(`tagging/task/${this.task_id}/`).then(
        response => {
          this.task = response.data;
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  mounted() {
    this.get_available_tags();
    this.get_task();
    this.get_nn_set();
  },
  detail_photo() {
    // Reset the sidebar anytime a new photo detail is chosen.
    this.sidebar_payload = {};
  }
};
</script>

<style>
img.approved {
  outline: 3px solid red;
}
</style>