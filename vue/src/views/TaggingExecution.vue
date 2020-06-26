<template>
  <b-row>
    <b-col cols="6">
      <p>Now let's get tagging with task {{ task_id }} on seed photo {{ seed_photo_id }}</p>
    </b-col>
    <b-col cols="6">
      <p>and here's the detail view</p>
    </b-col>
  </b-row>
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
      photos: [],
      task: null,
      offset: 0
    };
  },
  methods: {
    get_seed_distances(photograph_id) {
      HTTP.get("full_distances/", {
        query: {
          photograph: photograph_id,
          limit: 9,
          offset: this.offset,
          task: this.task_id
        }
      }).then(
        response => {
          if (response.data.count == 0) {
            this.cache_seed_distances(photograph_id);
          } else {
            this.photos = response.data.results;
          }
        },
        error => {
          console.log(error);
        }
      );
    },
    get_task(task_id) {
      HTTP.get("full_distances/", {
        query: {
          photograph: photograph_id,
          limit: 9,
          offset: this.offset,
          task: this.task_id
        }
      }).then(
        response => {
          if (response.data.count == 0) {
            this.cache_seed_distances(photograph_id);
          } else {
            this.photos = response.data.results;
          }
        },
        error => {
          console.log(error);
        }
      );
    },
    cache_seed_distances(pytorch_model_id, photograph_id) {
      HTTP.post(`pytorch_model/${pytorch_model_id}/`, {
        photograph: photograph_id
      }).then(
        results => {},
        error => {
          console.log(error);
        }
      );
    }
  }
};
</script>