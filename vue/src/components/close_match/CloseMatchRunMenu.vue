<template>
  <b-list-group v-if="close_match_runs">
    <b-list-group-item v-for="cmr in close_match_runs" :key="cmr.id">
      <CloseMatchRunBar :close_match_run="cmr" />
      <b-row flex align-h="between" class="my-2 mx-0">
        <b-button
          variant="warning"
          size="sm"
          :to="{name: 'CloseMatchRunList', params: { id: cmr.id }}"
        >Review decisions</b-button>
        <b-button variant="primary" size="sm" @click="goto_next_set(cmr.id)">See next set</b-button>
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
  },
  methods: {
    goto_next_set(close_match_run_id) {
      return HTTP.get("/close_match/set/", {
        params: {
          limit: 1,
          invalid: false,
          not_signed_off: true,
          close_match_run: this.close_match_run_id
        }
      }).then(
        results => {
          this.$router.push({
            name: "CloseMatchRunDetail",
            params: {
              id: close_match_run_id,
              set_id: results.data.results[0].id
            }
          });
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