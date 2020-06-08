<template>
  <div>
    <b-button-toolbar>
      <b-form-checkbox v-model="not_signed_off" name="check-button" switch>Only show to-dos</b-form-checkbox>
      <b-pagination
        v-if="close_match_sets"
        v-model="current_page"
        :total-rows="close_match_sets.count"
        :per-page="per_page"
        class="mx-auto"
      />
    </b-button-toolbar>
    <b-row align-h="center">
      <b-overlay :show="loading">
        <div v-if="close_match_sets">
          <CloseMatchSet
            v-for="cms in close_match_sets.results"
            :key="cms.id"
            :close_match_set="cms"
          />
        </div>
      </b-overlay>
    </b-row>
  </div>
</template>

<script>
import { HTTP } from "@/main";
import CloseMatchSet from "@/components/close_match/CloseMatchSet.vue";
export default {
  name: "CloseMatchRun",
  components: { CloseMatchSet },
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
      per_page: 10
    };
  },
  computed: {
    rest_page() {
      return (this.current_page - 1) * this.per_page;
    }
  },
  asyncComputed: {
    close_match_sets() {
      if (!!this.close_match_run_id) {
        this.loading = true;
        return HTTP.get("/close_match/set/", {
          params: {
            ordering: "seed_photograph",
            close_match_run: this.close_match_run_id,
            limit: this.per_page,
            offset: this.rest_page,
            not_signed_off: this.not_signed_off
          }
        }).then(
          results => {
            this.loading = false;
            return results.data;
          },
          error => {
            console.log(error);
          }
        );
      } else {
        return null;
      }
    }
  }
};
</script>