<template>
  <b-container>
    <b-row>
      <b-col cols="6">
        <CloseMatchRunMenu />
      </b-col>
      <b-col cols="6">
        <b-alert show variant="info">
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
    return {};
  }
};
</script>