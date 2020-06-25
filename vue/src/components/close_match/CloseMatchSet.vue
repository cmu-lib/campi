<template>
  <b-card
    :border-variant="set_variant"
    :header-border-variant="set_variant"
    class="my-2"
    :no-body="collapsed_state"
  >
    <b-sidebar
      :id="`sidebar-${close_match_set.id}`"
      v-model="show_sidebar"
      v-if="show_sidebar"
      width="600px"
      right
    >
      <b-container>
        <h3>{{ sidebar_title }}</h3>
        <p>Click on a photograph to add it to the close match set.</p>
        <PhotoGrid
          v-if="sidebar_payload.class=='job'"
          :highlight_ids="all_photo_ids"
          :job="sidebar_payload.object"
          @photo_click="add_membership"
        />
        <PhotoGrid
          v-if="sidebar_payload.class=='directory'"
          :highlight_ids="all_photo_ids"
          :directory="sidebar_payload.object"
          @photo_click="add_membership"
        />
      </b-container>
    </b-sidebar>
    <template v-slot:header>
      <b-row class="px-2" v-if="!!close_match_set_state">
        <b-col cols="3">
          <span @click="collapsed_state=!collapsed_state">
            <BIconCaretRightFill v-if="collapsed_state" />
            <BIconCaretDownFill v-else />
          </span>
          <span>Match set {{ close_match_set.id }} ({{ close_match_set.n_unreviewed_images }} unreviewed images / {{ close_match_set.n_images }} total)</span>
          <span
            v-if="modifying_user"
          >Reveiwed by {{ close_match_set_state.user_last_modified.username }} {{ from_now(close_match_set_state.last_updated) }}</span>
        </b-col>
        <b-col cols="3">
          <b-form-checkbox
            v-model="show_other"
            name="check-button"
            switch
            v-b-tooltip.hover
            title="Show photographs that have already been added to other sets."
          >Show photos already in other sets</b-form-checkbox>
          <b-form-checkbox
            v-model="show_excluded"
            name="check-button"
            switch
            v-b-tooltip.hover
            title="Show photographs that have been marked excluded by an editor."
          >Show photos already excluded from match consideration</b-form-checkbox>
        </b-col>
        <b-col cols="2">
          <b-form-group
            :id="`membership-ordering-label-${close_match_set.id}`"
            :label-for="`membership-ordering-${close_match_set.id}`"
            label="Photo order"
          >
            <b-form-select
              :id="`membership-ordering-${close_match_set.id}`"
              v-model="membership_ordering"
              :options="ordering_options"
            />
          </b-form-group>
        </b-col>
        <b-col class="ml-auto" cols="4">
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
                variant="warning"
                size="sm"
                @click="reject_all"
                v-b-tooltip.hover
                title="Mark every photo as rejected. Rejected photos may appear in later match sets"
              >
                <BIconXOctagon class="mr-1" />Reject all
              </b-button>
              <b-button
                variant="danger"
                size="sm"
                @click="exclude_all"
                v-b-tooltip.hover
                title="Mark every photo as excluded. Excluded photos will be removed from this and all other match sets."
              >
                <BIconExclamationOctagonFill class="mr-1" />Exclude All
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
          <b-row>
            <b-form-checkbox
              class="my-2"
              v-model="close_match_set_state.has_duplicates"
              name="has-duplicates-checkbox"
            >Does this set contain duplicates / copy-negatives?</b-form-checkbox>
          </b-row>
        </b-col>
      </b-row>
    </template>
    <b-row flex v-if="!!close_match_set_state & !collapsed_state">
      <CloseMatchSetMembership
        v-for="cmsm in close_match_set_state.memberships"
        :key="cmsm.id"
        :close_match_set_membership="cmsm"
        :close_match_run="close_match_set_state.close_match_run"
        :close_match_set="close_match_set_state"
        :primary="close_match_set_state.representative_photograph"
        :searched_photo="searched_photo"
        :show_sidebar="show_sidebar"
        class="m-2"
        @accept="accept"
        @reject="reject"
        @exclude="exclude"
        @claim_primary="claim_primary"
        @cancel_primary="cancel_primary"
        @photo_search="photo_search"
        @activate_sidebar="activate_sidebar"
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
import PhotoGrid from "@/components/browsing/PhotoGrid.vue";
import _ from "lodash";
import {
  BIconCheck2All,
  BIconXOctagon,
  BIconExclamationOctagonFill,
  BIconCloudUpload,
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
    BIconCaretRightFill,
    BIconCaretDownFill,
    PhotoGrid,
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
    show_other_initial: {
      type: Boolean,
      default: false
    },
    show_excluded_initial: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      show_sidebar: false,
      show_other: false,
      show_excluded: false,
      sidebar_payload: null,
      collapsed_state: true,
      close_match_set_state: null,
      toast_response: null,
      toast_variant: null,
      uploading: false,
      membership_ordering: "distance"
    };
  },
  computed: {
    all_photo_ids() {
      return this.close_match_set_state.memberships.map(m => m.photograph.id);
    },
    ordering_options() {
      return [
        { value: "distance", text: "Visual similarity" },
        {
          value: function(x) {
            return x.photograph.filename;
          },
          text: "Filename"
        },
        {
          value: function(x) {
            return x.photograph.directory.label;
          },
          text: "Directory name"
        },
        {
          value: function(x) {
            return x.photograph.job.label;
          },
          text: "Job name"
        }
      ];
    },
    sidebar_title() {
      return `${this.sidebar_payload.class}: ${this.sidebar_payload.object.label}`;
    },
    has_secondary_images() {
      return this.close_match_set.memberships.some(x => !x.core);
    },
    toast_id() {
      return `toast-${this.close_match_set.id}`;
    },
    set_variant() {
      if (this.close_match_set.redundant) {
        return "warning";
      } else if (!!this.modifying_user) {
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
    }
  },
  methods: {
    activate_sidebar(payload) {
      this.sidebar_payload = payload;
      this.show_sidebar = true;
    },
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
      this.close_match_set_state.memberships[set_index].state = "a";
    },
    reject(id) {
      const set_index = this.get_index(id);
      this.close_match_set_state.memberships[set_index].state = "r";
    },
    exclude(id) {
      const set_index = this.get_index(id);
      this.close_match_set_state.memberships[set_index].state = "e";
    },
    claim_primary(photograph) {
      this.close_match_set_state.representative_photograph = photograph;
    },
    cancel_primary() {
      this.close_match_set_state.representative_photograph = null;
    },
    accept_all() {
      this.close_match_set_state.memberships.map(x => {
        if (!["o"].includes(x.state)) {
          x.state = "a";
        }
      });
      this.close_match_set_state.representative_photograph = this.close_match_set_state.memberships.filter(
        x => x.state == "a"
      )[0].photograph;
    },
    reject_all() {
      this.close_match_set_state.representative_photograph = null;
      this.close_match_set_state.memberships.map(x => {
        if (!["o"].includes(x.state)) {
          x.state = "r";
        }
      });
    },
    exclude_all() {
      this.close_match_set_state.memberships.map(x => {
        if (!["o"].includes(x.state)) {
          x.state = "e";
        }
      });
      this.close_match_set_state.representative_photograph = null;
    },
    reject_remaining() {
      this.close_match_set_state.memberships
        .filter(x => x.state == "n")
        .map(x => (x.state = "r"));
    },
    get_registration_toast(res) {
      return `${res.invalidations}`;
    },
    get_close_match_approval() {
      var payload = {
        accepted_memberships: [],
        rejected_memberships: [],
        excluded_memberships: [],
        representative_photograph: null,
        has_duplicates: this.close_match_set_state.has_duplicates
      };
      if (!!this.close_match_set_state) {
        this.close_match_set_state.memberships.map(m => {
          if (m.state == "a") {
            payload.accepted_memberships.push(m.id);
          } else if (m.state == "r") {
            payload.rejected_memberships.push(m.id);
          } else if (m.state == "e") {
            payload.excluded_memberships.push(m.id);
          }
        });
        if (!!this.close_match_set_state.representative_photograph) {
          payload.representative_photograph = this.close_match_set_state.representative_photograph.id;
        } else if (payload.accepted_memberships.length > 1) {
          payload.representative_photograph =
            payload.accepted_memberships[0].photograph.id;
        }
      }
      return payload;
    },
    register_set() {
      this.uploading = true;
      this.reject_remaining();
      const payload = this.get_close_match_approval();
      if (payload.accepted_memberships.length < 2) {
        this.uploading = false;
        this.toast_response =
          "You must either accept 2 or more photos, or reject/exclude them all.";
        this.toast_variant = "warning";
        this.$bvToast.show(`toast-${this.close_match_set.id}`);
        return null;
      }
      return HTTP.patch(
        "/close_match/set/" + this.close_match_set.id + "/approve/",
        payload
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
    },
    add_membership(photograph) {
      return HTTP.post("/close_match/set_membership/", {
        close_match_set: this.close_match_set.id,
        photograph: photograph.id,
        core: true,
        distance: 0,
        state: "a"
      }).then(
        results => {
          this.toast_variant = "success";
          this.toast_response = "Photo added to set";
          this.$bvToast.show(`toast-${this.close_match_set.id}`);
          return HTTP.get(
            `/close_match/set_membership/${results.data.id}`
          ).then(
            response => {
              this.close_match_set_state.memberships.push(response.data);
            },
            error => {
              console.log(error);
            }
          );
        },
        error => {
          this.toast_response = error.data;
          this.toast_variant = "danger";
          this.$bvToast.show(`toast-${this.close_match_set.id}`);
        }
      );
    },
    update_state() {
      this.close_match_set_state = this.close_match_set;
      var excl = [];
      if (!this.show_excluded) excl.push("e");
      if (!this.show_other) excl.push("o");
      this.close_match_set_state.memberships = _.sortBy(
        this.close_match_set.memberships.filter(m => !excl.includes(m.state)),
        [this.membership_ordering, "id"]
      );
    }
  },
  created() {
    this.collapsed_state = this.collapsed;
  },
  mounted() {
    this.show_other = this.show_other_initial;
    this.show_excluded = this.show_excluded_initial;
    this.update_state();
  },
  watch: {
    show_other() {
      this.update_state();
    },
    show_excluded() {
      this.update_state();
    },
    membership_ordering() {
      this.update_state();
    }
  }
};
</script>

<style>
.info-badges {
  font-size: x-large;
}
</style>