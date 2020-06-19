<template>
  <b-container>
    <b-alert show variant="info" class="my-2">
      <h2>Select a close match run</h2>
      <p></p>
    </b-alert>
    <CloseMatchRunMenu />
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