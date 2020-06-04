<template>
  <b-card :header="match_set_header">
    <b-row flex align-v="center">
      <CloseMatchSetMembership
        v-for="cmsm in close_match_set.memberships"
        :key="cmsm.id"
        :close_match_set_membership="cmsm"
        class="m-3"
      />
    </b-row>
  </b-card>
</template>

<script>
import CloseMatchSetMembership from "@/components/close_match/CloseMatchSetMembership.vue";
export default {
  name: "CloseMatchSet",
  components: { CloseMatchSetMembership },
  props: {
    close_match_set: {
      type: Object,
      required: true
    }
  },
  data() {
    return {};
  },
  computed: {
    match_set_header() {
      return "Match set " + this.close_match_set.id;
    }
  }
};
</script>