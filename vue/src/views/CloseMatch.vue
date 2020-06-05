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
      <b-col cols-9>
        <router-view v-if="!!close_match_run_id" />
        <b-alert v-else show variant="info">
          <h2>Select a close match run at left to begin review</h2>
        </b-alert>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import CloseMatchRunMenu from "@/components/close_match/CloseMatchRunMenu.vue";
export default {
  name: "CloseMatch",
  components: { CloseMatchRunMenu },
  data() {
    return {
      close_match_run_id: null
    };
  },
  watch: {
    close_match_run_id() {
      this.$router.push({
        name: "CloseMatchRun",
        params: { id: this.close_match_run_id }
      });
    }
  },
  created() {
    if (!!this.$route.params.id) {
      this.close_match_run_id = Number(this.$route.params.id);
    }
  }
};
</script>