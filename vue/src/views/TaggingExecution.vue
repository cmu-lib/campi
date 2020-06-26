<template>
  <div>
    <p>Now let's get tagging with task {{ task_id }} on seed photo {{ seed_photo_id }}</p>
    <b-row>
      <b-col cols="6">
        <div v-if="!!sorted_photos">
          <b-row v-for="row in sorted_photos" :key="row.number">
            <b-col v-for="photograph in row.data" :key="photograph.id" cols="3">
              <b-img :src="photograph.image.square" />
              {{photograph.distance}}
            </b-col>
          </b-row>
        </div>
      </b-col>
      <b-col cols="6"></b-col>
    </b-row>
  </div>
</template>

<script>
import { HTTP } from "@/main";
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
      nearest_neighbors: []
    };
  },
  computed: {
    sorted_photos() {
      if (this.nearest_neighbors.length > 0) {
        return [
          { number: 0, data: this.nearest_neighbors.slice(0, 3) },
          { number: 1, data: this.nearest_neighbors.slice(3, 6) },
          { number: 2, data: this.nearest_neighbors.slice(6, 9) }
        ];
      } else {
        return null;
      }
    }
  },
  methods: {
    get_nn_set() {
      HTTP.get(`tagging/task/${this.task_id}/get_nn/`, {
        params: { photograph: this.seed_photo_id, n_neighbors: 9 }
      }).then(
        response => {
          this.nearest_neighbors = response.data;
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  mounted() {
    this.get_nn_set();
  }
};
</script>