<template>
  <div>
    <p>Now let's get tagging with task {{ task_id }} on seed photo {{ seed_photo_id }}</p>
    <p v-if="loading">Loading new results - this may take a few seconds...</p>
    <b-overlay :show="loading">
      <b-row>
        <b-col cols="6">
          <div v-if="!!sorted_photos">
            <b-row v-for="row in sorted_photos" :key="row.number">
              <b-col v-for="photograph in row.data" :key="photograph.id" cols="3">
                <b-img :src="photograph.image.square" @click="approve_photo(photograph)" />
                <p>{{ photograph.id }}-{{ photograph.distance }}</p>
              </b-col>
            </b-row>
          </div>
          {{ accepted_neighbors }}
          {{ unaccepted_photos }}
          <b-button @click="submit_choices">Get more photos...</b-button>
        </b-col>
        <b-col cols="6"></b-col>
      </b-row>
    </b-overlay>
  </div>
</template>

<script>
import { HTTP } from "@/main";
import _ from "lodash";
export default {
  name: "TaggingExecution",
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
      nearest_neighbors: [],
      current_neighbors: [],
      accepted_neighbors: [],
      loading: false
    };
  },
  computed: {
    sorted_photos() {
      if (this.current_neighbors.length > 0) {
        return [
          { number: 0, data: this.current_neighbors.slice(0, 3) },
          { number: 1, data: this.current_neighbors.slice(3, 6) },
          { number: 2, data: this.current_neighbors.slice(6, 9) }
        ];
      } else {
        return null;
      }
    },
    unaccepted_photos() {
      var diffs = _.difference(
        this.current_neighbors.map(p => p.id),
        this.accepted_neighbors
      );
      console.log(diffs);
      return diffs;
    }
  },
  methods: {
    pop_neighbors() {
      this.current_neighbors = this.nearest_neighbors.slice(0, 9);
      this.nearest_neighbors = this.nearest_neighbors.slice(
        9,
        this.nearest_neighbors.length
      );
    },
    get_nn_set(func = null) {
      this.loading = true;
      HTTP.get(`tagging/task/${this.task_id}/get_nn/`, {
        params: { photograph: this.seed_photo_id, n_neighbors: 90 }
      }).then(
        response => {
          this.nearest_neighbors = response.data;
          this.loading = false;
          if (!!func) {
            func();
          }
        },
        error => {
          console.log(error);
          this.loading = false;
        }
      );
    },
    approve_photo(photograph) {
      HTTP.post("tagging/decision/", {
        task: this.task_id,
        photograph: photograph.id,
        is_applicable: true
      }).then(response => {
        this.accepted_neighbors.push(response.data.photograph);
      });
    },
    submit_choices() {
      Promise.all(
        this.unaccepted_photos.map(id =>
          HTTP.post("tagging/decision/", {
            task: this.task_id,
            photograph: id,
            is_applicable: false
          })
        )
      ).then(onfulfilled => {
        console.log(onfulfilled);
        this.accepted_neighbors = [];
        this.load_more_photos();
      });
    },
    load_more_photos() {
      if (this.nearest_neighbors.length == 0) {
        this.get_nn_set(this.pop_neighbors);
      } else {
        this.pop_neighbors();
      }
    }
  },
  mounted() {
    this.get_nn_set(this.pop_neighbors);
  }
};
</script>