<template>
  <b-container fluid>
    <CloseMatchRunBar v-if="!!close_match_run" :close_match_run="close_match_run" />
    <router-view @set_submitted="set_submitted" />
  </b-container>
</template>

<script>
import { HTTP } from "@/main";
import CloseMatchRunBar from "@/components/close_match/CloseMatchRunBar.vue";
export default {
  name: "CloseMatchRun",
  components: { CloseMatchRunBar },
  props: {
    close_match_run_id: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      close_match_run: null
    };
  },
  methods: {
    get_close_match_run() {
      if (!!this.close_match_run_id) {
        return HTTP.get(`/close_match/run/${this.close_match_run_id}/`, {
          params: this.query_payload
        }).then(
          results => {
            this.close_match_run = results.data;
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    },
    set_submitted() {
      this.get_close_match_run();
    }
  },
  mounted() {
    this.get_close_match_run(this.$route.params.id);
  }
};
</script>