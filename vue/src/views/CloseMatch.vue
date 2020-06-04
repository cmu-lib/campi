<template>
  <b-container fluid>
    <b-alert
      show
      variant="warning"
    >This is for display only now. None of the buttons are functioning for data entry yet :)</b-alert>
    <b-row>
      <b-col cols="3">
        <CloseMatchRunMenu v-model="close_match_run_id" />
      </b-col>
      <b-col cols-9 v-if="!!close_match_sets">
        <CloseMatchSet v-for="cms in close_match_sets" :key="cms.id" :close_match_set="cms" />
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
import CloseMatchRunMenu from "@/components/close_match/CloseMatchRunMenu.vue";
import CloseMatchSet from "@/components/close_match/CloseMatchSet.vue";
export default {
  name: "CloseMatch",
  components: { CloseMatchRunMenu, CloseMatchSet },
  data() {
    return {
      close_match_run_id: null
    };
  },
  asyncComputed: {
    close_match_sets() {
      if (!!this.close_match_run_id) {
        return HTTP.get("/close_match/set/", {
          params: { close_match_run: this.close_match_run_id, limit: 100 }
        }).then(
          results => {
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