<template>
  <div>
    <b-alert
      variant="info"
      :show="loading"
    >Computing a set of visually-similar images - this may take a few seconds...</b-alert>
    <b-overlay :show="loading">
      <b-row v-if="!loading">
        <b-col cols="6">
          <div>
            <b-card no-body>
              <template v-slot:header>
                <b-row align-h="between" align-v="center" class="px-2">
                  <span>Click a photo to inspect and tag other photos in the same job/directory</span>
                  <b-button
                    size="sm"
                    @click="submit_choices"
                    title="Discard the rest of this grid and draw more photos from the similarity results"
                    v-b-tooltip:hover
                  >Get more photos...</b-button>
                </b-row>
              </template>
              <b-list-group flush v-if="!!sorted_photos">
                <b-list-group-item v-for="row in sorted_photos" :key="row.number">
                  <b-row align-h="between" align-v="center">
                    <b-img
                      v-for="photograph in row.data"
                      height="230"
                      width="230"
                      :key="photograph.id"
                      :src="photograph.image.square"
                      class="pointer"
                      @click="get_info(photograph)"
                    />
                  </b-row>
                </b-list-group-item>
              </b-list-group>
            </b-card>
          </div>
        </b-col>
        <b-col cols="6">
          <PhotoDetail
            :key="detail_photo.id"
            v-if="!!detail_photo & !!task"
            :photograph="detail_photo"
            :available_tags="available_tags"
            :highlighted_photos="tagged_photos"
            :task_tag="task.tag"
            @new_tagged_photo="remove_photo"
            @new_seed_photo="new_seed_photo"
            @close_photo_detail="detail_photo=null"
            @activate_sidebar="activate_sidebar"
            @add_tag="add_tag"
            @remove_tag="remove_tag"
          />

          <b-alert v-else show variant="primary">
            <p>Click a photo at left to inspect and tag it and the other photographs in its associated job / directory.</p>
            <p>As you add tags to photographs within jobs, photos will get removed from the stack of similar photos at left. If none of the photos in the stack look relevant, click the "Get more photos..." button to pull up another set.</p>
            <p>If you stop getting relevant photos, you may click on "Choose seed photo" above to backtrack and pick a new, different-looking seed photograph that may pull up other relevant photos.</p>
            <p>
              <strong>When you want to stop working on a tag, be sure to click on the tag button above with the X icon. This will check the tag back in and allow another user to check it out and continue work on it.</strong>
            </p>
          </b-alert>
          <TaggingDrawer
            v-if="!!sidebar_payload.object"
            :sidebar_payload="sidebar_payload"
            :task="task"
            :higlighted_photos="tagged_photos"
            :rejected_photos="negative_tagged_photos"
            @add_tag="add_tag"
            @remove_tag="remove_tag"
            @grid_state="update_grid_state"
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
      return this.photo_decisions.map(d => d.photograph_id);
    },
    accepted_photo_ids() {
      return this.photo_decisions
        .filter(d => d.is_applicable == true)
        .map(d => d.photograph_id);
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
    },
    negative_tagged_photos() {
      // List of photo ids that are actively tagged as negative
      return this.photo_decisions
        .filter(d => !d.is_applicable)
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
    update_grid_state(photographs) {
      console.log("Updating grid state");
      // Add any applicable tag decisions from the photo grid drawer to the cache of photo decisions
      photographs.map(p => {
        if (this.decided_photo_ids.includes(p.id)) {
          console.log(`Updating photo ${p.id} already in cache`);
          // Remove the cached decision and update from the current state
          const photo_index = _.findIndex(this.photo_decisions, {
            photograph_id: p.id
          });
          this.photo_decisions.splice(photo_index, 1);
          const decision = _.find(p.decisions, { task: this.task_id });
          this.photo_decisions.push({
            photograph_id: p.id,
            decision_id: decision.id,
            is_applicable: decision.is_applicable
          });
        }
        p.decisions.map(d => {
          console.log(`Decision ${d.id} for photo ${p.id}`);
          if (d.task == this.task_id) {
            console.log(`Adding decision data for ${p.id}`);
            this.photo_decisions.push({
              photograph_id: p.id,
              decision_id: d.id,
              is_applicable: d.is_applicable
            });
          }
        });
      });
    },
    derive_photo_decisions(photographs) {
      // Create a list of photo ids, decision ids, and true/false values
      const photo_decisions = photographs
        .filter(p => p.decisions.length > 0)
        .map(p =>
          p.decisions
            .filter(d => d.task == this.task_id)
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
        .map(d => d.photograph_id)
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
        this.update_decision(photo_decision.decision_id, value);
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
          this.photo_decisions.splice(decision_index, 1);
          this.photo_decisions.push(this.response_to_decision(response));
          this.remove_photo_from_deck(response.data.photograph);
          this.manage_related_photos(response.data.other_tagged_photos);
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
          this.remove_photo_from_deck(response.data.photograph);
          this.manage_related_photos(response.data.other_tagged_photos);
        },
        error => {
          console.log(error);
        }
      );
    },
    manage_related_photos(other_tagged_photos) {
      console.log("managing related pics");
      console.log(other_tagged_photos);
      other_tagged_photos
        .filter(op => op.tagging_decision.task == this.task_id)
        .map(op => {
          if (this.is_photo_decided(op.photograph.id)) {
            const related_decision_index = _.findIndex(this.photo_decisions, {
              decision_id: op.tagging_decision.id
            });
            this.photo_decisions.splice(related_decision_index, 1);
            this.remove_photo_from_deck(op.photograph.id);
          }
          this.photo_decisions.push({
            photograph_id: op.photograph.id,
            decision_id: op.tagging_decision.id,
            is_applicable: op.tagging_decision.is_applicable
          });
        });
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
    remove_photo_from_deck(photograph_id) {
      const nn_index = _.findIndex(this.nearest_neighbor_set, {
        id: photograph_id
      });
      if (nn_index > -1) {
        this.nearest_neighbor_set.splice(nn_index, 1);
      }
    },
    load_more_photos() {
      if (this.nearest_neighbor_set.length == 0) {
        this.get_nn_set(); //this.pop_neighbors
      } else {
        this.pop_neighbors();
      }
      this.detail_photo = null;
    },
    get_info(photograph) {
      this.detail_photo = photograph;
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
    this.get_task();
    this.get_nn_set();
  }
};
</script>
