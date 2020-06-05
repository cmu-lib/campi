<template>
  <div>
    <b-button-toolbar></b-button-toolbar>
    <b-row align-h="center">
      <b-overlay :show="loading">
        <CloseMatchSet v-for="cms in close_match_sets" :key="cms.id" :close_match_set="cms" />
      </b-overlay>
    </b-row>
  </div>
</template>

<script>
import { HTTP } from "@/main";
import CloseMatchSet from "@/components/close_match/CloseMatchSet.vue";
export default {
  name: "CloseMatchRun",
  components: { CloseMatchSet },
  props: {
    close_match_run_id: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      loading: null,
      page: 1
    };
  },
  asyncComputed: {
    close_match_sets() {
      if (!!this.close_match_run_id) {
        this.loading = true;
        return HTTP.get("/close_match/set/", {
          params: { close_match_run: this.close_match_run_id, limit: 100 }
        }).then(
          results => {
            this.loading = false;
            return results.data.results;
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    }
  }
};
</script>