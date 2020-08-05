<template>
  <b-card class="my-2" no-body>
    <template v-slot:header>
      <b-row align-h="between" align-v="center" class="mx-1">
        <span>
          Jobs
          <BIconQuestionCircle
            title="Titles or codes of official CMU photographer 'jobs' during which these photos were taken."
            v-b-tooltip:hover
            class="mx-1"
          />
        </span>
        <BIconCaretDownFill v-if="open" class="pointer" @click="open=!open" />
        <BIconCaretLeftFill v-else class="pointer" @click="open=!open" />
      </b-row>
    </template>
    <b-collapse v-model="open">
      <b-input-group class="p-2">
        <b-input v-model="job_label_search" debounce="500" placeholder="Search job names..." />
        <b-input-group-append v-if="job_label_search != ''">
          <b-button variant="warning" size="sm" @click="job_label_search=''">
            <BIconXSquare />
          </b-button>
        </b-input-group-append>
      </b-input-group>
      <b-list-group v-if="!!jobs" flush>
        <b-list-group-item
          v-for="job in jobs"
          :key="job.id"
          class="d-flex justify-content-between align-items-center my-0 py-1 mr-0 pr-0"
        >
          <span class="text-truncate pointer" @click="select_job(job)">{{ job_display(job) }}</span>
          <b-badge variant="info" class="ml-auto mr-1">{{ job.n_images }}</b-badge>
        </b-list-group-item>
        <b-list-group-item
          v-if="additional_jobs"
          class="my-0 py-1 mr-0 pr-0 pointer"
          @click="show_more"
          variant="secondary"
        >Show more...</b-list-group-item>
      </b-list-group>
    </b-collapse>
  </b-card>
</template>

<script>
import { HTTP } from "@/main";
// import _ from "lodash";
import {
  BIconXSquare,
  BIconCaretDownFill,
  BIconCaretLeftFill,
  BIconQuestionCircle,
} from "bootstrap-vue";
export default {
  name: "Jobs",
  components: {
    BIconXSquare,
    BIconCaretDownFill,
    BIconCaretLeftFill,
    BIconQuestionCircle,
  },
  props: {
    digitized_date_before: {
      type: Number,
      default: null,
    },
    digitized_date_after: {
      type: Number,
      default: null,
    },
    page_size: {
      type: Number,
      default: 10,
    },
    directory: {
      type: Object,
      default: null,
    },
    tag: {
      type: Object,
      default: null,
    },
    gcv_object: {
      type: Object,
      default: null,
    },
    gcv_label: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      show_total: 10,
      job_label_search: "",
      additional_jobs: true,
      open: false,
    };
  },
  computed: {
    query_payload() {
      var payload = {
        ordering: "-n_images,label",
        limit: this.show_total,
      };
      if (this.job_label_search != "") {
        payload["text"] = this.job_label_search;
      }
      if (!!this.gcv_object) {
        payload["gcv_object"] = this.gcv_object.id;
      }
      if (!!this.gcv_label) {
        payload["gcv_label"] = this.gcv_label.id;
      }
      if (!!this.directory) {
        payload["directory"] = this.directory.id;
      }
      if (!!this.tag) {
        payload["tag"] = this.tag.id;
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
    },
  },
  asyncComputed: {
    jobs() {
      return HTTP.get("/job/", {
        params: this.query_payload,
      }).then(
        (results) => {
          if (!!results.data.next) {
            this.additional_jobs = true;
          } else {
            this.additional_jobs = false;
          }
          return results.data.results;
        },
        (error) => {
          console.log(error);
        }
      );
    },
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
    },
  },
};
</script>