<template>
  <b-card
    :border-variant="set_variant"
    :header-border-variant="set_variant"
    class="my-2"
    :no-body="collapsed"
  >
    <template v-slot:header>
      <b-row class="px-2" flex align-h="between" align-v="center">
        <span @click="collapsed=!collapsed">
          <BIconCaretRightFill v-if="collapsed" />
          <BIconCaretDownFill v-else />
        </span>
        <span>Match set {{ close_match_set.id }} ({{ close_match_set.memberships.length }} images)</span>
        <span v-if="close_match_set_state.overlapping" class="info-badges">
          <b-badge
            size="lg"
            class="mx-1"
            variant="warning"
            v-b-tooltip.hover
            title="This set contains photos that may also appear in other sets."
          >
            <BIconConeStriped />
          </b-badge>
        </span>
        <span
          v-if="modifying_user"
        >Reveiwed by {{ close_match_set_state.user_last_modified.username }} {{ from_now(close_match_set_state.last_updated) }}</span>
        <b-button-toolbar>
          <b-button-group>
            <b-button
              variant="success"
              size="sm"
              @click="accept_all"
              v-b-tooltip.hover
              title="Mark every photo as accepted. If you haven't starred a photo, it will star the first accepted one in the set."
            >
              <BIconCheck2All class="mr-1" />Accept all
            </b-button>
            <b-button
              variant="danger"
              size="sm"
              @click="reject_all"
              v-b-tooltip.hover
              title="Mark every photo as rejected."
            >
              <BIconXOctagon class="mr-1" />Reject all
            </b-button>
            <b-button
              variant="warning"
              size="sm"
              @click="eliminate_all"
              v-b-tooltip.hover
              title="Mark every photo as eliminated."
            >
              <BIconExclamationOctagonFill class="mr-1" />Eliminate All
            </b-button>
          </b-button-group>
          <b-button
            class="ml-2"
            variant="primary"
            size="sm"
            @click="register_set"
            v-b-tooltip.hover
            title="Save your judgments to the server. Any photo left blank will be automatically marked as 'rejected'"
          >
            <BIconCloudUpload v-if="!uploading" class="mr-1" />
            <b-spinner v-else small class="mr-1" />Save
          </b-button>
        </b-button-toolbar>
      </b-row>
    </template>
    <b-row flex v-if="!!close_match_set_state & !collapsed">
      <CloseMatchSetMembership
        v-for="cmsm in close_match_set_state.memberships"
        :key="cmsm.id"
        :close_match_set_membership="cmsm"
        :close_match_run="close_match_set_state.close_match_run"
        :primary="close_match_set_state.representative_photograph"
        :searched_photo="searched_photo"
        :show_invalid="show_invalid"
        :eliminated="eliminated_photographs.includes(cmsm.photograph.id)"
        class="m-2"
        @accept="accept"
        @reject="reject"
        @eliminate="eliminate"
        @uneliminate="uneliminate"
        @claim_primary="claim_primary"
        @cancel_primary="cancel_primary"
        @photo_search="photo_search"
      />
    </b-row>
    <b-toast :id="toast_id" :variant="toast_variant">
      <Nested :value="toast_response" />
    </b-toast>
  </b-card>
</template>

<script>
import { HTTP } from "@/main";
import moment from "moment";
import CloseMatchSetMembership from "@/components/close_match/CloseMatchSetMembership.vue";
import Nested from "@/components/Nested.vue";
import _ from "lodash";
import {
  BIconCheck2All,
  BIconXOctagon,
  BIconExclamationOctagonFill,
  BIconCloudUpload,
  BIconConeStriped,
  BIconCaretRightFill,
  BIconCaretDownFill
} from "bootstrap-vue";
export default {
  name: "CloseMatchSet",
  components: {
    CloseMatchSetMembership,
    BIconCheck2All,
    BIconXOctagon,
    BIconCloudUpload,
    BIconExclamationOctagonFill,
    BIconConeStriped,
    BIconCaretRightFill,
    BIconCaretDownFill,
    Nested
  },
  props: {
    close_match_set: {
      type: Object,
      required: true
    },
    collapsed: {
      type: Boolean,
      default: false
    },
    searched_photo: {
      type: Number,
      default: null
    },
    show_invalid: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      close_match_set_state: null,
      eliminated_photographs: [],
      toast_response: null,
      toast_variant: null,
      uploading: false
    };
  },
  computed: {
    has_secondary_images() {
      return this.close_match_set.memberships.some(x => !x.core);
    },
    toast_id() {
      return `toast-${this.close_match_set.id}`;
    },
    set_variant() {
      if (!!this.modifying_user) {
        return "success";
      }
      return "null";
    },
    modifying_user() {
      if (!!this.close_match_set_state) {
        return this.close_match_set_state.user_last_modified;
      }
      return null;
    },
    match_set_header() {
      return "Match set " + this.close_match_set.id;
    },
    close_match_approval() {
      var payload = {
        accepted_memberships: [],
        eliminated_photographs: [],
        representative_photograph: null
      };
      if (!!this.close_match_set_state) {
        payload.accepted_memberships = this.close_match_set_state.memberships
          .filter(x => x.accepted)
          .map(x => x.id);
        payload.eliminated_photographs = this.eliminated_photographs;
        if (!!this.close_match_set_state.representative_photograph) {
          payload.representative_photograph = this.close_match_set_state.representative_photograph.id;
        }
      }
      return payload;
    }
  },
  methods: {
    from_now(dt) {
      return moment(dt).fromNow();
    },
    photo_search(id) {
      this.$emit("photo_search", id);
    },
    get_index(id) {
      return _.findIndex(this.close_match_set_state.memberships, { id: id });
    },
    accept(id) {
      const set_index = this.get_index(id);
      this.close_match_set_state.memberships[set_index].accepted = true;
    },
    reject(id) {
      const set_index = this.get_index(id);
      this.close_match_set_state.memberships[set_index].accepted = false;
    },
    eliminate(photograph_id) {
      this.eliminated_photographs.push(photograph_id);
    },
    uneliminate(photograph_id) {
      _.pull(this.eliminated_photographs, photograph_id);
    },
    claim_primary(photograph) {
      this.close_match_set_state.representative_photograph = photograph;
    },
    cancel_primary(photograph) {
      if (!!this.close_match_set_state.representative_photograph) {
        if (
          photograph.id ==
          this.close_match_set_state.representative_photograph.id
        ) {
          this.close_match_set_state.representative_photograph = null;
        }
      }
    },
    accept_all() {
      this.close_match_set_state.memberships.map(x => (x.accepted = true));
      this.eliminated_photographs = [];
      this.close_match_set_state.representative_photograph = this.close_match_set_state.memberships[0].photograph;
    },
    reject_all() {
      this.close_match_set_state.representative_photograph = null;
      this.eliminated_photographs = [];
      this.close_match_set_state.memberships.map(x => (x.accepted = false));
    },
    eliminate_all() {
      this.eliminated_photographs = this.close_match_set_state.memberships.map(
        x => {
          return x.photograph.id;
        }
      );
      this.close_match_set_state.representative_photograph = null;
    },
    reject_remaining() {
      this.close_match_set_state.memberships
        .filter(x => x.accepted == null)
        .map(x => (x.accepted = false));
    },
    get_registration_toast(res) {
      return `${res.invalidations}`;
    },
    register_set() {
      this.uploading = true;
      this.reject_remaining();
      return HTTP.patch(
        "/close_match/set/" + this.close_match_set.id + "/approve/",
        this.close_match_approval
      ).then(
        results => {
          this.uploading = false;
          this.toast_variant = "success";
          this.toast_response = results.data.invalidations;
          this.$bvToast.show(`toast-${this.close_match_set.id}`);
          this.$emit("set_submitted", {
            id: this.close_match_set.id,
            object: results.data
          });
        },
        error => {
          this.uploading = false;
          this.toast_response = error;
          this.toast_variant = "danger";
          this.$bvToast.show(`toast-${this.close_match_set.id}`);
        }
      );
    }
  },
  mounted() {
    this.close_match_set_state = this.close_match_set;
  }
};
</script>

<style>
.info-badges {
  font-size: x-large;
}
</style>