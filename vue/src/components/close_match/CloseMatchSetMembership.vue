<template>
  <b-card :border-variant="border_variant" :bg-variant="background_variant" v-if="show_membership">
    <template v-slot:header>
      <b-row flex align-h="between">
        <span class="info-badges">
          <b-badge class="mx-1" variant="primary" :title="directory_tooltip" v-b-tooltip.hover>
            <BIconFolderFill />
          </b-badge>
          <b-badge class="mx-1" variant="info" v-if="!!close_match_set_membership.photograph.job">
            <BIconCamera v-b-tooltip.hover :title="job_tooltip" />
          </b-badge>
          <b-badge
            v-if="close_match_set_membership.invalid"
            variant="danger"
            v-b-tooltip.hover
            title="This photo has already been reviewed and added to another match set by an editor."
          >ALREADY COMMITTED</b-badge>
        </span>
        <b-button-toolbar>
          <b-button
            v-if="!close_match_set_membership.core"
            variant="warning"
            class="mx-1"
            size="sm"
            @click="photo_search"
            v-b-tooltip.hover
            title="This photo appears in other sets. Click to display all sets."
          >
            <BIconSearch />
          </b-button>
          <b-button-group>
            <b-button
              :variant="accept_variant"
              size="sm"
              :pressed="close_match_set_membership.accepted==true"
              @click="accept"
              v-b-tooltip.hover
              title="Keep this photo in this match set (will remove it from any other unapproved set.)"
            >
              <BIconCheck2 />
            </b-button>
            <b-button
              :variant="reject_variant"
              size="sm"
              :pressed="close_match_set_membership.accepted==false"
              @click="reject"
              v-b-tooltip.hover
              title="Reject this photo from the match set (it may still show up in later match sets.)"
            >
              <BIconX />
            </b-button>
            <b-button
              :variant="eliminate_variant"
              size="sm"
              @click="toggle_eliminate"
              :pressed="eliminated"
              v-b-tooltip.hover
              title="Eliminate this photo from this AND ALL OTHER MATCH SETS."
            >
              <BIconExclamationOctagonFill />
            </b-button>
            <b-button
              v-if="is_primary"
              variant="secondary"
              size="sm"
              @click="cancel_primary"
              v-b-tooltip.hover
              title="Mark this as the representative photo of the match set."
            >
              <BIconStarFill variant="warning" />
            </b-button>
            <b-button
              v-else
              variant="secondary"
              size="sm"
              @click="claim_primary"
              v-b-tooltip.hover
              title="Mark this as the representative photo of the match set."
            >
              <BIconStar />
            </b-button>
          </b-button-group>
        </b-button-toolbar>
      </b-row>
    </template>
    <div @click="$bvModal.show(popover_id)" class="magnify">
      <b-img-lazy
        :src="close_match_set_membership.photograph.image.thumbnail"
        width="300"
        class="m-0"
      />
    </div>
    <b-modal :id="popover_id" size="xl" centered hide-footer :title="popover_title">
      <b-row align-h="center">
        <b-img :src="popover_preivew_src" :width="popup_size" />
      </b-row>
    </b-modal>
    <template v-slot:footer>
      <b-row align-h="between">
        <small>{{ close_match_set_membership.photograph.filename }}</small>
        <small v-if="close_match_set_membership.core">Core</small>
        <small v-else>Secondary</small>
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
  BIconSearch,
  BIconExclamationOctagonFill
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
    BIconSearch,
    BIconExclamationOctagonFill
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
    searched_photo: {
      type: Number,
      default: null
    },
    show_invalid: {
      type: Boolean,
      default: false
    },
    popup_size: {
      type: Number,
      default: 900
    },
    eliminated: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {};
  },
  computed: {
    show_membership() {
      return this.show_invalid | !this.close_match_set_membership.invalid;
    },
    background_variant() {
      if (this.close_match_set_membership.invalid) {
        return "secondary";
      } else {
        return null;
      }
    },
    border_variant() {
      if (!!this.searched_photo) {
        if (
          this.searched_photo == this.close_match_set_membership.photograph.id
        ) {
          return "danger";
        }
      }
      return null;
    },
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
    eliminate_variant() {
      if (this.eliminated) {
        return "warning";
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
      return `${this.close_match_set_membership.photograph.id} - ${this.close_match_set_membership.photograph.filename}`;
    },
    popover_id() {
      return `image-popover${this.close_match_set_membership.id}-${this.close_match_set_membership.photograph.id}`;
    },
    popover_preivew_src() {
      return `${this.close_match_set_membership.photograph.image.id}/full/!${this.popup_size},${this.popup_size}/0/default.jpg`;
    }
  },
  methods: {
    show_modal() {
      this.$bvModal.show(this.popover_id);
    },
    photo_search() {
      this.$emit("photo_search", this.close_match_set_membership.photograph.id);
    },
    claim_primary() {
      // Emits a signal to the match set to take status as the representative photo
      this.$emit("claim_primary", this.close_match_set_membership.photograph);
    },
    cancel_primary() {
      this.$emit("cancel_primary", this.close_match_set_membership.photograph);
    },
    toggle_eliminate() {
      if (this.eliminated) {
        this.$emit(
          "uneliminate",
          this.close_match_set_membership.photograph.id
        );
      } else {
        this.$emit("eliminate", this.close_match_set_membership.photograph.id);
      }
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
    },
    eliminated() {
      if (this.eliminated) {
        this.reject();
      }
    }
  }
};
</script>

<style>
.info-badges {
  font-size: x-large;
}
.magnify {
  cursor: zoom-in;
}
</style>