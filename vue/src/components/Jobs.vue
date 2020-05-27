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
        :directory="job"
        class="d-flex justify-content-between align-items-center my-0 py-1 mr-0 pr-0"
      >
        <span class="text-truncate" @click="select_job(job)">{{ job_display(job) }}</span>
        <b-badge variant="info" class="ml-auto mr-1">{{ job.n_images }}</b-badge>
      </b-list-group-item>
      <b-list-group-item
        v-if="additional_jobs"
        class="my-0 py-1 mr-0 pr-0"
        @click="see_more_jobs"
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
    }
  },
  data() {
    return {
      jobs: [],
      offset: 0,
      job_label_search: "",
      additional_jobs: true
    };
  },
  methods: {
    job_display(job) {
      if (job.label != job.job_code) {
        return job.label + " (" + job.job_code + ")";
      } else {
        return job.job_code;
      }
    },
    see_more_jobs() {
      this.offset += this.page_size;
      this.get_jobs(this.offset);
    },
    get_jobs(offset) {
      var payload = {
        ordering: "label",
        limit: this.page_size,
        offset: offset
      };
      if (this.job_label_search != "") {
        payload["text"] = this.job_label_search;
      }
      if (!!this.digitized_date_after) {
        payload["digitized_date_after"] = `${this.digitized_date_after}-01-01`;
      }
      if (!!this.digitized_date_before) {
        payload[
          "digitized_date_before"
        ] = `${this.digitized_date_before}-01-01`;
      }
      return HTTP.get("/job/", {
        params: payload
      }).then(
        results => {
          if (!!results.data.next) {
            this.additional_jobs = true;
          } else {
            this.additional_jobs = false;
          }
          this.jobs = this.jobs.concat(results.data.results);
        },
        error => {
          console.log(error);
        }
      );
    },
    select_job(job) {
      this.$emit("input", job);
      window.scrollTo(0, 0);
    }
  },
  watch: {
    job_label_search() {
      if (this.job_label_search != "") {
        this.show_all = true;
      }
      this.jobs = [];
      this.page = 0;
      this.get_jobs();
    }
  },
  mounted() {
    this.get_jobs();
  }
};
</script>