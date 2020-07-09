<template>
  <div>
    <p v-if="loading">Loading new results - this may take a few seconds...</p>
    <b-overlay :show="loading">
      <b-row>
        <b-col cols="6">
          <div v-if="!!sorted_photos">
            <b-card header="Photos for consideration" no-body>
              <b-list-group flush>
                <b-list-group-item v-for="row in sorted_photos" :key="row.number">
                  <b-row align-h="between" align-v="center">
                    <PhotoSquare
                      v-for="photograph in row.data"
                      :key="photograph.id"
                      :photograph="photograph"
                      :approved="accepted_photo_ids.includes(photograph.id)"
                      @toggle_photo="toggle_photo"
                      @get_info="get_info"
                    />
                  </b-row>
                </b-list-group-item>
              </b-list-group>
            </b-card>
          </div>
          <b-button @click="submit_choices">Get more photos...</b-button>
        </b-col>
        <b-col cols="6">
          <PhotoDetail
            :key="detail_photo_id + reset_counter"
            v-if="!!detail_photo_id & !!task"
            :photograph_id="detail_photo_id"
            :available_tags="available_tags"
            :task_tag="task.tag"
          />
        </b-col>
      </b-row>
    </b-overlay>
  </div>
</template>

<script>
import { HTTP } from "@/main";
import _ from "lodash";
import PhotoSquare from "@/components/tagging/PhotoSquare.vue";
import PhotoDetail from "@/components/tagging/PhotoDetail.vue";
export default {
  name: "TaggingExecution",
  components: { PhotoSquare, PhotoDetail },
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
      displayed_photos: [],
      photo_decisions: [],
      loading: false,
      detail_photo_id: null,
      reset_counter: 0,
      available_tags: []
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
    }
  },
  methods: {
    pop_neighbors() {
      // Get up to nine photographs from the downloaded set
      this.displayed_photos = this.nearest_neighbor_set.slice(0, 9);
      // Remove those 9 from the nearest neighbor queue
      this.nearest_neighbor_set = this.nearest_neighbor_set.slice(9);
    },
    get_nn_set(func = null) {
      this.loading = true;
      HTTP.get(`tagging/task/${this.task_id}/get_nn/`, {
        params: { photograph: this.seed_photo_id, n_neighbors: 90 }
      }).then(
        response => {
          this.nearest_neighbor_set = response.data;
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
    toggle_photo(photograph) {
      if (this.decided_photo_ids.includes(photograph.id)) {
        // Get the associated photo decision and reverse it
        const photo_decision = _.find(this.photo_decisions, {
          photograph: photograph.id
        });
        this.update_decision(photo_decision.id, !photo_decision.is_applicable);
      } else {
        this.create_decision(photograph.id, true);
      }
    },
    update_decision(decision_id, value) {
      HTTP.patch(`tagging/decision/${decision_id}/`, {
        is_applicable: value
      }).then(
        response => {
          const decision_index = _.findIndex(this.photo_decisions, {
            id: decision_id
          });
          this.photo_decisions.splice([decision_index], 1);
          this.photo_decisions.push(response.data);
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
          this.photo_decisions.push(response.data);
        },
        error => {
          console.log(error);
        }
      );
    },
    submit_choices() {
      Promise.all(
        this.undecided_photo_ids.map(id =>
          HTTP.post("tagging/decision/", {
            task: this.task_id,
            photograph: id,
            is_applicable: false
          })
        )
      ).then(onfulfilled => {
        console.log(onfulfilled);
        this.photo_decisions = [];
        this.load_more_photos();
      });
    },
    load_more_photos() {
      if (this.nearest_neighbor_set.length == 0) {
        this.get_nn_set(this.pop_neighbors);
      } else {
        this.pop_neighbors();
      }
      this.detail_photo_id = null;
    },
    get_info(photograph) {
      this.detail_photo_id = photograph.id;
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
    this.get_nn_set(this.pop_neighbors);
  },
  watch: {
    photo_decisions() {
      // this.reset_counter += 1;
    }
  }
};
</script>