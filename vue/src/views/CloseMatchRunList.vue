<template>
  <b-row>
    <b-col cols="2">
      <b-overlay :show="loading">
        <b-navbar v-b-scrollspy:scrollspy-cms class="flex-column" v-if="close_match_sets">
          <b-navbar-brand href="#">Match Groups</b-navbar-brand>
          <b-nav pills vertical>
            <b-nav-item
              v-for="cms in close_match_sets"
              :key="cms.id"
              :href="`#cms-${cms.id}`"
              :class="{completed: !!cms.user_last_modified}"
            >
              <BIconCheck2 v-if="!!cms.user_last_modified" variant="success" />
              <BIconX v-else variant="warning" />
              Match set {{ cms.id }}
              <br />
              ({{ cms.memberships.length }} images)
            </b-nav-item>
          </b-nav>
        </b-navbar>
      </b-overlay>
    </b-col>
    <b-col cols="10">
      <b-row flex align-h="between" align-v="center" class="mx-2">
        <b-col cols="3">
          <b-form-checkbox
            v-model="not_signed_off"
            name="check-button"
            switch
            v-b-tooltip.hover
            title="Only show sets that have not yet been reviewed by an editor."
          >Only show unreviewed sets</b-form-checkbox>
          <b-form-checkbox
            v-model="show_valid"
            name="check-button"
            switch
            v-b-tooltip.hover
            title="Only show sets valid sets whose members haven't already been committed to another match set."
          >See only valid sets</b-form-checkbox>
        </b-col>
        <b-form-group
          id="contain-photo"
          label-for="contain-photo-input"
          label="Match set contains photo:"
        >
          <b-input-group>
            <b-form-input
              id="contain-photo-input"
              type="number"
              v-model="photo_memberships"
              debounce="750"
            />
            <b-input-group-append v-if="!!photo_memberships">
              <b-button variant="danger" @click="photo_memberships=null">
                <BIconX />
              </b-button>
            </b-input-group-append>
          </b-input-group>
        </b-form-group>
        <b-pagination
          v-if="close_match_sets"
          v-model="current_page"
          :total-rows="close_match_set_count"
          :per-page="per_page"
        />
        <span v-if="!!close_match_sets">{{ close_match_set_count }} {{ set_count_type }} sets</span>
      </b-row>
      <b-overlay :show="loading">
        <div v-if="close_match_sets" id="scrollspy-cms" class="set-review-window">
          <CloseMatchSet
            v-for="cms in close_match_sets"
            :id="`cms-${cms.id}`"
            :key="cms.id"
            :close_match_set="cms"
            :collapsed="true"
            :searched_photo="photo_memberships"
            :show_invalid="!show_valid"
            @set_submitted="set_submitted"
            @photo_search="photo_search"
          />
        </div>
      </b-overlay>
    </b-col>
  </b-row>
</template>

<script>
import { HTTP } from "@/main";
import CloseMatchSet from "@/components/close_match/CloseMatchSet.vue";
import { BIconCheck2, BIconX } from "bootstrap-vue";
export default {
  name: "CloseMatchRunList",
  components: { CloseMatchSet, BIconCheck2, BIconX },
  props: {
    close_match_run_id: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      loading: null,
      current_page: 1,
      not_signed_off: false,
      show_valid: false,
      close_match_sets: null,
      close_match_set_count: 0,
      photo_memberships: null
    };
  },
  computed: {
    per_page() {
      return 10;
    },
    set_count_type() {
      if (this.not_signed_off) {
        return "unapproved";
      } else {
        return "total";
      }
    },
    rest_page() {
      return (this.current_page - 1) * this.per_page;
    },
    query_payload() {
      var payload = {
        ordering: "-n_images",
        close_match_run: this.close_match_run_id,
        limit: this.per_page,
        offset: this.rest_page,
        not_signed_off: this.not_signed_off,
        memberships: this.photo_memberships
      };
      if (this.show_valid) {
        payload["invalid"] = false;
      }
      return payload;
    }
  },
  methods: {
    get_close_match_sets() {
      if (!!this.close_match_run_id) {
        this.loading = true;
        return HTTP.get("/close_match/set/", {
          params: this.query_payload
        }).then(
          results => {
            this.loading = false;
            this.close_match_sets = results.data.results;
            this.close_match_set_count = results.data.count;
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    },
    set_submitted() {
      this.loading = true;
      this.close_match_sets = [];
      this.get_close_match_sets();
    },
    photo_search(id) {
      this.photo_memberships = id;
    }
  },
  watch: {
    query_payload() {
      this.get_close_match_sets();
    },
    not_signed_off() {
      this.current_page = 1;
    }
  },
  mounted() {
    this.get_close_match_sets();
  }
};
</script>

<style>
.set-review-window {
  position: relative;
  height: 70vh;
  overflow-y: auto;
}
</style>