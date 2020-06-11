<template>
  <b-list-group v-if="close_match_runs">
    <b-list-group-item v-for="cmr in close_match_runs" :key="cmr.id" :active="cmr.id==value">
      <h6>CMR {{ cmr.id }}</h6>
      <b-button size="sm" @click="select_cmr(cmr)" block>Evaluate</b-button>
      <p>{{ cmr.pytorch_model.label }} - trees</p>
      <p>{{ cmr.max_neighbors }} neighbors, >{{ cmr.exclude_future_distance }} and >{{ cmr.cutoff_distance }}</p>
      <p>{{ cmr.n_sets }} sets</p>
    </b-list-group-item>
  </b-list-group>
</template>

<script>
import { HTTP } from "@/main";
export default {
  name: "CloseMatchRunMenu",
  props: {
    value: {
      type: Number,
      default: null
    }
  },
  asyncComputed: {
    close_match_runs() {
      return HTTP.get("/close_match/run/").then(
        results => {
          return results.data.results;
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  methods: {
    select_cmr(cmr) {
      this.$emit("input", cmr.id);
    }
  }
};
</script>

<style>
p {
  font-size: small;
}
</style>