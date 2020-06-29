<template>
  <b-card class="my-2">
    <b-button class="mx-1" v-if="!!tag" pill variant="warning" size="sm">
      <BIconTag />
      <span class="mx-2">{{ tag.label }}</span>
      <BIconXCircle @click="$emit('clear_tag')" />
    </b-button>
    <b-button class="mx-1" v-if="!!directory" pill variant="primary" size="sm">
      <BIconFolderFill />
      <span class="mx-2">{{ directory.label }}</span>
      <BIconXCircle @click="$emit('clear_directory')" />
    </b-button>
    <b-button class="mx-1" v-if="!!job" pill variant="info" size="sm">
      <BIconCamera />
      <span class="mx-2">{{ job.label }}</span>
      <BIconXCircle @click="$emit('clear_job')" />
    </b-button>
    <b-button class="mx-1" v-if="!!job_tag" pill variant="info" size="sm">
      <BIconTag />
      <span class="mx-2">{{ job_tag.label }}</span>
      <BIconXCircle @click="$emit('clear_job_tag')" />
    </b-button>
    <b-button class="mx-1" v-if="show_range" pill variant="secondary" size="sm">
      <BIconCalendarFill />
      <span class="mx-2">Digitized: {{ digitized_date_range[0] }}-{{ digitized_date_range[1] }}</span>
      <BIconXCircle @click="$emit('clear_date_range')" />
    </b-button>
  </b-card>
</template>

<script>
import {
  BIconXCircle,
  BIconFolderFill,
  BIconCalendarFill,
  BIconCamera,
  BIconTag
} from "bootstrap-vue";

export default {
  name: "FacetPills",
  components: {
    BIconXCircle,
    BIconFolderFill,
    BIconCalendarFill,
    BIconCamera,
    BIconTag
  },
  props: {
    directory: Object,
    job: Object,
    job_tag: Object,
    tag: Object,
    digitized_date_range: Array
  },
  computed: {
    show_range() {
      return !(
        this.digitized_date_range[0] == 2016 &&
        this.digitized_date_range[1] == 2020
      );
    }
  }
};
</script>
