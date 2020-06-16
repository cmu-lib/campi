<template>
  <b-overlay :show="loading">
    <CloseMatchSet
      v-if="!!close_match_set"
      :key="close_match_set.id"
      :id="`close_match_set-${close_match_set.id}`"
      :close_match_set="close_match_set"
      :collapsed="false"
      :show_invalid="true"
      @set_submitted="set_submitted"
      @photo_search="photo_search"
    />
  </b-overlay>
</template>

<script>
import { HTTP } from "@/main";
import CloseMatchSet from "@/components/close_match/CloseMatchSet.vue";
export default {
  name: "CloseMatchRunDetail",
  components: {
    CloseMatchSet
  },
  props: {
    close_match_run_id: {
      type: Number,
      required: true
    },
    close_match_set_id: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      close_match_set: null
    };
  },
  methods: {
    photo_search(id) {
      this.$emit("photo_search", id);
    },
    get_close_match_set() {
      return HTTP.get(`/close_match/set/${this.close_match_set_id}/`).then(
        results => {
          this.close_match_set = results.data;
        },
        error => {
          console.log(error);
        }
      );
    },
    set_submitted() {
      this.$emit("set_submitted");
      return HTTP.get("/close_match/set/", {
        params: {
          limit: 1,
          invalid: false,
          not_signed_off: true,
          ordering: "-n_images",
          close_match_run: this.close_match_run_id
        }
      }).then(
        results => {
          this.close_match_set = results.data.results[0];
          this.$router.push({
            name: "CloseMatchRunDetail",
            params: {
              id: this.close_match_run_id,
              set_id: this.close_match_set.id
            }
          });
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  mounted() {
    if (!!this.close_match_set) {
      if (this.close_match_set.id != this.$route.params.set_id) {
        this.get_close_match_set();
      }
    } else {
      this.get_close_match_set();
    }
  },
  updated() {
    if (!!this.close_match_set) {
      if (this.close_match_set.id != this.$route.params.set_id) {
        this.get_close_match_set();
      }
    } else {
      this.get_close_match_set();
    }
  }
};
</script>