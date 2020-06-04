<template>
  <b-list-group v-if="close_match_runs">
    <b-list-group-item v-for="cmr in close_match_runs" :key="cmr.id" :active="cmr.id==selected">
      <h6>{{ cmr.created_on }}</h6>
      <b-button size="sm" @click="select_cmr(cmr)" block>Evaluate</b-button>
      <b-row>
        <b-col cols="6">
          <p>Model: {{ cmr.pytorch_model.label }}</p>
          <p>Index trees: {{ cmr.annoy_idx.n_trees }}</p>
          <p>Sets: {{ cmr.n_sets }}</p>
        </b-col>
        <b-col cols="6">
          <p>Max neighbors: {{ cmr.max_neighbors }}</p>
          <p>Cutoff distance: {{ cmr.cutoff_distance }}</p>
          <p>Max neighbors: {{ cmr.max_neighbors }}</p>
        </b-col>
      </b-row>
    </b-list-group-item>
  </b-list-group>
</template>

<script>
import { HTTP } from "@/main";
export default {
  name: "CloseMatchRunMenu",
  data() {
    return {
      selected: null
    };
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
      this.selected = cmr.id;
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