<template>
  <div>
    <b-row>
      <b-button-group>
        <b-button variant="success" :pressed="selection==true">
          <BIconCheck2 />
        </b-button>
        <b-button variant="danger" :pressed="selection">
          <BIconX />
        </b-button>
      </b-button-group>
      <BIconStarFill v-if="primary" />
      <BIconStar v-else />
    </b-row>
    <b-img :src="close_match_set_membership.photograph.image.square" width="150" />
  </div>
</template>

<script>
import { BIconStar, BIconStarFill, BIconCheck2, BIconX } from "bootstrap-vue";
export default {
  name: "CloseMatchSetMembership",
  components: {
    BIconStar,
    BIconStarFill,
    BIconCheck2,
    BIconX
  },
  props: {
    close_match_set_membership: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      selection: null,
      primary: false
    };
  }
};
</script>