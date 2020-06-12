<template>
  <b-card v-if="!!close_match_run" class="my-1">
    <b-row flex align-h="between" class="px-3 py-0 my-0">
      <span class="lead">CMR {{ close_match_run.id }}</span>
      <span>Model: {{ close_match_run.pytorch_model.label }}</span>
      <span>window: {{ close_match_run.exclude_future_distance }}-{{ close_match_run.cutoff_distance }} (min. samples: {{ close_match_run.min_samples }})</span>
      <span>{{ close_match_run.n_sets }} total sets</span>
    </b-row>
    <small>Completion</small>
    <b-progress
      :value="close_match_run.n_complete"
      :max="close_match_run.n_sets"
      v-b-tooltip:hover
      :title="`${close_match_run.n_complete} sets reviewed`"
    />
  </b-card>
</template>

<script>
export default {
  name: "CloseMatchRunBar",
  props: {
    close_match_run: {
      type: Object,
      required: true
    }
  }
};
</script>