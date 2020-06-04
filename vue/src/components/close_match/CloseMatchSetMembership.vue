<template>
  <div>
    <b-row align-v="center" align-h="around">
      <b-button-group>
        <b-button
          :variant="accept_variant"
          size="sm"
          :pressed="selection==true"
          @click="selection=true"
        >
          <BIconCheck2 />
        </b-button>
        <b-button
          :variant="reject_variant"
          size="sm"
          :pressed="selection==false"
          @click="selection=false"
        >
          <BIconX />
        </b-button>
        <b-button variant="light" size="sm">
          <BIconStarFill v-if="primary" variant="warning" @click="primary_toggle" />
          <BIconStar v-else @click="primary_toggle" />
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
    popup_size: {
      type: Number,
      default: 500
    }
  },
  data() {
    return {
      selection: null,
      primary: false
    };
  },
  computed: {
    accept_variant() {
      if (this.selection == true) {
        return "success";
      } else {
        return "light";
      }
    },
    reject_variant() {
      if (this.selection == false) {
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
    primary_toggle() {
      this.primary = !this.primary;
    }
  },
  watch: {
    selection() {
      if (this.selection == false) {
        this.primary = false;
      }
    },
    primary() {
      if (this.primary) {
        this.selection = true;
      }
    }
  }
};
</script>