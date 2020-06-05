<template>
  <div>
    <b-row align-v="center" align-h="around">
      <b-button-group>
        <b-button
          :variant="accept_variant"
          size="sm"
          :pressed="close_match_set_membership.accepted==true"
          @click="accept"
        >
          <BIconCheck2 />
        </b-button>
        <b-button
          :variant="reject_variant"
          size="sm"
          :pressed="close_match_set_membership.accepted==false"
          @click="reject"
        >
          <BIconX />
        </b-button>
        <b-button variant="light" size="sm">
          <BIconStarFill v-if="is_primary" variant="warning" @click="claim_primary" />
          <BIconStar v-else @click="claim_primary" />
        </b-button>
      </b-button-group>
    </b-row>
    <b-img-lazy
      :src="close_match_set_membership.photograph.image.square"
      width="150"
      :id="popover_id"
    />
    <b-popover :target="popover_id" triggers="hover" placement="top">
      <template v-slot:title>{{ popover_title }}</template>
      <b-img :src="popover_preivew_src" />
    </b-popover>
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
    },
    primary: {
      type: Object,
      default: null
    },
    popup_size: {
      type: Number,
      default: 500
    }
  },
  data() {
    return {
      selection: null
    };
  },
  computed: {
    is_primary() {
      if (!!this.primary) {
        return this.primary.id == this.close_match_set_membership.photograph.id;
      }
      return false;
    },
    accept_variant() {
      if (this.close_match_set_membership.accepted == true) {
        return "success";
      } else {
        return "light";
      }
    },
    reject_variant() {
      if (this.close_match_set_membership.accepted == false) {
        return "danger";
      } else {
        return "light";
      }
    },
    popover_title() {
      return (
        this.close_match_set_membership.photograph.id +
        "-" +
        this.close_match_set_membership.distance
      );
    },
    popover_id() {
      return (
        "image-popover" +
        this.close_match_set_membership.id +
        "-" +
        this.close_match_set_membership.photograph.id
      );
    },
    popover_preivew_src() {
      return (
        this.close_match_set_membership.photograph.image.id +
        "/full/!" +
        this.popup_size +
        "," +
        this.popup_size +
        "/0/default.jpg"
      );
    }
  },
  methods: {
    claim_primary() {
      // Emits a signal to the match set to take status as the representative photo
      this.$emit("claim_primary", this.close_match_set_membership.photograph);
    },
    cancel_primary() {
      this.$emit("cancel_primary", this.close_match_set_membership.photograph);
    },
    accept() {
      this.$emit("accept", this.close_match_set_membership.id);
    },
    reject() {
      this.$emit("reject", this.close_match_set_membership.id);
    }
  },
  watch: {
    primary() {
      if (this.primary) {
        this.accept();
      }
    }
  }
};
</script>