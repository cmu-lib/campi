<template>
  <b-list-group>
    <b-list-group-item v-for="cmr in close_match_runs" :key="cmr.id">
      <CloseMatchRunBar :close_match_run="cmr" />
      <b-button-toolbar justify>
        <b-button
          class="mx-1"
          variant="primary"
          size="sm"
          @click="goto_next_set(cmr.id) "
          v-b-tooltip:hover
          title="Approve sets one at a time."
        >See next set</b-button>
        <b-button
          class="mx-1"
          variant="secondary"
          size="sm"
          :to="{name: 'CloseMatchRunList', params: { id: cmr.id }}"
          v-b-tooltip:hover
          title="Review sets that have already been approved/invalidated by an editor."
        >Review decisions</b-button>
        <b-button
          class="mx-1"
          variant="info"
          size="sm"
          :href="cmr.download_matches"
          v-b-tooltip:hover
          title="Download a CSV of close match sets with image filenames, set ids, and more metadata."
        >Download</b-button>
        <b-button
          class="mx-1"
          variant="danger"
          size="sm"
          @click="$bvModal.show(`delete-modal-${cmr.id}`)"
          v-b-tooltip:hover
          title="Delete the CMR and all its sets."
        >Delete</b-button>
        <b-modal
          :id="`delete-modal-${cmr.id}`"
          title="Delete run?"
          ok-variant="danger"
          @ok="delete_run(cmr.id)"
        >Delete run {{ cmr.id }}? This will erase all sets and editor decisions and cannot be undone.</b-modal>
      </b-button-toolbar>
    </b-list-group-item>
  </b-list-group>
</template>

<script>
import { HTTP } from "@/main";
import CloseMatchRunBar from "@/components/close_match/CloseMatchRunBar.vue";
export default {
  name: "CloseMatchRunMenu",
  components: {
    CloseMatchRunBar
  },
  data() {
    return {
      close_match_runs: []
    };
  },
  methods: {
    get_close_match_runs() {
      return HTTP.get("/close_match/run/").then(
        results => {
          this.close_match_runs = results.data.results;
        },
        error => {
          console.log(error);
        }
      );
    },
    goto_next_set(close_match_run_id) {
      return HTTP.get("/close_match/set/", {
        params: {
          limit: 1,
          user_signed_off: true,
          redundant: false,
          close_match_run: this.close_match_run_id,
          ordering: "-n_unreviewed_images"
        }
      }).then(
        results => {
          this.$router.push({
            name: "CloseMatchRunDetail",
            params: {
              id: close_match_run_id,
              set_id: results.data.results[0].id
            }
          });
        },
        error => {
          console.log(error);
        }
      );
    },
    delete_run(id) {
      return HTTP.delete(`/close_match/run/${id}/`).then(
        results => {
          this.$bvToast.toast(`Run ${id} deleted`, {
            title: `Deleted ${results.status}`,
            variant: "success"
          });
          this.get_close_match_runs();
        },
        error => {
          this.$bvToast.toast({
            message: error,
            options: { variant: "danger" }
          });
        }
      );
    }
  },
  mounted() {
    this.get_close_match_runs();
  }
};
</script>

<style>
p {
  font-size: small;
}
</style>