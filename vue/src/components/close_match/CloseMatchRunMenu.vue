<template>
  <b-list-group v-if="close_match_runs">
    <b-list-group-item v-for="cmr in close_match_runs" :key="cmr.id" :active="cmr.id==value">
      <CloseMatchRunBar :close_match_run="cmr" />
      <b-row flex align-h="between" class="my-2 mx-0">
        <b-button
          variant="warning"
          size="sm"
          :to="{name: 'CloseMatchRunList', params: { id: cmr.id }}"
        >Evaluate</b-button>
        <b-button variant="info" size="sm" :href="cmr.download_matches">Download results</b-button>
      </b-row>
    </b-list-group-item>
  </b-list-group>
</template>

<script>
import { HTTP } from "@/main";
import CloseMatchRunBar from "@/components/close_match/CloseMatchRunBar.vue";
export default {
  name: "CloseMatchRunMenu",
  components: {
    CloseMatchRunBar
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
  }
};
</script>

<style>
p {
  font-size: small;
}
</style>