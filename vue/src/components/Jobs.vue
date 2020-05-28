<template>
  <b-card class="my-2" header="Jobs">
    <b-input-group class="my-2">
      <b-input v-model="job_label_search" debounce="500" placeholder="Search job names..." />
      <b-input-group-append v-if="job_label_search != ''">
        <b-button variant="warning" size="sm" @click="job_label_search=''">
          <BIconXSquare />
        </b-button>
      </b-input-group-append>
    </b-input-group>
    <b-list-group v-if="!!jobs">
      <b-list-group-item
        v-for="job in jobs"
        :key="job.id"
        class="d-flex justify-content-between align-items-center my-0 py-1 mr-0 pr-0"
      >
        <span class="text-truncate" @click="select_job(job)">{{ job_display(job) }}</span>
        <b-badge variant="info" class="ml-auto mr-1">{{ job.n_images }}</b-badge>
      </b-list-group-item>
      <b-list-group-item
        v-if="additional_jobs"
        class="my-0 py-1 mr-0 pr-0"
        @click="show_more"
        variant="secondary"
      >Show more...</b-list-group-item>
    </b-list-group>
  </b-card>
</template>

<script>
import { HTTP } from "../main";
// import _ from "lodash";
import { BIconXSquare } from "bootstrap-vue";
export default {
  name: "Jobs",
  components: {
    BIconXSquare
  },
  props: {
    digitized_date_before: {
      type: Number,
      default: null
    },
    digitized_date_after: {
      type: Number,
      default: null
    },
    page_size: {
      type: Number,
      default: 10
    },
    job_tag: {
      type: Object,
      default: null
    },
    directory: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      show_total: 10,
      job_label_search: "",
      additional_jobs: true
    };
  },
  computed: {
    query_payload() {
      var payload = {
        ordering: "-n_images",
        limit: this.page_size
      };
      if (this.job_label_search != "") {
        payload["text"] = this.job_label_search;
      }
      if (!!this.job_tag) {
        payload["job_tag"] = this.job_tag.id;
      }
      if (!!this.directory) {
        payload["directory"] = this.directory.id;
      }
      if (!!this.digitized_date_after) {
        payload["digitized_date_after"] = `${this.digitized_date_after}-01-01`;
      }
      if (!!this.digitized_date_before) {
        payload[
          "digitized_date_before"
        ] = `${this.digitized_date_before}-01-01`;
      }
      return payload;
    }
  },
  asyncComputed: {
    jobs() {
      return HTTP.get("/job/", {
        params: this.query_payload
      }).then(
        results => {
          if (!!results.data.next) {
            this.additional_jobs = true;
          } else {
            this.additional_jobs = false;
          }
          return results.data.results;
        },
        error => {
          console.log(error);
        }
      );
    }
  },
  methods: {
    job_display(job) {
      if (job.label != job.job_code) {
        return job.label + " (" + job.job_code + ")";
      } else {
        return job.job_code;
      }
    },
    show_more() {
      this.show_total += this.page_size;
    },
    select_job(job) {
      this.$emit("input", job);
      window.scrollTo(0, 0);
    }
  }
};
</script>