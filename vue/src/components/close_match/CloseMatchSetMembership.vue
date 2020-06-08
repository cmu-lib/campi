<template>
  <b-card no-body>
    <template v-slot:header>
      <b-row flex align-h="between">
        <span class="info-badges">
          <b-badge
            class="mx-1"
            variant="warning"
            v-if="close_match_set_membership.distance==0.0"
            v-b-tooltip.hover
            title="This is the seed photograph used as the starting point of the search"
          >
            <BIconAward />
          </b-badge>
          <b-badge
            class="mx-1"
            variant="warning"
            v-else-if="close_match_set_membership.distance <= close_match_run.exclude_future_distance"
            v-b-tooltip.hover
            title="This photo is so similar to the the seed photograph that it won't be included in future potential match sets"
          >
            <BIconConeStriped />
          </b-badge>
          <b-badge class="mx-1" variant="primary" :title="directory_tooltip" v-b-tooltip.hover>
            <BIconFolderFill />
          </b-badge>
          <b-badge class="mx-1" variant="info" v-if="!!close_match_set_membership.photograph.job">
            <BIconCamera v-b-tooltip.hover :title="job_tooltip" />
          </b-badge>
        </span>
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
          <b-button v-if="is_primary" variant="secondary" size="sm" @click="cancel_primary">
            <BIconStarFill variant="warning" />
          </b-button>
          <b-button v-else variant="secondary" size="sm" @click="claim_primary">
            <BIconStar />
          </b-button>
        </b-button-group>
      </b-row>
    </template>
    <b-img-lazy
      :src="close_match_set_membership.photograph.image.thumbnail"
      width="300"
      :id="popover_id"
      class="m-0"
    />
    <b-popover :target="popover_id" triggers="hover" placement="top">
      <template v-slot:title>{{ popover_title }}</template>
      <b-img :src="popover_preivew_src" />
    </b-popover>
    <template v-slot:footer>
      <b-row align-h="between">
        <span>{{ close_match_set_membership.photograph.filename }}</span>
        <span>Distance: {{ close_match_set_membership.distance.toFixed(3) }}</span>
      </b-row>
    </template>
  </b-card>
</template>

<script>
import {
  BIconStar,
  BIconStarFill,
  BIconCheck2,
  BIconX,
  BIconCamera,
  BIconFolderFill,
  BIconConeStriped,
  BIconAward
} from "bootstrap-vue";
export default {
  name: "CloseMatchSetMembership",
  components: {
    BIconStar,
    BIconStarFill,
    BIconCheck2,
    BIconX,
    BIconCamera,
    BIconFolderFill,
    BIconConeStriped,
    BIconAward
  },
  props: {
    close_match_set_membership: {
      type: Object,
      required: true
    },
    close_match_run: {
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
    directory_tooltip() {
      return `Directory: ${this.close_match_set_membership.photograph.directory.label}`;
    },
    job_tooltip() {
      if (
        this.close_match_set_membership.photograph.job.label ==
        this.close_match_set_membership.photograph.job.job_code
      ) {
        return `Job: ${this.close_match_set_membership.photograph.job.job_code}`;
      } else {
        return `Job: ${this.close_match_set_membership.photograph.job.label} (${this.close_match_set_membership.photograph.job.job_code})`;
      }
    },
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
        return "secondary";
      }
    },
    reject_variant() {
      if (this.close_match_set_membership.accepted == false) {
        return "danger";
      } else {
        return "secondary";
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
      this.cancel_primary();
      this.$emit("reject", this.close_match_set_membership.id);
    }
  },
  watch: {
    primary() {
      if (this.primary == this.close_match_set_membership.photograph) {
        this.accept();
      }
    }
  }
};
</script>

<style>
.info-badges {
  font-size: x-large;
}
</style>