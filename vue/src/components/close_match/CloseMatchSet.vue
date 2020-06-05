<template>
  <b-card :border-variant="set_variant" :header-border-variant="set_variant" class="my-2">
    <template v-slot:header>
      <b-row class="px-2" flex align-h="between" align-v="center">
        <span>Match set {{ close_match_set.id }}</span>
        <b-button-toolbar>
          <b-button-group>
            <b-button variant="success" size="sm" @click="accept_all">
              <BIconCheck2All class="mr-1" />Accept all
            </b-button>
            <b-button variant="danger" size="sm" @click="reject_all">
              <BIconXOctagon class="mr-1" />Reject all
            </b-button>
          </b-button-group>
          <b-button class="ml-2" variant="primary" size="sm" @click="register_set">
            <BIconCloudUpload class="mr-1" />Save
          </b-button>
        </b-button-toolbar>
      </b-row>
    </template>
    <b-row flex align-v="center" v-if="!!close_match_set_state">
      <CloseMatchSetMembership
        v-for="cmsm in close_match_set_state.memberships"
        :key="cmsm.id"
        :close_match_set_membership="cmsm"
        :primary="close_match_set_state.representative_photograph"
        class="m-3"
        @accept="accept"
        @reject="reject"
        @claim_primary="claim_primary"
        @cancel_primary="cancel_primary"
      />
    </b-row>
    <template v-slot:footer v-if="!!modifying_user">
      <p>Approved by {{ close_match_set_state.user_last_modified.username }} on {{ close_match_set_state.last_updated }}</p>
    </template>
  </b-card>
</template>

<script>
import { HTTP } from "@/main";
import CloseMatchSetMembership from "@/components/close_match/CloseMatchSetMembership.vue";
import _ from "lodash";
import { BIconCheck2All, BIconXOctagon, BIconCloudUpload } from "bootstrap-vue";
export default {
  name: "CloseMatchSet",
  components: {
    CloseMatchSetMembership,
    BIconCheck2All,
    BIconXOctagon,
    BIconCloudUpload
  },
  props: {
    close_match_set: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      close_match_set_state: null
    };
  },
  computed: {
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
        representative_photograph: null
      };
      if (!!this.close_match_set_state) {
        payload.accepted_memberships = this.close_match_set_state.memberships
          .filter(x => x.accepted)
          .map(x => x.id);
        if (!!this.close_match_set_state.representative_photograph) {
          payload.representative_photograph = this.close_match_set_state.representative_photograph.id;
        }
      }
      return payload;
    }
  },
  methods: {
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
    claim_primary(photograph) {
      this.close_match_set_state.representative_photograph = photograph;
    },
    cancel_primary(photograph) {
      if (photograph == this.close_match_set_state.representative_photograph) {
        this.close_match_set_state.representative_photograph = null;
      }
    },
    accept_all() {
      this.close_match_set_state.memberships.map(x => (x.accepted = true));
    },
    reject_all() {
      this.close_match_set_state.representative_photograph = null;
      this.close_match_set_state.memberships.map(x => (x.accepted = false));
    },
    reject_remaining() {
      this.close_match_set_state.memberships
        .filter(x => x.accepted == null)
        .map(x => (x.accepted = false));
    },
    register_set() {
      this.reject_remaining();
      return HTTP.patch(
        "/close_match/set/" + this.close_match_set.id + "/approve/",
        this.close_match_approval
      ).then(
        results => {
          return results.data.results;
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  mounted() {
    this.close_match_set_state = this.close_match_set;
  }
};
</script>